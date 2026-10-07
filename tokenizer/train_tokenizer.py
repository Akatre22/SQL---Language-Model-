"""
Train a custom Byte-Pair Encoding (BPE) Tokenizer for NICE Tiny LLM
Using Hugging Face `tokenizers` library.
Target Vocab Size: 4,096 tokens (optimized for ~250K-500K param models).
"""

from pathlib import Path
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import ByteLevel
from tokenizers.decoders import ByteLevel as ByteLevelDecoder

TOKENIZER_DIR = Path(__file__).resolve().parent
CORPUS_FILE = TOKENIZER_DIR.parent / "data" / "corpus.txt"
SAVE_PATH = TOKENIZER_DIR / "tokenizer.json"

SPECIAL_TOKENS = [
    "<|pad|>",
    "<|unk|>",
    "<|bos|>",
    "<|eos|>",
    "<|endoftext|>",
    "<schema>",
    "</schema>",
    "<question>",
    "</question>",
    "<sql>",
    "</sql>",
    "<dialect>",
    "</dialect>",
    "<clarify>",
    "</clarify>",
    "<error>",
    "</error>"
]

def train_custom_bpe(vocab_size=4096):
    print(f"[*] Training custom BPE tokenizer on {CORPUS_FILE}...")
    if not CORPUS_FILE.exists():
        raise FileNotFoundError(f"Corpus file not found: {CORPUS_FILE}. Run data/data_generator.py first.")

    # 1. Initialize Byte-Level BPE Tokenizer
    tokenizer = Tokenizer(BPE(unk_token="<|unk|>"))
    tokenizer.pre_tokenizer = ByteLevel(add_prefix_space=False)
    tokenizer.decoder = ByteLevelDecoder()

    # 2. Setup Trainer
    trainer = BpeTrainer(
        vocab_size=vocab_size,
        min_frequency=2,
        special_tokens=SPECIAL_TOKENS,
        initial_alphabet=ByteLevel.alphabet()
    )

    # 3. Train on Corpus
    tokenizer.train(files=[str(CORPUS_FILE)], trainer=trainer)

    # 4. Save
    tokenizer.save(str(SAVE_PATH))
    print(f"[+] Tokenizer saved successfully to {SAVE_PATH}")
    print(f"[+] Vocabulary size: {tokenizer.get_vocab_size()}")

    # 5. Quick Test
    test_text = "SELECT customer_id, SUM(amount) FROM sales WHERE region = 'EMEA' GROUP BY customer_id;"
    encoded = tokenizer.encode(test_text)
    decoded = tokenizer.decode(encoded.ids)
    print("\n--- Tokenizer Test ---")
    print(f"Original: {test_text}")
    print(f"Token IDs ({len(encoded.ids)} tokens): {encoded.ids[:15]}...")
    safe_tokens = [t.encode('ascii', 'replace').decode('ascii') for t in encoded.tokens[:15]]
    print(f"Tokens: {safe_tokens}...")
    print(f"Decoded: {decoded}")

if __name__ == "__main__":
    train_custom_bpe(vocab_size=4096)
