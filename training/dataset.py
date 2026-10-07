"""
PyTorch Dataset and DataLoader for NICE Tiny LLM
Reads instruction-response JSONL files and formats training sequences.
"""

import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import torch
from torch.utils.data import Dataset, DataLoader
from tokenizer.tokenizer_wrapper import TinyTokenizer

class InstructionDataset(Dataset):
    def __init__(self, file_path: str, tokenizer: TinyTokenizer, max_seq_len: int = 256):
        self.tokenizer = tokenizer
        self.max_seq_len = max_seq_len
        self.samples = []
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Dataset file not found: {file_path}")
            
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    self.samples.append(json.loads(line))
                    
    def __len__(self):
        return len(self.samples)
        
    def __getitem__(self, idx):
        item = self.samples[idx]
        
        # Support both new schema-conditioned schema and standard instruction schema
        if "schema" in item and "question" in item:
            prompt_text = f"<schema>\n{item['schema']}\n</schema>\n\n<question>\n{item['question']}\n</question>\n\n<sql>\n"
            response_text = f"{item.get('sql', item.get('response', ''))}\n</sql>\n<|endoftext|>"
        else:
            instruction = item.get("instruction", item.get("question", ""))
            response = item.get("response", item.get("output", ""))
            prompt_text = f"### Question:\n{instruction}\n\n### Answer:\n"
            response_text = f"{response}\n<|endoftext|>"
            
        full_text = prompt_text + response_text
        
        # Tokenize prompt and full text
        prompt_tokens = self.tokenizer.encode(prompt_text)
        tokens = self.tokenizer.encode(full_text)
        prompt_len = len(prompt_tokens)
        
        # Truncate or Pad
        if len(tokens) > self.max_seq_len:
            tokens = tokens[:self.max_seq_len]
        else:
            tokens = tokens + [self.tokenizer.pad_token_id] * (self.max_seq_len - len(tokens))
            
        tensor_tokens = torch.tensor(tokens, dtype=torch.long)
        
        # x is input sequence, y is target shifted by 1
        x = tensor_tokens[:-1]
        y = tensor_tokens[1:].clone()
        
        # 1. Mask prompt tokens in target (index 0 to prompt_len - 2) so loss is ONLY on SQL/response
        prompt_mask_limit = min(max(0, prompt_len - 1), len(y))
        if prompt_mask_limit > 0:
            y[:prompt_mask_limit] = -100
            
        # 2. Mask padding tokens in target (-100 is ignored by PyTorch CrossEntropyLoss)
        y[y == self.tokenizer.pad_token_id] = -100
        
        return x, y

def get_dataloaders(train_file: str, val_file: str, tokenizer: TinyTokenizer, batch_size: int = 16, max_seq_len: int = 256):
    train_ds = InstructionDataset(train_file, tokenizer, max_seq_len)
    val_ds = InstructionDataset(val_file, tokenizer, max_seq_len)
    
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, drop_last=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)
    
    return train_loader, val_loader

if __name__ == "__main__":
    tokenizer = TinyTokenizer()
    train_file = Path(__file__).resolve().parent.parent / "data" / "train.jsonl"
    val_file = Path(__file__).resolve().parent.parent / "data" / "val.jsonl"
    train_loader, val_loader = get_dataloaders(str(train_file), str(val_file), tokenizer, batch_size=4, max_seq_len=256)
    
    for x, y in train_loader:
        print("[*] Batch X shape:", x.shape)
        print("[*] Batch Y shape:", y.shape)
        print("[*] First sample token count:", (x[0] != tokenizer.pad_token_id).sum().item())
        break
