from __future__ import annotations


def maybe_subdivide(mesh, target_triangles: int = 12_000):
    if len(mesh.triangles) >= target_triangles:
        return mesh
    return mesh.subdivide_midpoint(number_of_iterations=1)
