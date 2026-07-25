from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np

from .prompt import PromptAnalysis


@dataclass
class DisplacementBundle:
    maps: Dict[str, np.ndarray]
    strength: float
    resolution: int


def generate_displacement_maps(
    analysis: PromptAnalysis,
    resolution: int = 64,
    strength: float = 0.08,
) -> DisplacementBundle:
    from .image_generator import generate_mock_concept_maps

    concept_maps = generate_mock_concept_maps(analysis, resolution=resolution)
    maps: Dict[str, np.ndarray] = {}

    # Make displacement a little sharper than concept maps.
    for name, arr in concept_maps.items():
        normalized = arr - arr.min()
        if normalized.max() > 0:
            normalized = normalized / normalized.max()
        maps[name] = np.clip(normalized, 0.0, 1.0).astype(np.float32)

    return DisplacementBundle(maps=maps, strength=float(strength), resolution=int(resolution))
