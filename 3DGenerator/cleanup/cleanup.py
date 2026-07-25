from __future__ import annotations

import copy

def clean_mesh(mesh, target_triangle_count: int = 12_000, simplify_if_over: int = 25_000):
    mesh = copy.deepcopy(mesh)
    mesh.remove_duplicated_vertices()
    mesh.remove_duplicated_triangles()
    mesh.remove_degenerate_triangles()
    mesh.remove_non_manifold_edges()
    mesh.remove_unreferenced_vertices()

    if len(mesh.triangles) > simplify_if_over and target_triangle_count > 0:
        mesh = mesh.simplify_quadric_decimation(target_number_of_triangles=target_triangle_count)
        mesh.remove_degenerate_triangles()
        mesh.remove_duplicated_triangles()
        mesh.remove_non_manifold_edges()
        mesh.remove_unreferenced_vertices()

    mesh.compute_vertex_normals()
    return mesh
