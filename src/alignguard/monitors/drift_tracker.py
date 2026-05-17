"""Agent D — Drift Tracker.

Reads the historical alignment signal time-series from the store and detects
sharp safety degradation. Compares the rolling average of the early half of
recent signals against the late half. Emits a DRIFT signal if degradation
exceeds the configured threshold.
"""

from alignguard.store import AlignmentStore
from alignguard.types import AlignmentSignal, SignalType

_DRIFT_THRESHOLD = 0.15   # score drop triggering a drift alert
_MIN_HISTORY = 6          # minimum stored signals before drift can be detected
_WINDOW = 20              # how many recent signals to analyse


class DriftTracker:
    def __init__(self, store: AlignmentStore, threshold: float = _DRIFT_THRESHOLD) -> None:
        self.store = store
        self.threshold = threshold

    def analyze(self, session_id: str) -> AlignmentSignal | None:
        """Return a DRIFT signal if degradation detected, else None."""
        recent = self.store.load_recent_signals(
            _WINDOW,
            signal_type=None,  # include all signal types for the trend
        )
        # Exclude previous DRIFT signals to avoid feedback loops
        scored = [s for s in recent if s.signal_type != SignalType.DRIFT]
        if len(scored) < _MIN_HISTORY:
            return None

        mid = len(scored) // 2
        early_avg = sum(s.score for s in scored[:mid]) / mid
        late_avg = sum(s.score for s in scored[mid:]) / (len(scored) - mid)
        delta = late_avg - early_avg  # negative = degradation

        if delta < -self.threshold:
            return AlignmentSignal(
                signal_type=SignalType.DRIFT,
                agent_name="system",
                score=late_avg,
                evidence=(
                    f"Alignment score dropped from {early_avg:.2f} (early) to "
                    f"{late_avg:.2f} (recent) — delta={delta:+.2f} over "
                    f"{len(scored)} signals."
                ),
                session_id=session_id,
            )
        return None
