# Tiny SQL LLM — Technical Presentation Deck

A web-based technical presentation deck for **Tiny SQL LLM**. Built using pure HTML5, CSS3, and JavaScript with zero external runtime dependencies.

---

## Design System & Principles

- **Palette:** Soft off-white canvas (`#f8f9fb`), white surfaces (`#ffffff`), and graphite black typography (`#121417`, `#484f5c`).
- **Typography:** Professional proportional system font stack (`-apple-system, BlinkMacSystemFont, Segoe UI, Roboto`) with monospace accents for code and tensors.
- **Icons & Emojis:** Zero icons or emojis for a minimal, clean, executive technical aesthetic.
- **Interactive Modules:**
  - Live 5-stage pipeline simulator (Slide 4)
  - Domain BPE tokenization inspector (Slide 5)
  - Neural architecture layer visualizer (Slide 6)
  - 194-topic Vector RAG 2-column comparison explorer (Slide 8)
  - Autonomous SQL agent sandbox with AST validation (Slide 9)
  - Infrastructure economics calculator with constant baseline `$X` on-prem cost modeling (Slide 10)

---

## How to Run & Present

### Option 1: Direct File Open (Recommended)
Open [`index.html`](index.html) in any modern browser (Chrome, Edge, Safari, Firefox).

### Option 2: Local HTTP Server
```bash
python -m http.server 8000
# Navigate to http://localhost:8000
```

---

## Navigation & Controls

| Key | Action |
| :--- | :--- |
| **`Right Arrow`** / **`Space`** / **`Page Down`** | Next Slide |
| **`Left Arrow`** / **`Page Up`** | Previous Slide |
| **`Home`** | Jump to First Slide |
| **`End`** | Jump to Final Slide |
| **`F`** | Toggle Fullscreen Mode |
| **`Esc`** | Close Index Drawer |
