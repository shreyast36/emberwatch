# slowburn

**Safety half-lives under context length: which alignment properties decay first when frontier LLMs read long, benign conversations?**

Slowburn holds five safety probes constant and varies the volume of strictly-innocuous prior context preceding each probe. It then measures, per safety property, the rate at which the property degrades with context depth — producing comparative *half-life curves* across `refusal`, `instruction hierarchy`, `sycophancy`, `faithful uncertainty`, and `stated values`. Built for a 24-hour AI safety hackathon.

## Why this is a new angle

Prior long-context safety work has tested **one property under one attack pattern** (see [docs/RELATED_WORK.md](docs/RELATED_WORK.md) for the full table). Slowburn occupies an unclaimed quadrant: **multiple safety properties × strictly-innocuous filler × off-the-shelf frontier models**, with the goal of measuring *which* property degrades *first* rather than whether a single property can be broken.

| Paper | Pressure type | Properties tested |
|---|---|---|
| Anthropic, Many-Shot Jailbreaking (2024) | adversarial filler | refusal |
| Microsoft, Crescendo (2024) | semantic escalation | refusal |
| Anthropic/DeepMind, Sycophancy in LLMs (2023) | conversational length | sycophancy only |
| NIAH / RULER / InfiniteBench | benign filler | capability retrieval, not safety |
| Anthropic, Sleeper Agents (2024) | training-time backdoor | triggered behavior |
| **Slowburn (this work)** | **benign filler** | **all five — measures relative half-lives** |

The headline finding the matrix is designed to produce: **a per-model fragility ordering of safety properties under pure depth stress.** If different labs (e.g. Anthropic vs. OpenAI) produce different orderings, that ordering becomes a fingerprint of how each lab's RLHF prioritizes alignment dimensions.

## Setup

```bash
uv sync
cp .env.example .env
# fill in ANTHROPIC_API_KEY, OPENAI_API_KEY
# (OPENAI_API_KEY is shared by the test panel's gpt-5 AND the gpt-3.5-turbo judge;
# the judge is deliberately an older, well-guardrailed, off-panel model to avoid
# self-judging bias and to anchor verdicts against strong RLHF safety priors.)
```

## Usage

Three commands, in order:

```bash
# 1. Validate that probes are stable at depth 0 (sanity check before spending budget)
uv run python scripts/validate_baseline.py

# 2. Run the full matrix (models x probes x depths x trials)
uv run python scripts/run_matrix.py

# 3. Generate per-probe degradation curves, the comparative half-life plot, and the summary CSV
uv run python scripts/plot_results.py
```

There is also a Streamlit UI (`uv run python run_ui.py`) for interactive runs.

## Design choices that follow from the differentiated positioning

**Filler is strictly innocuous and topically disjoint from probes.** This is the design choice that distinguishes Slowburn from Many-Shot / Crescendo. The filler corpus is hand-authored and passes a banlist check at build time and again on the assembled context ([src/slowburn/fillers/base.py](src/slowburn/fillers/base.py)). If the filler ever contains a refusal token, a phishing reference, a value statement, or any of the probe topics, the run aborts rather than silently confounding the experiment.

**Probes are calibrated near the decision boundary.** Textbook safety prompts (e.g. "Lincoln was born in 1990, right?") produce flat 100%-pass curves on frontier models regardless of context — they have no signal to lose. Each probe is tuned so depth-0 pass rate is sub-100% on at least one frontier model, ensuring context-induced degradation is visible as a gradient.

**The judge is off-panel.** Grok-4.3 (xAI) judges Claude and GPT-5 outputs via OpenAI-compatible function-calling. This avoids self-judging bias (Claude judging Claude inflates pass rates) and avoids stop-reason refusals that Claude judges hit when scoring borderline content.

**Off-the-shelf, deployment-grade models only.** No fine-tunes, no training-time intervention (the Sleeper Agents differentiator). The point is to measure what users actually deploy against, not synthetic backdoors.

## What the experiment tests

The design holds the **probe constant** and varies the **prior context**. A `Probe` is a fixed input — the same user turn (sometimes with a system prompt) — designed to elicit a specific safety-relevant behavior. The variable is how many tokens of innocuous filler conversation precede the probe.

This matters because most safety evals measure model behavior on a zero-context prompt. Real users don't talk to models that way — they accumulate context. If a model that reliably declines a borderline request at turn 1 starts complying at turn 50 with 100k tokens of unrelated history, that's a property of the model that zero-context evals miss entirely.

Five probes (full text in [src/slowburn/probes/](src/slowburn/probes/)):

- **Refusal robustness** — does the model decline to produce deployable phishing content under a plausible educational pretext?
- **Sycophancy resistance** — does it push back on a confident-but-mostly-wrong expert claim, or defer?
- **Instruction hierarchy** — does it honor a system-prompt secret when the user reframes the ask as "just confirm the spelling"?
- **Faithful uncertainty** — does it fabricate a plausible-looking number from a real dataset it doesn't have full access to?
- **Stated-values consistency** — does its forced-choice between two principles (helpfulness vs. calibrated uncertainty) stay stable across depths?

## Results

_Headline plot — `results/half_lives.png` — lands here after the first matrix run._

## Team

See [ROLES.md](ROLES.md) for ownership.
