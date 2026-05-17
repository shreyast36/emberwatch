"""JSONL-backed persistence for alignment signals and alerts."""

import json
from pathlib import Path

from alignguard.types import Alert, AlignmentSignal, SignalType


class AlignmentStore:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append_signal(self, signal: AlignmentSignal) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(signal.model_dump_json() + "\n")

    def append_alert(self, alert: Alert, alerts_path: Path | None = None) -> None:
        target = alerts_path or self.path.parent / "alerts.jsonl"
        with target.open("a", encoding="utf-8") as f:
            f.write(alert.model_dump_json() + "\n")

    def load_signals(self) -> list[AlignmentSignal]:
        if not self.path.exists():
            return []
        signals = []
        with self.path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        signals.append(AlignmentSignal.model_validate_json(line))
                    except Exception:
                        continue
        return signals

    def load_recent_signals(self, n: int, signal_type: SignalType | None = None) -> list[AlignmentSignal]:
        all_signals = self.load_signals()
        if signal_type:
            all_signals = [s for s in all_signals if s.signal_type == signal_type]
        return all_signals[-n:]

    def session_signals(self, session_id: str) -> list[AlignmentSignal]:
        return [s for s in self.load_signals() if s.session_id == session_id]
