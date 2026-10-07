"""
Causal Multi-Head Self-Attention Module for NICE Tiny LLM
"""

import math
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import torch
import torch.nn as nn
import torch.nn.functional as F
from model.config import TinyLLMConfig

class CausalSelfAttention(nn.Module):
    def __init__(self, config: TinyLLMConfig):
        super().__init__()
        assert config.d_model % config.n_heads == 0, "d_model must be divisible by n_heads"
        
        self.d_model = config.d_model
        self.n_heads = config.n_heads
        self.head_dim = config.d_model // config.n_heads
        
        # Combined Q, K, V linear projection for efficiency
        self.c_attn = nn.Linear(config.d_model, 3 * config.d_model, bias=config.bias)
        # Output projection
        self.c_proj = nn.Linear(config.d_model, config.d_model, bias=config.bias)
        
        # Regularization
        self.attn_dropout = nn.Dropout(config.dropout)
        self.resid_dropout = nn.Dropout(config.dropout)

    def forward(self, x, mask=None):
        B, T, C = x.size() # Batch size, sequence length, embedding dim (d_model)
        
        # 1. Project to Q, K, V
        qkv = self.c_attn(x)
        q, k, v = qkv.chunk(3, dim=2)
        
        # 2. Reshape into (B, n_heads, T, head_dim)
        q = q.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        
        # 3. Fast Causal Scaled Dot-Product Attention
        # is_causal=True automatically handles the lower-triangular causal mask
        y = F.scaled_dot_product_attention(
            q, k, v,
            attn_mask=mask,
            dropout_p=self.attn_dropout.p if self.training else 0.0,
            is_causal=(mask is None)
        )
        
        # 4. Re-assemble head outputs: (B, T, C)
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        
        # 5. Output projection
        y = self.resid_dropout(self.c_proj(y))
        return y
