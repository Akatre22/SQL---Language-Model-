import sys
import os

print(f"Python: {sys.version}")

packages = ["pypdf", "pypdf2", "pdfplumber", "fitz", "pdfminer", "torch", "transformers", "tiktoken", "sentencepiece"]
for pkg in packages:
    try:
        mod = __import__(pkg)
        print(f"  [x] {pkg} (version: {getattr(mod, '__version__', 'unknown')})")
    except ImportError:
        print(f"  [ ] {pkg} NOT installed")
