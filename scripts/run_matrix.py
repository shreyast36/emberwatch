"""Main experiment runner.

Owner: Shreyas. See ROLES.md.

Default config (2 x 5 x 5 x 10 = 500 runs — budget accordingly):
  models  = ClaudeModel("claude-opus-4-7"), OpenAIModel("gpt-5")
  probes  = all 5
  depths  = [0, 5000, 25000, 75000, 150000]
  trials  = 10
  filler  = coding (swap to qa by changing the import below)
  judge   = grok-4.3 via xAI  (off the test panel)

Gemini and Wafer/GLM were dropped from the panel: Gemini's free-tier quota is 0
(needs billing) and Wafer's published base URL doesn't expose OpenAI-compatible paths.

Usage:
    uv run python scripts/run_matrix.py
    uv run python scripts/run_matrix.py --depths 0,5000 --trials 2
"""

import argparse
import asyncio
from pathlib import Path

from slowburn.fillers.coding import generate_coding_filler  # swap to fillers.qa for QA filler
from slowburn.models import ClaudeModel, OpenAIModel
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
        ClaudeModel("claude-opus-4-7"),
        OpenAIModel("gpt-5"),
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
