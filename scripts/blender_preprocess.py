import bpy, sys, json, os, argparse

argv = sys.argv[sys.argv.index("--") + 1:]
parser = argparse.ArgumentParser()
parser.add_argument("--input")
parser.add_argument("--output")
args = parser.parse_args(argv)

bpy.ops.wm.read_factory_settings(use_empty=True)

ext = os.path.splitext(args.input)[1].lower()
if ext == ".fbx":
    bpy.ops.import_scene.fbx(filepath=args.input)
elif ext == ".obj":
    bpy.ops.import_scene.obj(filepath=args.input)
elif ext in (".gltf", ".glb"):
    bpy.ops.import_scene.gltf(filepath=args.input)
elif ext == ".blend":
    bpy.ops.wm.open_mainfile(filepath=args.input)
else:
    print(f"Unsupported format: {ext}", file=sys.stderr)
    sys.exit(1)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.transform_apply(scale=True)

meshes = []
for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    bb = obj.bound_box
    world_coords = [obj.matrix_world @ __import__('mathutils').Vector(v) for v in bb]
    xs = [v.x for v in world_coords]
    ys = [v.y for v in world_coords]
    zs = [v.z for v in world_coords]
    meshes.append({
        "name": obj.name,
        "boundingBox": {
            "min": [min(xs), min(ys), min(zs)],
            "max": [max(xs), max(ys), max(zs)]
        },
        "pivot": list(obj.location),
        "parent": obj.parent.name if obj.parent else None,
        "children": [c.name for c in obj.children if c.type == 'MESH'],
        "vertexCount": len(obj.data.vertices),
        "hasCollisionMesh": False
    })

jobId = os.path.basename(args.output).replace("-object-manifest.json", "")
manifest = {
    "jobId": jobId,
    "sourceFile": args.input,
    "units": "meters",
    "meshes": meshes
}

os.makedirs(os.path.dirname(args.output), exist_ok=True)
with open(args.output, "w") as f:
    json.dump(manifest, f, indent=2)

print(f"Object manifest written: {args.output}")