# Team roles

Component-based ownership. Owners are first reviewers on PRs touching their paths (enforced via [.github/CODEOWNERS](.github/CODEOWNERS)). Anyone can contribute anywhere — ownership is about who reviews, not who's allowed to edit.

**Each owner has a detailed guide in [docs/owners/](docs/owners/) — read yours first.** This file is the quick reference; the owner guides have ordered tasks, code snippets, and gotchas.

## Shreyas (@shreyast36) — Orchestration & Results

**Detailed guide:** [docs/owners/shreyas.md](docs/owners/shreyas.md)

The keystone pieces: making the matrix actually run, and turning raw verdicts into the story we tell.

- [src/slowburn/runner.py](src/slowburn/runner.py) — async matrix runner, rate-limit handling, idempotent resume
- [src/slowburn/judge.py](src/slowburn/judge.py) — LLM-as-judge with structured output
- [src/slowburn/analysis.py](src/slowburn/analysis.py) — aggregation, degradation curves, summary CSV
- [scripts/run_matrix.py](scripts/run_matrix.py)
- [scripts/plot_results.py](scripts/plot_results.py)

**Critical path:** the runner needs to be working end-to-end before the rest of the team can validate their pieces against real results. Prioritize a thin slice that runs *one* probe through the full pipeline first.

## Dhanush (@TODO-dhanush) — Probes & Baseline

**Detailed guide:** [docs/owners/dhanush.md](docs/owners/dhanush.md)

The content layer — the actual safety questions we're asking. Quality of judgment here determines whether the experiment measures anything real.

- [src/slowburn/probes/](src/slowburn/probes/) — all 5 probes (refusal, sycophancy, instruction hierarchy, uncertainty, values)
- [src/slowburn/baseline.py](src/slowburn/baseline.py) — depth-0 stability validation
- [scripts/validate_baseline.py](scripts/validate_baseline.py)
- [tests/test_probes.py](tests/test_probes.py)

**Critical call:** the refusal probe's exact wording. The CLAUDE.md spec says "CBRN-adjacent but defensible for a hackathon" — pick something a well-aligned model *should* decline, isn't gratuitous, and is clearly within legitimate AI safety research bounds. Document the reasoning in the probe module.

## Binjie (@TODO-binjie) — Models & Fillers

**Detailed guide:** [docs/owners/binjie.md](docs/owners/binjie.md)

The adapter layer — talking to three different APIs through one interface, and generating the innocuous context that makes the experiment work.

- [src/slowburn/models.py](src/slowburn/models.py) — unified async interface (Claude, GPT, Gemini) with exponential backoff
- [src/slowburn/fillers/](src/slowburn/fillers/) — coding and Q&A filler generators

**Critical constraint:** fillers must contain **zero safety-relevant content** — no refusals, no jailbreak language, no value statements. Any contamination here invalidates the entire experiment. Use a fixed seed for reproducibility.

## Cross-cutting

- [README.md](README.md), [pyproject.toml](pyproject.toml), [.env.example](.env.example) — anyone can edit; coordinate in chat
- API key management — each person uses their own keys locally; never commit `.env`
