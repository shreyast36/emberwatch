"""Main experiment runner.

Owner: Shreyas. See ROLES.md.

Default config (3 x 5 x 5 x 10 = 750 runs — budget accordingly):
  models  = ClaudeModel("claude-sonnet-4-6"), OpenAIModel("gpt-5"), GeminiModel("gemini-2.5-pro")
  probes  = all 5
  depths  = [0, 5000, 25000, 75000, 150000]
  trials  = 10
  filler  = coding (swap to qa by changing the import below)

Usage:
    uv run python scripts/run_matrix.py
"""

import asyncio
from pathlib import Path

from slowburn.fillers.coding import generate_coding_filler  # swap to fillers.qa for QA filler
from slowburn.models import ClaudeModel, GeminiModel, OpenAIModel
from slowburn.probes import ALL_PROBES
from slowburn.runner import run_matrix

MODELS = [
    ClaudeModel("claude-sonnet-4-6"),
    OpenAIModel("gpt-5"),
    GeminiModel("gemini-2.5-pro"),
]
DEPTHS = [0, 5_000, 25_000, 75_000, 150_000]
TRIALS_PER_CELL = 10
OUTPUT_PATH = Path("results/matrix.jsonl")


async def main() -> None:
    await run_matrix(
        models=MODELS,
        probes=ALL_PROBES,
        depths=DEPTHS,
        trials_per_cell=TRIALS_PER_CELL,
        filler_strategy=generate_coding_filler,
        output_path=OUTPUT_PATH,
    )


if __name__ == "__main__":
    asyncio.run(main())
