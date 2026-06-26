"""
blender_simulate_render.py — Phase 5 (Simulation) + Phase 6 (Rendering)
Run via: blender --background --python scripts/blender_simulate_render.py -- \
           --cad <path> --simjson <path> --manifest <path> --outdir <path>
"""

import bpy
import sys
import json
import os
import math
import mathutils
import argparse


# ─── Arg parsing ──────────────────────────────────────────────────────────────

def get_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    parser = argparse.ArgumentParser()
    parser.add_argument("--cad",      required=True, help="Path to CAD file")
    parser.add_argument("--simjson",  required=True, help="Path to simulation-execution.json")
    parser.add_argument("--manifest", required=True, help="Path to object-manifest.json")
    parser.add_argument("--outdir",   required=True, help="Directory for rendered frames")
    return parser.parse_args(argv)


# ─── CAD import ───────────────────────────────────────────────────────────────

def import_cad(cad_path):
    ext = os.path.splitext(cad_path)[1].lower()
    print(f"[Phase 5] Importing {ext.upper()}: {cad_path}")
    if ext == ".obj":
        bpy.ops.wm.obj_import(filepath=cad_path)
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=cad_path)
    elif ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=cad_path)
    elif ext in (".usd", ".usda", ".usdc"):
        bpy.ops.wm.usd_import(filepath=cad_path)
    elif ext == ".abc":
        bpy.ops.wm.alembic_import(filepath=cad_path)
    elif ext == ".blend":
        # Link all objects from a .blend library
        with bpy.data.libraries.load(cad_path, link=False) as (src, dst):
            dst.objects = src.objects
        for obj in bpy.context.scene.collection.objects:
            pass  # objects auto-linked
    else:
        print(f"[ERROR] Unsupported CAD extension: {ext}", file=sys.stderr)
        sys.exit(1)
    print(f"[Phase 5] Import complete. Objects in scene: {len(bpy.data.objects)}")


# ─── Keyframes ────────────────────────────────────────────────────────────────

def apply_keyframes(sim_data):
    """Apply per-object keyframes (location + rotation_euler)."""
    frame_rate   = sim_data.get("frameRate", 24)
    total_frames = sim_data.get("totalFrames", 240)

    scene = bpy.context.scene
    scene.render.fps    = frame_rate
    scene.frame_start   = 0
    scene.frame_end     = total_frames

    INTERP_MAP = {"LINEAR": "LINEAR", "BEZIER": "BEZIER", "CONSTANT": "CONSTANT"}

    missing = []
    for obj_data in sim_data.get("objects", []):
        mesh_name = obj_data.get("meshName", "")
        obj = bpy.data.objects.get(mesh_name)
        if obj is None:
            missing.append(mesh_name)
            print(f"[Phase 5] WARNING: mesh '{mesh_name}' not found in scene — skipped.",
                  file=sys.stderr)
            continue

        for kf in obj_data.get("keyframes", []):
            frame    = kf.get("frame", 0)
            position = kf.get("position", [0, 0, 0])
            rotation = kf.get("rotation", [0, 0, 0])  # degrees
            interp   = INTERP_MAP.get(kf.get("interpolation", "LINEAR"), "LINEAR")

            scene.frame_set(frame)
            obj.location        = position
            obj.rotation_euler  = [math.radians(r) for r in rotation]
            obj.keyframe_insert(data_path="location",       frame=frame)
            obj.keyframe_insert(data_path="rotation_euler", frame=frame)

            scale = kf.get("scale", None)
            if scale is not None:
                obj.scale = scale
                obj.keyframe_insert(data_path="scale", frame=frame)

            # Set interpolation type on the keyframe just inserted
            if obj.animation_data and obj.animation_data.action:
                for fc in obj.animation_data.action.fcurves:
                    for kfp in fc.keyframe_points:
                        if kfp.co[0] == frame:
                            kfp.interpolation = interp

    if missing:
        print(f"[Phase 5] {len(missing)} mesh(es) not found and skipped: {missing}",
              file=sys.stderr)


# ─── Constraints ──────────────────────────────────────────────────────────────

