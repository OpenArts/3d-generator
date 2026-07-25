from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
OUTPUT_DIR = PROJECT_ROOT / "output"
CACHE_DIR = PROJECT_ROOT / "cache"
LOG_DIR = PROJECT_ROOT / "logs"


@dataclass(frozen=True)
class GenerationConfig:
    prompt: str = "wooden crate"
    template_type: str = "object"
    output_name: str = "generated_asset"
    target_triangle_count: int = 12_000
    displacement_strength: float = 0.08
    map_resolution: int = 64
    random_seed: int = 42
    export_obj: bool = True
    export_ply: bool = True
    export_metadata: bool = True
    simplify_if_over: int = 25_000
    simplify_target: int = 12_000


DEFAULT_CONFIG = GenerationConfig()
