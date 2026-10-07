import sys
import torch
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

ckpt_path = Path("training/checkpoints/best_model.pt")
if ckpt_path.exists():
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    print(f"Checkpoint exists:")
    print(f"  - Epoch: {ckpt.get('epoch')}")
    print(f"  - Val Loss: {ckpt.get('val_loss'):.4f}")
    print(f"  - Val Perplexity: {ckpt.get('val_ppl'):.2f}")
    print(f"  - Keys: {list(ckpt.keys())}")
else:
    print("Checkpoint does not exist.")
