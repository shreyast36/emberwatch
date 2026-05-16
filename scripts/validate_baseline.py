"""Run probes at depth 0 to confirm verdict stability.

Owner: Dhanush. See ROLES.md.

Usage:
    uv run python scripts/validate_baseline.py
"""

import asyncio

from slowburn.baseline import validate_baseline


async def main() -> None:
    raise NotImplementedError("TODO(dhanush): wire up models + probes and print report")


if __name__ == "__main__":
    asyncio.run(main())
