from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class TemplateRecord:
    name: str
    category: str
    path: str
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TemplateDatabase:
    def __init__(self):
        self.records: list[TemplateRecord] = []

    def add(self, record: TemplateRecord) -> None:
        self.records.append(record)

    def find_by_category(self, category: str) -> list[TemplateRecord]:
        category = category.lower()
        return [r for r in self.records if r.category.lower() == category]
