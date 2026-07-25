from __future__ import annotations

import argparse
from pathlib import Path

from ai.prompt import analyze_prompt
from ai.displacement_generator import generate_displacement_maps
from cleanup.cleanup import clean_mesh
from config import DEFAULT_CONFIG, OUTPUT_DIR
from deformation.deform import deform_mesh
from template_search.search import ensure_default_templates, load_selected_template, search_template
from utils.io import ensure_dir, save_mesh, write_json


def run_pipeline(prompt: str, template_type: str = "object", output_name: str = "generated_asset"):
    ensure_default_templates()

    analysis = analyze_prompt(prompt)
    if template_type and template_type != "object":
        analysis.category = template_type  # runtime override for the first prototype

    print(f"[1/6] Prompt analysis: {analysis.category} | {analysis.size_hint} | {analysis.style_hint}")
    print(f"[2/6] Building displacement maps...")
    bundle = generate_displacement_maps(
        analysis,
        resolution=DEFAULT_CONFIG.map_resolution,
        strength=DEFAULT_CONFIG.displacement_strength,
    )

    print(f"[3/6] Searching template...")
    match = search_template(analysis.category, analysis.keywords)
    print(f"    Selected: {match.source} | score={match.score:.2f} | path={match.path}")

    mesh = load_selected_template(match)
    print(f"[4/6] Deforming mesh...")
    mesh = deform_mesh(mesh, bundle.maps, strength=bundle.strength)

    print(f"[5/6] Cleaning mesh...")
    mesh = clean_mesh(
        mesh,
        target_triangle_count=DEFAULT_CONFIG.simplify_target,
        simplify_if_over=DEFAULT_CONFIG.simplify_if_over,
    )

    out_dir = ensure_dir(OUTPUT_DIR / output_name)
    obj_path = out_dir / f"{output_name}.obj"
    ply_path = out_dir / f"{output_name}.ply"
    meta_path = out_dir / "metadata.json"

    print(f"[6/6] Exporting...")
    save_mesh(mesh, obj_path)
    save_mesh(mesh, ply_path)

    meta = {
        "prompt": prompt,
        "analysis": analysis.to_dict(),
        "template": {
            "source": match.source,
            "path": str(match.path) if match.path else None,
            "score": match.score,
        },
        "exports": {
            "obj": str(obj_path),
            "ply": str(ply_path),
        },
        "displacement_strength": bundle.strength,
        "resolution": bundle.resolution,
    }
    write_json(meta_path, meta)

    print("Done.")
    print(f"OBJ: {obj_path}")
    print(f"PLY: {ply_path}")
    print(f"Meta: {meta_path}")


def main():
    parser = argparse.ArgumentParser(description="3DGenerator prototype pipeline")
    parser.add_argument("--prompt", type=str, default=DEFAULT_CONFIG.prompt)
    parser.add_argument("--template-type", type=str, default=DEFAULT_CONFIG.template_type)
    parser.add_argument("--output-name", type=str, default=DEFAULT_CONFIG.output_name)
    args = parser.parse_args()

    run_pipeline(
        prompt=args.prompt,
        template_type=args.template_type,
        output_name=args.output_name,
    )


if __name__ == "__main__":
    main()