def apply_constraints(sim_data):
    """Apply Blender constraints from objects[].constraints."""
    CTYPE_MAP = {
        "track_to":       "TRACK_TO",
        "limit_location": "LIMIT_LOCATION",
        "limit_rotation": "LIMIT_ROTATION",
        "child_of":       "CHILD_OF",
    }
    for obj_data in sim_data.get("objects", []):
        obj = bpy.data.objects.get(obj_data.get("meshName", ""))
        if obj is None:
            continue
        for cd in obj_data.get("constraints", []):
            c_type  = cd.get("type", "")
            t_name  = cd.get("targetMesh", "")
            t_obj   = bpy.data.objects.get(t_name)

            if c_type == "parent":
                if t_obj:
                    obj.parent = t_obj
                    print(f"[Phase 5] Parented '{obj.name}' → '{t_name}'")
                else:
                    print(f"[Phase 5] WARNING: parent target '{t_name}' not found.",
                          file=sys.stderr)
            elif c_type in CTYPE_MAP:
                btype = CTYPE_MAP[c_type]
                c = obj.constraints.new(type=btype)
                if t_obj:
                    c.target = t_obj
                print(f"[Phase 5] Constraint {btype} on '{obj.name}' → '{t_name}'")
            else:
                print(f"[Phase 5] WARNING: unknown constraint type '{c_type}' — skipped.",
                      file=sys.stderr)


# ─── Camera ───────────────────────────────────────────────────────────────────

def setup_camera(sim_data):
    """Keyframe camera from cameraPath (position + lookAt per frame)."""
    cam_path = sim_data.get("cameraPath", [])
    if not cam_path:
        print("[Phase 5] WARNING: no cameraPath — using default camera.", file=sys.stderr)
        return

    # Ensure a camera object exists
    cam_data = bpy.data.cameras.get("SimCamera") or bpy.data.cameras.new("SimCamera")
    cam_obj  = bpy.data.objects.get("SimCamera")
    if cam_obj is None:
        cam_obj = bpy.data.objects.new("SimCamera", cam_data)
        bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    for ckf in cam_path:
        frame    = ckf.get("frame", 0)
        position = ckf.get("position", [5, -5, 5])
        look_at  = ckf.get("lookAt",   [0,  0,  0])
        fov      = ckf.get("fov")          # degrees or None

        bpy.context.scene.frame_set(frame)
        cam_obj.location = mathutils.Vector(position)

        # Compute rotation: camera looks along -Z, Y is up
        direction = mathutils.Vector(look_at) - mathutils.Vector(position)
        if direction.length > 1e-6:
            rot_quat = direction.to_track_quat("-Z", "Y")
            cam_obj.rotation_euler = rot_quat.to_euler()

        cam_obj.keyframe_insert(data_path="location",       frame=frame)
        cam_obj.keyframe_insert(data_path="rotation_euler", frame=frame)

        if fov is not None:
            cam_data.lens = cam_data.sensor_width / (2 * math.tan(math.radians(fov) / 2))
            cam_data.keyframe_insert(data_path="lens", frame=frame)

    print(f"[Phase 5] Camera keyframed over {len(cam_path)} control point(s).")


# ─── Materials ────────────────────────────────────────────────────────────────

def setup_materials():
    """Assign Principled BSDF materials to known demo objects."""
    configs = {
        "TriPyramid": (0.65, 0.70, 0.80, 0.8, 0.1),   # silver-blue metallic
        "SqPyramid":  (0.85, 0.60, 0.15, 0.7, 0.2),   # gold
        "Label1":     (0.90, 0.15, 0.15, 0.0, 0.0),   # red
        "Label2":     (0.15, 0.75, 0.15, 0.0, 0.0),   # green
        "Label3":     (0.15, 0.35, 0.90, 0.0, 0.0),   # blue
        "Label4":     (0.95, 0.75, 0.05, 0.0, 0.0),   # yellow
    }
    for name, (r, g, b, metallic, roughness_add) in configs.items():
        obj = bpy.data.objects.get(name)
        if obj is None or obj.type != 'MESH':
            continue
        mat = bpy.data.materials.new(name=f"Mat_{name}")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
            bsdf.inputs["Metallic"].default_value   = metallic
            bsdf.inputs["Roughness"].default_value  = 0.25 + roughness_add
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        # Smooth shading
        for poly in obj.data.polygons:
            poly.use_smooth = True
    print(f"[Phase 5] Materials assigned.")


# ─── Lighting ─────────────────────────────────────────────────────────────────

