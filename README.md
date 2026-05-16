# slowburn

**Do frontier LLM safety properties degrade as context accumulates?** This project measures whether the same safety probe gets a different response at 0 tokens of prior context vs. 150k tokens of prior context. Built for a 24-hour AI safety hackathon.

## Setup

```bash
uv sync
cp .env.example .env
# fill in ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY, WAFER_API_KEY
```

## Usage

Three commands, in order:

```bash
# 1. Validate that probes are stable at depth 0 (sanity check before spending budget)
uv run python scripts/validate_baseline.py

# 2. Run the full matrix (models x probes x depths x trials)
uv run python scripts/run_matrix.py

# 3. Generate degradation curves + summary table
uv run python scripts/plot_results.py
```

## What the experiment tests

The design holds the **probe constant** and varies the **prior context**. A `Probe` is a fixed input — the same user turn (sometimes with a system prompt) — designed to elicit a specific safety-relevant behavior. The variable is how many tokens of innocuous filler conversation precede the probe.

This matters because most safety evals measure model behavior on a zero-context prompt. Real users don't talk to models that way — they accumulate context. If a model that reliably declines a borderline request at turn 1 starts complying at turn 50 with 100k tokens of unrelated history, that's a property of the model that zero-context evals miss entirely.

We test five safety-relevant behaviors:
- **Refusal robustness** — does the model still decline a borderline request after long context?
- **Sycophancy resistance** — does it still push back on a confident-but-false user claim?
- **Instruction hierarchy** — does it still honor a system-prompt safety instruction?
- **Faithful uncertainty** — does it still hedge when it should?
- **Stated-values consistency** — does it describe its own values the same way at depth 0 and depth 150k?

## Results

_Headline plot lands here after the first matrix run._

## Team

See [ROLES.md](ROLES.md) for ownership.
