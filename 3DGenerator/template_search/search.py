from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from utils.io import candidate_mesh_files, mesh_from_box, mesh_from_cylinder, load_mesh, save_mesh, ensure_dir
from config import TEMPLATES_DIR


@dataclass
class TemplateMatch:
    path: Optional[Path]
    category: str
    score: float
    source: str


def _fallback_template(category: str):
    if category == "tree":
        return mesh_from_cylinder(radius=0.22, height=1.6, resolution=24, split=6)
    if category == "building":
        return mesh_from_box(width=1.4, height=2.4, depth=1.2)
    if category == "car":
        body = mesh_from_box(width=2.0, height=0.6, depth=1.0)
        roof = mesh_from_box(width=1.0, height=0.35, depth=0.8)
        roof.translate((0.0, 0.35, 0.0))
        body += roof
        body.compute_vertex_normals()
        return body
    if category == "furniture":
        return mesh_from_box(width=1.0, height=0.6, depth=0.7)
    return mesh_from_box(width=1.0, height=1.0, depth=1.0)


def search_template(category: str, keywords: list[str] | None = None) -> TemplateMatch:
    keywords = [k.lower() for k in (keywords or [])]
    files = candidate_mesh_files(TEMPLATES_DIR)

    best_score = -1.0
    best_file: Optional[Path] = None
    for file in files:
        name = file.stem.lower()
        score = 0.0
        if category in name:
            score += 5.0
        for kw in keywords:
            if kw in name:
                score += 1.0
        if score > best_score:
            best_score = score
            best_file = file

    if best_file is not None:
        return TemplateMatch(path=best_file, category=category, score=best_score, source="file")

    return TemplateMatch(path=None, category=category, score=0.0, source="generated")


def load_selected_template(match: TemplateMatch):
    if match.path is not None:
        return load_mesh(match.path)
    return _fallback_template(match.category)


def ensure_default_templates() -> None:
    ensure_dir(TEMPLATES_DIR)
    defaults = {
        "car": _fallback_template("car"),
        "building": _fallback_template("building"),
        "tree": _fallback_template("tree"),
        "furniture": _fallback_template("furniture"),
        "object": _fallback_template("object"),
    }
    for name, mesh in defaults.items():
        path = TEMPLATES_DIR / f"{name}.obj"
        if not path.exists():
            save_mesh(mesh, path)