def add_default_lighting():
    """Add a simple 3-point sun setup for POC renders."""
    lights = [
        ("KeyLight",  "SUN", (8,  -8,  10), (math.radians(45), 0, math.radians(30)),  5.0),
        ("FillLight", "SUN", (-6,  6,   6), (math.radians(30), 0, math.radians(210)), 1.5),
        ("RimLight",  "SUN", (0,   8,   4), (math.radians(60), 0, math.radians(0)),   2.0),
    ]
    for name, ltype, loc, rot, energy in lights:
        ld  = bpy.data.lights.new(name=name, type=ltype)
        ld.energy = energy
        lo  = bpy.data.objects.new(name, ld)
        bpy.context.collection.objects.link(lo)
        lo.location       = loc
        lo.rotation_euler = rot

    # Subtle world background
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.04, 0.04, 0.04, 1.0)
        bg.inputs[1].default_value = 1.0
    print("[Phase 6] Default 3-point lighting added.")


# ─── Render settings ──────────────────────────────────────────────────────────

def configure_render(outdir, frame_rate):
    """Configure Cycles + OptiX, 4K, 512 samples, PNG 16-bit output."""
    scene = bpy.context.scene
    scene.render.engine    = "CYCLES"
    scene.cycles.device    = "GPU"

    # OptiX → CUDA fallback → CPU
    prefs = bpy.context.preferences.addons.get("cycles")
    if prefs:
        pref = prefs.preferences
        for backend in ("OPTIX", "CUDA"):
            try:
                pref.compute_device_type = backend
                pref.get_devices()
                for dev in pref.devices:
                    dev.use = True
                print(f"[Phase 6] GPU backend: {backend}")
                break
            except Exception:
                continue
        else:
            scene.cycles.device = "CPU"
            print("[Phase 6] WARNING: GPU unavailable — falling back to CPU.", file=sys.stderr)

    # Resolution (4K)
    scene.render.resolution_x          = 3840
    scene.render.resolution_y          = 2160
    scene.render.resolution_percentage = 100
    scene.render.fps                   = frame_rate

    # Samples + adaptive sampling
    scene.cycles.samples               = 512
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold    = 0.01

    # Denoiser (OptiX preferred)
    scene.cycles.use_denoising = True
    for denoiser in ("OPTIX", "NLM", "OPENIMAGEDENOISE"):
        try:
            scene.cycles.denoiser = denoiser
            break
        except Exception:
            continue

    # Color management — AgX (Blender 4.x default)
    try:
        scene.view_settings.view_transform = "AgX"
    except Exception:
        pass

    # Output format
    scene.render.image_settings.file_format  = "PNG"
    scene.render.image_settings.color_depth  = "16"
    scene.render.image_settings.color_mode   = "RGBA"

    # Output path — Blender appends frame number: frame_0001.png, frame_0002.png …
    os.makedirs(outdir, exist_ok=True)
    blender_outdir = outdir.replace("\\", "/")
    scene.render.filepath            = blender_outdir + "/frame_"
    scene.render.use_file_extension  = True
    scene.render.use_render_cache    = False

    print(f"[Phase 6] Render → {outdir}")
    print(f"[Phase 6] Engine: Cycles | 4K | 512 samples | AdaptiveSampling | PNG 16-bit")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    args = get_args()
    print(f"[START] blender_simulate_render.py")
    print(f"  cad:      {args.cad}")
    print(f"  simjson:  {args.simjson}")
    print(f"  manifest: {args.manifest}")
    print(f"  outdir:   {args.outdir}")

    # Load sim JSON
    with open(args.simjson, "r", encoding="utf-8") as f:
        sim_data = json.load(f)

    frame_rate   = sim_data.get("frameRate", 24)
    total_frames = sim_data.get("totalFrames", 240)

    # ── Phase 5: Simulation ─────────────────────────────────────────────────

    # 1. Clear default scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # 2. Import CAD
    import_cad(args.cad)

    # 3. Apply keyframes
    print("[Phase 5] Applying keyframes...")
    apply_keyframes(sim_data)

    # 3b. Materials
    setup_materials()
    # 4. Apply constraints
    print("[Phase 5] Applying constraints...")
    apply_constraints(sim_data)

    # 5. Setup camera
    print("[Phase 5] Setting up camera...")
    setup_camera(sim_data)

    # ── Phase 6: Rendering ──────────────────────────────────────────────────

    # 6. Add lighting
    add_default_lighting()

    # 7. Configure Cycles render
    configure_render(args.outdir, frame_rate)

    # 8. Set frame range and render
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end   = total_frames

    print(f"[Phase 6] Rendering {total_frames} frames @ {frame_rate}fps ...")
    bpy.ops.render.render(animation=True)

    print("[DONE] blender_simulate_render.py complete.")
    sys.exit(0)


if __name__ == "__main__":
    main()