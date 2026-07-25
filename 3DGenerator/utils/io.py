from __future__ import annotations

from pathlib import Path
import json
from typing import Any

import numpy as np


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _o3d():
    import open3d as o3d
    return o3d


def mesh_from_box(width=1.0, height=1.0, depth=1.0):
    o3d = _o3d()
    mesh = o3d.geometry.TriangleMesh.create_box(width=width, height=height, depth=depth)
    mesh.compute_vertex_normals()
    mesh.translate((-width / 2.0, -height / 2.0, -depth / 2.0))
    return mesh


def mesh_from_cylinder(radius=0.5, height=1.0, resolution=32, split=4):
    o3d = _o3d()
    mesh = o3d.geometry.TriangleMesh.create_cylinder(radius=radius, height=height, resolution=resolution, split=split)
    mesh.compute_vertex_normals()
    mesh.translate((0.0, -height / 2.0, 0.0))
    return mesh


def save_mesh(mesh, path: Path) -> None:
    o3d = _o3d()
    ensure_dir(path.parent)
    o3d.io.write_triangle_mesh(str(path), mesh, write_ascii=True)


def load_mesh(path: Path):
    o3d = _o3d()
    mesh = o3d.io.read_triangle_mesh(str(path))
    if mesh.is_empty():
        raise ValueError(f"Unable to read mesh: {path}")
    mesh.compute_vertex_normals()
    return mesh


def candidate_mesh_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    out = []
    for ext in ("*.obj", "*.ply", "*.stl", "*.off", "*.gltf", "*.glb"):
        out.extend(root.rglob(ext))
    return sorted({p for p in out if p.is_file()})


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")
