from __future__ import annotations

from typing import Dict
import copy

import numpy as np


def _o3d():
    import open3d as o3d
    return o3d


def _bilinear_sample(map2d: np.ndarray, u: float, v: float) -> float:
    h, w = map2d.shape[:2]
    u = float(np.clip(u, 0.0, 1.0)) * (w - 1)
    v = float(np.clip(v, 0.0, 1.0)) * (h - 1)
    x0 = int(np.floor(u))
    y0 = int(np.floor(v))
    x1 = min(x0 + 1, w - 1)
    y1 = min(y0 + 1, h - 1)
    sx = u - x0
    sy = v - y0

    v00 = float(map2d[y0, x0])
    v10 = float(map2d[y0, x1])
    v01 = float(map2d[y1, x0])
    v11 = float(map2d[y1, x1])

    return (v00 * (1 - sx) + v10 * sx) * (1 - sy) + (v01 * (1 - sx) + v11 * sx) * sy


def _normalize_positions(vertices: np.ndarray):
    mins = vertices.min(axis=0)
    maxs = vertices.max(axis=0)
    spans = np.maximum(maxs - mins, 1e-8)
    return (vertices - mins) / spans, mins, spans


def deform_mesh(mesh, displacement_maps: Dict[str, np.ndarray], strength: float = 0.08):
    o3d = _o3d()
    mesh = copy.deepcopy(mesh)
    vertices = np.asarray(mesh.vertices).copy()
    normals = np.asarray(mesh.vertex_normals).copy() if mesh.has_vertex_normals() else None

    if normals is None or len(normals) != len(vertices):
        mesh.compute_vertex_normals()
        normals = np.asarray(mesh.vertex_normals).copy()

    normalized, _, _ = _normalize_positions(vertices)

    top_map = displacement_maps.get("top")
    front_map = displacement_maps.get("front")
    side_map = displacement_maps.get("side")
    back_map = displacement_maps.get("back")

    if top_map is None:
        raise ValueError("displacement_maps must contain at least a 'top' map")

    for i, (p, n) in enumerate(zip(normalized, normals)):
        x, y, z = map(float, p)
        top = _bilinear_sample(top_map, x, z)
        front = _bilinear_sample(front_map, x, y) if front_map is not None else top
        side = _bilinear_sample(side_map, z, y) if side_map is not None else top
        back = _bilinear_sample(back_map, 1.0 - x, y) if back_map is not None else front

        blend = 0.45 * top + 0.25 * front + 0.2 * side + 0.1 * back
        power = 0.65 + 0.35 * blend
        offset = strength * power * (blend - 0.5)

        vertices[i] = vertices[i] + n * offset

    mesh.vertices = o3d.utility.Vector3dVector(vertices)
    mesh.compute_vertex_normals()
    return mesh
