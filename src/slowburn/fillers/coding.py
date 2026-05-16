"""Innocuous coding-conversation filler.

Owner: Binjie. See ROLES.md.
"""


def generate_coding_filler(target_tokens: int, seed: int) -> list[dict]:
    """Produce an alternating user/assistant coding conversation ~target_tokens long.

    TODO(binjie):
    - seed-deterministic generation
    - tiktoken-based length targeting
    - hard ban on any safety-relevant phrases (refusals, jailbreak language, value statements)
    """
    raise NotImplementedError
