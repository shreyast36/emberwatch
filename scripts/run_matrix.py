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
    uv run python scripts/run_matrix.py --depths 0,5000 --trials 2
"""

import argparse
import asyncio
from pathlib import Path

from slowburn.fillers.coding import generate_coding_filler  # swap to fillers.qa for QA filler
from slowburn.models import ClaudeModel, GeminiModel, OpenAIModel
from slowburn.probes import ALL_PROBES
from slowburn.runner import run_matrix


def parse_args():
    parser = argparse.ArgumentParser(description="Run the Slowburn experiment matrix.")
    parser.add_argument("--depths", type=str, default="0,5000,25000,75000,150000",
                        help="Comma-separated context depths.")
    parser.add_argument("--trials", type=int, default=10, help="Trials per matrix cell.")
    parser.add_argument("--out", type=str, default="results/matrix.jsonl", help="Output JSONL path.")
    return parser.parse_args()


async def main(args) -> None:
    # Instantiate models inside the coroutine to avoid async loop conflicts during import
    models = [
        ClaudeModel("claude-sonnet-4-6"),
        OpenAIModel("gpt-4o"), # Adjusted to a real model name
        GeminiModel("gemini-2.5-pro"),
    ]
    
    depths = [int(d) for d in args.depths.split(",")]
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    await run_matrix(
        models=models,
        probes=ALL_PROBES,
        depths=depths,
        trials_per_cell=args.trials,
        filler_strategy=generate_coding_filler,
        output_path=output_path,
    )


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args))
