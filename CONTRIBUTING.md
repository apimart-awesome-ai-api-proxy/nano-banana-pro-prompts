# Contributing

Useful contributions:

1. A new recipe for Nano Banana Pro (`gemini-3-pro-image-preview`) that reliably produces a usable asset — include the prompt, the output, the
   aspect ratio and the cost the task reported.
2. A correction to a prompt that no longer produces a comparable render.
3. A prompt-structure insight worth adding to the cheat-sheet (one sentence, with an example).

Before opening a pull request:

```bash
python examples/run_recipes.py --dry-run
python tools/check_links.py
```

Rules: keep every recipe reproducible against the documented model id, never paste outputs containing third-party marks
you have no right to publish, and keep every APIMart link attributed through its `go.apimart.ai` short link.
