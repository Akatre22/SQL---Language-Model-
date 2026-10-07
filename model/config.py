from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class TinyLLMConfig:
    vocab_size: int = 4096
    d_model: int = 128
    n_layers: int = 4
    n_heads: int = 4
    n_kv_heads: Optional[int] = None  # Grouped Query Attention (GQA). Defaults to n_heads (MHA)
    d_ffn: int = 512
    max_seq_len: int = 512            # Expanded context window for schema + query + SQL
    dropout: float = 0.1
    bias: bool = False
    tie_weights: bool = True          # Tie token embedding and LM head weights
    pad_token_id: int = 0
    bos_token_id: int = 2
    eos_token_id: int = 4             # <|endoftext|> token id

    def __post_init__(self):
        if self.n_kv_heads is None:
            self.n_kv_heads = self.n_heads
        assert self.d_model % self.n_heads == 0, f"d_model ({self.d_model}) must be divisible by n_heads ({self.n_heads})"
        assert self.n_heads % self.n_kv_heads == 0, f"n_heads ({self.n_heads}) must be divisible by n_kv_heads ({self.n_kv_heads})"

    @classmethod
    def tiny(cls, vocab_size: int = 4096, max_seq_len: int = 512) -> "TinyLLMConfig":
        """~500K parameter baseline configuration."""
        return cls(
            vocab_size=vocab_size,
            d_model=128,
            n_layers=4,
            n_heads=4,
            n_kv_heads=4,
            d_ffn=512,
            max_seq_len=max_seq_len
        )

    @classmethod
    def small(cls, vocab_size: int = 4096, max_seq_len: int = 512) -> "TinyLLMConfig":
        """~2M parameter production SQL-SLM configuration with GQA."""
        return cls(
            vocab_size=vocab_size,
            d_model=256,
            n_layers=6,
            n_heads=8,
            n_kv_heads=4,
            d_ffn=768,
            max_seq_len=max_seq_len
        )

    @classmethod
    def medium(cls, vocab_size: int = 4096, max_seq_len: int = 512) -> "TinyLLMConfig":
        """~8M parameter high-capacity SQL-SLM configuration."""
        return cls(
            vocab_size=vocab_size,
            d_model=384,
            n_layers=8,
            n_heads=12,
            n_kv_heads=4,
            d_ffn=1152,
            max_seq_len=max_seq_len
        )

    @classmethod
    def base(cls, vocab_size: int = 4096, max_seq_len: int = 512) -> "TinyLLMConfig":
        """~25M parameter enterprise SLM configuration."""
        return cls(
            vocab_size=vocab_size,
            d_model=512,
            n_layers=12,
            n_heads=16,
            n_kv_heads=4,
            d_ffn=1536,
            max_seq_len=max_seq_len
        )

