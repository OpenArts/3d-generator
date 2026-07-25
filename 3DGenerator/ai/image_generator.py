from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple
import numpy as np

from .prompt import PromptAnalysis


@dataclass
class ImagePlan:
    views: Dict[str, str]
    notes: str


def build_image_plan(analysis: PromptAnalysis) -> ImagePlan:
    if analysis.category == "car":
        views = {
            "front": "Front orthographic concept view of a {style} car",
            "side": "Side orthographic concept view of a {style} car",
            "top": "Top orthographic concept view of a {style} car",
            "back": "Rear orthographic concept view of a {style} car",
        }
    elif analysis.category == "building":
        views = {
            "front": "Front facade concept of a {style} building",
            "side": "Side elevation concept of a {style} building",
            "top": "Top roof concept of a {style} building",
            "back": "Rear facade concept of a {style} building",
        }
    elif analysis.category == "tree":
        views = {
            "front": "Front concept of a {style} tree",
            "side": "Side concept of a {style} tree",
            "top": "Top canopy concept of a {style} tree",
            "back": "Back concept of a {style} tree",
        }
    else:
        views = {
            "front": "Front concept of a {style} 3D object",
            "side": "Side concept of a {style} 3D object",
            "top": "Top concept of a {style} 3D object",
            "back": "Back concept of a {style} 3D object",
        }

    filled = {k: v.format(style=analysis.style_hint) for k, v in views.items()}
    notes = f"category={analysis.category}; size={analysis.size_hint}; keywords={', '.join(analysis.keywords) or 'none'}"
    return ImagePlan(views=filled, notes=notes)


def _smooth_noise(rng: np.random.Generator, size: int) -> np.ndarray:
    base = rng.random((size, size), dtype=np.float32)
    # A tiny blur-ish effect without extra dependencies.
    for _ in range(2):
        base = (
            base
            + np.roll(base, 1, axis=0)
            + np.roll(base, -1, axis=0)
            + np.roll(base, 1, axis=1)
            + np.roll(base, -1, axis=1)
        ) / 5.0
    return base


def generate_mock_concept_maps(analysis: PromptAnalysis, resolution: int = 64) -> Dict[str, np.ndarray]:
    rng = np.random.default_rng(analysis.seed)
    maps: Dict[str, np.ndarray] = {}

    yy, xx = np.mgrid[0:resolution, 0:resolution].astype(np.float32)
    xx = xx / max(1, resolution - 1)
    yy = yy / max(1, resolution - 1)

    category_bias = {
        "car": (0.55, 0.25),
        "building": (0.65, 0.35),
        "tree": (0.35, 0.55),
        "furniture": (0.45, 0.20),
        "object": (0.5, 0.3),
    }.get(analysis.category, (0.5, 0.3))

    for view in ["front", "side", "top", "back"]:
        noise = _smooth_noise(rng, resolution)
        if view == "top":
            base = 1.0 - np.sqrt((xx - 0.5) ** 2 + (yy - 0.5) ** 2) * 1.7
            base += 0.35 * noise
        elif view in {"front", "back"}:
            base = 1.0 - np.abs(xx - 0.5) * 1.7
            base += category_bias[0] * (1.0 - yy) + category_bias[1] * noise
        else:
            base = 1.0 - np.abs(yy - 0.5) * 1.7
            base += category_bias[0] * (1.0 - xx) + category_bias[1] * noise

        if analysis.category == "car":
            base += 0.12 * np.exp(-((yy - 0.7) ** 2) / 0.03)
        elif analysis.category == "building":
            base += 0.25 * yy
        elif analysis.category == "tree":
            base += 0.25 * np.exp(-((xx - 0.5) ** 2 + (yy - 0.35) ** 2) / 0.08)
        elif analysis.category == "furniture":
            base += 0.1 * np.clip(1.0 - yy * 1.4, 0, 1)

        base = np.clip(base, 0.0, 1.0)
        maps[view] = base.astype(np.float32)
    return maps
