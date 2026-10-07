"""
Tokenizer Wrapper for NICE Tiny LLM
Provides a standard, clean interface to encode, decode, and pad sequences.
"""

from pathlib import Path
from tokenizers import Tokenizer

DEFAULT_TOKENIZER_PATH = Path(__file__).resolve().parent / "tokenizer.json"

class TinyTokenizer:
    def __init__(self, tokenizer_path=None):
        path = tokenizer_path or DEFAULT_TOKENIZER_PATH
        if not Path(path).exists():
            raise FileNotFoundError(f"Tokenizer not found at {path}. Please train it first using train_tokenizer.py.")
        self.tokenizer = Tokenizer.from_file(str(path))
        
        self.pad_token = "<|pad|>"
        self.unk_token = "<|unk|>"
        self.bos_token = "<|bos|>"
        self.eos_token = "<|eos|>"
        self.eot_token = "<|endoftext|>"
        
        self.pad_token_id = self.tokenizer.token_to_id(self.pad_token)
        self.unk_token_id = self.tokenizer.token_to_id(self.unk_token)
        self.bos_token_id = self.tokenizer.token_to_id(self.bos_token)
        self.eos_token_id = self.tokenizer.token_to_id(self.eos_token)
        self.eot_token_id = self.tokenizer.token_to_id(self.eot_token)
        
        # Schema & SQL boundary special tokens
        self.special_tokens = [
            "<|pad|>", "<|unk|>", "<|bos|>", "<|eos|>", "<|endoftext|>",
            "<schema>", "</schema>", "<question>", "</question>",
            "<sql>", "</sql>", "<dialect>", "</dialect>",
            "<clarify>", "</clarify>", "<error>", "</error>"
        ]
        self.special_token_ids = {
            tok: self.tokenizer.token_to_id(tok)
            for tok in self.special_tokens
            if self.tokenizer.token_to_id(tok) is not None
        }
        
        self.vocab_size = self.tokenizer.get_vocab_size()

    def encode(self, text: str):
        return self.tokenizer.encode(text).ids

    def decode(self, token_ids: list, skip_special_tokens: bool = False):
        if skip_special_tokens:
            token_ids = [tid for tid in token_ids if tid not in {self.pad_token_id, self.bos_token_id, self.eos_token_id, self.eot_token_id}]
        return self.tokenizer.decode(token_ids)

    def __len__(self):
        return self.vocab_size
