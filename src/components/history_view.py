from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict


@dataclass
class HistoryEntry:
    timestamp: str
    label: str
    confidence: int
    source: str


class HistoryStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.entries: List[HistoryEntry] = self._load()

    def _load(self) -> List[HistoryEntry]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return [HistoryEntry(**item) for item in data]
        except Exception:
            return []

    def add(self, label: str, confidence: int, source: str) -> None:
        entry = HistoryEntry(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
            label=label,
            confidence=confidence,
            source=source,
        )
        self.entries.insert(0, entry)
        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [entry.__dict__ for entry in self.entries]
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
