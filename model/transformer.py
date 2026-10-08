"""
Modernized Decoder-Only Transformer Architecture for Tiny SQL LLM.
Features:
- Rotary Position Embeddings (RoPE)
- SwiGLU Gated Feed-Forward Networks (as in Llama 3 / Mistral)
- RMSNorm (Root Mean Square Layer Normalization)
- Tied Weights (Input Embedding <-> LM Head)
"""

import math
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import torch
import torch.nn as nn
import torch.nn.functional as F
from model.config import TinyLLMConfig

class RMSNorm(nn.Module):
    def __init__(self, dim: int, eps: float = 1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def forward(self, x):
        norm = torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.eps)
        return x * norm * self.weight

def precompute_rope_freqs(head_dim: int, max_seq_len: int, theta: float = 10000.0) -> torch.Tensor:
    """Precomputes complex frequencies for Rotary Position Embeddings (RoPE)."""
    dim_range = torch.arange(0, head_dim, 2)[: (head_dim // 2)].float()
    freqs = 1.0 / (theta ** (dim_range / head_dim))
    t = torch.arange(max_seq_len, dtype=torch.float32)
    freqs = torch.outer(t, freqs) # (max_seq_len, head_dim // 2)
    freqs_cis = torch.polar(torch.ones_like(freqs), freqs) # complex64
    return freqs_cis

def apply_rotary_emb(xq: torch.Tensor, xk: torch.Tensor, freqs_cis: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """Applies Rotary Position Embeddings (RoPE) to Queries and Keys with GQA support."""
    B, n_q_heads, T, head_dim = xq.shape
    _, n_kv_heads, _, _ = xk.shape
    
    xq_ = torch.view_as_complex(xq.float().reshape(B, n_q_heads, T, head_dim // 2, 2))
    xk_ = torch.view_as_complex(xk.float().reshape(B, n_kv_heads, T, head_dim // 2, 2))
    
    freqs_cis = freqs_cis[:T].view(1, 1, T, head_dim // 2)
    
    xq_out = torch.view_as_real(xq_ * freqs_cis).flatten(3)
    xk_out = torch.view_as_real(xk_ * freqs_cis).flatten(3)
    
    return xq_out.type_as(xq), xk_out.type_as(xk)

class RoPECausalAttention(nn.Module):
    def __init__(self, config: TinyLLMConfig):
        super().__init__()
        self.d_model = config.d_model
        self.n_heads = config.n_heads
        self.n_kv_heads = config.n_kv_heads if config.n_kv_heads is not None else config.n_heads
        self.n_rep = self.n_heads // self.n_kv_heads
        self.head_dim = config.d_model // config.n_heads
        
        self.q_proj = nn.Linear(config.d_model, self.n_heads * self.head_dim, bias=config.bias)
        self.k_proj = nn.Linear(config.d_model, self.n_kv_heads * self.head_dim, bias=config.bias)
        self.v_proj = nn.Linear(config.d_model, self.n_kv_heads * self.head_dim, bias=config.bias)
        self.out_proj = nn.Linear(config.d_model, config.d_model, bias=config.bias)
        
        self.dropout = nn.Dropout(config.dropout)
        
        # Precompute RoPE complex frequencies
        freqs = precompute_rope_freqs(self.head_dim, config.max_seq_len)
        self.register_buffer("freqs_cis", freqs, persistent=False)

    def forward(self, x, mask=None):
        B, T, C = x.shape
        
        q = self.q_proj(x).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(B, T, self.n_kv_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(B, T, self.n_kv_heads, self.head_dim).transpose(1, 2)
        
        # Apply RoPE to Q and K
        q, k = apply_rotary_emb(q, k, self.freqs_cis)

        # GQA: Repeat Key and Value heads if n_kv_heads < n_heads
        if self.n_rep > 1:
            k = torch.repeat_interleave(k, self.n_rep, dim=1)
            v = torch.repeat_interleave(v, self.n_rep, dim=1)
        
        # Scaled Dot-Product Attention with Causal Mask
        y = F.scaled_dot_product_attention(
            q, k, v,
            attn_mask=mask,
            dropout_p=self.dropout.p if self.training else 0.0,
            is_causal=(mask is None)
        )
        
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        return self.dropout(self.out_proj(y))

class SwiGLU(nn.Module):
    """SwiGLU Feed-Forward Network as used in modern LLMs (LLaMA / Mistral)."""
    def __init__(self, config: TinyLLMConfig):
        super().__init__()
        # Standard SwiGLU uses hidden dimension ~ 8/3 * d_model or config.d_ffn
        hidden_dim = config.d_ffn or int(8 * config.d_model / 3)
        self.w1 = nn.Linear(config.d_model, hidden_dim, bias=config.bias) # Gate
        self.w2 = nn.Linear(hidden_dim, config.d_model, bias=config.bias) # Down
        self.w3 = nn.Linear(config.d_model, hidden_dim, bias=config.bias) # Up
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, x):
        # SwiGLU(x) = (SiLU(w1(x)) * w3(x)) * w2
        return self.dropout(self.w2(F.silu(self.w1(x)) * self.w3(x)))

class ModernTransformerBlock(nn.Module):
    def __init__(self, config: TinyLLMConfig):
        super().__init__()
        self.attn_norm = RMSNorm(config.d_model)
        self.attn = RoPECausalAttention(config)
        self.ffn_norm = RMSNorm(config.d_model)
        self.ffn = SwiGLU(config)

    def forward(self, x, mask=None):
        x = x + self.attn(self.attn_norm(x), mask=mask)
        x = x + self.ffn(self.ffn_norm(x))
        return x

class TinyLLM(nn.Module):
    def __init__(self, config: TinyLLMConfig):
        super().__init__()
        self.config = config

        # Token Embedding (no positional embedding needed with RoPE)
        self.token_embedding = nn.Embedding(config.vocab_size, config.d_model)
        self.drop = nn.Dropout(config.dropout)

        # Transformer Blocks
        self.blocks = nn.ModuleList([ModernTransformerBlock(config) for _ in range(config.n_layers)])

        # Final RMSNorm & LM Head
        self.norm = RMSNorm(config.d_model)
        self.lm_head = nn.Linear(config.d_model, config.vocab_size, bias=False)
        if config.tie_weights:
            self.lm_head.weight = self.token_embedding.weight

        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def count_parameters(self):
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        return {"total": total_params, "trainable": trainable_params}

    def forward(self, idx, targets=None):
        B, T = idx.shape
        x = self.drop(self.token_embedding(idx))

        for block in self.blocks:
            x = block(x)

        x = self.norm(x)
        logits = self.lm_head(x)

        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1), ignore_index=-100)

        return logits, loss

    @torch.no_grad()
    def generate(
        self,
        idx: torch.Tensor,
        max_new_tokens: int = 150,
        temperature: float = 0.3,
        top_k: int = 40,
        top_p: float = 0.9,
        repetition_penalty: float = 1.25,
        no_repeat_ngram_size: int = 3,
        eos_token_id=None
    ) -> torch.Tensor:
        """Autoregressive text generation with greedy argmax, repetition penalty, and sampling controls."""
        self.eval()
        
        # Normalize eos_token_id into a list
        eos_list = []
        if eos_token_id is not None:
            if isinstance(eos_token_id, (list, tuple, set)):
                eos_list = list(eos_token_id)
            else:
                eos_list = [eos_token_id]

        for _ in range(max_new_tokens):
            idx_cond = idx if idx.size(1) <= self.config.max_seq_len else idx[:, -self.config.max_seq_len:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :].clone() # focus on last token

            # Repetition Penalty across previously generated tokens
            if repetition_penalty != 1.0 and idx.size(1) > 0:
                past_tokens = set(idx[0].tolist())
                for token_id in past_tokens:
                    if logits[0, token_id] > 0:
                        logits[0, token_id] /= repetition_penalty
                    else:
                        logits[0, token_id] *= repetition_penalty

            # No-repeat n-gram blocking
            if no_repeat_ngram_size > 0 and idx.size(1) >= no_repeat_ngram_size:
                seq = idx[0].tolist()
                ngram_prefix = tuple(seq[-(no_repeat_ngram_size - 1):])
                for i in range(len(seq) - no_repeat_ngram_size + 1):
                    if tuple(seq[i:i + no_repeat_ngram_size - 1]) == ngram_prefix:
                        banned_token = seq[i + no_repeat_ngram_size - 1]
                        logits[0, banned_token] = -float("inf")

            # Fast deterministic greedy decoding
            if temperature == 0.0 or temperature < 1e-6:
                idx_next = torch.argmax(logits, dim=-1, keepdim=True)
                idx = torch.cat((idx, idx_next), dim=1)
                
                # Check for 2-token and 3-token repetitive loop traps
                if idx.size(1) >= 6:
                    last6 = idx[0, -6:].tolist()
                    if last6[0] == last6[2] == last6[4] and last6[1] == last6[3] == last6[5]:
                        break
                    if last6[3] == last6[4] == last6[5]:
                        break

                if eos_list and idx_next.item() in eos_list:
                    break
                continue

            # Temperature Scaling
            logits = logits / max(temperature, 1e-4)

            # Top-K Truncation
            if top_k > 0:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = -float('Inf')

            # Top-P (Nucleus) Filtering
            if top_p < 1.0:
                sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                sorted_indices_to_remove = cumulative_probs > top_p
                sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                sorted_indices_to_remove[..., 0] = 0
                indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                logits[indices_to_remove] = -float('Inf')

            # Sample next token
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)

            # Check for repetition traps
            if idx.size(1) >= 6:
                last6 = idx[0, -6:].tolist()
                if last6[0] == last6[2] == last6[4] and last6[1] == last6[3] == last6[5]:
                    break
                if last6[3] == last6[4] == last6[5]:
                    break

            if eos_list and idx_next.item() in eos_list:
                break

        return idx

