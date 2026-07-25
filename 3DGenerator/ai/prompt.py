from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import re
from typing import Dict, List


CATEGORY_KEYWORDS = {
    "car": ["car", "sedan", "vehicle", "truck", "suv", "coupe", "van", "automobile"],
    "building": ["building", "house", "tower", "apartment", "villa", "skyscraper", "shed"],
    "tree": ["tree", "oak", "pine", "palm", "plant", "bush", "bushes", "forest"],
    "furniture": ["chair", "table", "sofa", "desk", "cabinet", "shelf", "bed", "stool", "crate"],
}


@dataclass
class PromptAnalysis:
    raw_prompt: str
    category: str
    keywords: List[str]
    size_hint: str
    style_hint: str
    complexity: float
    seed: int

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def _pick_category(prompt: str) -> str:
    prompt_l = prompt.lower()
    for category, words in CATEGORY_KEYWORDS.items():
        if any(word in prompt_l for word in words):
            return category
    return "object"


def _extract_keywords(prompt: str) -> List[str]:
    tokens = [t for t in re.split(r"[^a-zA-Z0-9_\-\u0600-\u06FF]+", prompt.lower()) if len(t) > 2]
    stop = {
        "the", "and", "with", "from", "for", "this", "that", "have", "want", "make", "create",
        "model", "object", "thing", "very", "good", "nice", "realistic", "style", "build",
    }
    keywords = []
    for t in tokens:
        if t not in stop and t not in keywords:
            keywords.append(t)
    return keywords[:8]


def analyze_prompt(prompt: str) -> PromptAnalysis:
    prompt = (prompt or "").strip()
    category = _pick_category(prompt)
    keywords = _extract_keywords(prompt)

    prompt_l = prompt.lower()
    if any(x in prompt_l for x in ["tiny", "small", "mini"]):
        size_hint = "small"
    elif any(x in prompt_l for x in ["huge", "large", "big", "tower", "skyscraper"]):
        size_hint = "large"
    else:
        size_hint = "medium"

    if any(x in prompt_l for x in ["realistic", "realism", "photoreal", "detailed"]):
        style_hint = "realistic"
    elif any(x in prompt_l for x in ["low poly", "simple", "stylized"]):
        style_hint = "stylized"
    else:
        style_hint = "balanced"

    complexity = 0.55
    if "detailed" in prompt_l or "complex" in prompt_l:
        complexity += 0.15
    if "simple" in prompt_l or "minimal" in prompt_l:
        complexity -= 0.15
    if category in {"building", "car"}:
        complexity += 0.1

    complexity = max(0.2, min(1.0, complexity))
    seed = int(hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:8], 16)

    return PromptAnalysis(
        raw_prompt=prompt,
        category=category,
        keywords=keywords,
        size_hint=size_hint,
        style_hint=style_hint,
        complexity=complexity,
        seed=seed,
    )
