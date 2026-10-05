import os
import sys
import UnityPy

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_ROOT = os.path.join(ROOT, "extracted")
SKIP_DIRS = {".git", "extracted", ".github", "node_modules"}


def find_all_ab():
    found = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.lower().endswith(".ab"):
                found.append(os.path.join(base, f))
    return found


def unique_path(folder, name, ext=".png"):
    path = os.path.join(folder, f"{name}{ext}")
    i = 1
    while os.path.exists(path):
        path = os.path.join(folder, f"{name}_{i}{ext}")
        i += 1
    return path


def extract(fpath):
    rel = os.path.relpath(fpath, ROOT)
    # extracted/<path/to/file.ab without extension>/
    out_dir = os.path.join(OUT_ROOT, os.path.splitext(rel)[0])
    os.makedirs(out_dir, exist_ok=True)
    print(f"Loading {rel}...")
    env = UnityPy.load(fpath)
    count = 0

    # Sprites first: UnityPy crops individual icons from the atlas sheet
    for obj in env.objects:
        if obj.type.name == "Sprite":
            try:
                data = obj.read()
                name = getattr(data, "m_Name", None) or str(obj.path_id)
                img = getattr(data, "image", None)
                if img:
                    img.save(unique_path(out_dir, name))
                    count += 1
                    print(f"  [Sprite] {name}")
            except Exception as e:
                print(f"  ! Sprite {obj.path_id} failed: {e}")

    # Raw Texture2D sheets
    for obj in env.objects:
        if obj.type.name == "Texture2D":
            try:
                data = obj.read()
                name = getattr(data, "m_Name", None) or str(obj.path_id)
                img = getattr(data, "image", None)
                if img:
                    img.save(unique_path(out_dir, f"tex_{name}"))
                    count += 1
                    print(f"  [Texture2D] tex_{name}")
            except Exception as e:
                print(f"  ! Texture2D {obj.path_id} failed: {e}")

    print(f"  -> {count} assets from {rel}")


def main():
    # Files passed as args (changed files in a push); otherwise scan whole repo
    targets = [os.path.abspath(p) for p in sys.argv[1:] if os.path.isfile(p)]
    if not targets:
        targets = find_all_ab()
    if not targets:
        print("No .ab files found.")
        return
    for t in targets:
        try:
            extract(t)
        except Exception as e:
            print(f"Failed on {t}: {e}")
    print("Extraction complete.")


if __name__ == "__main__":
    main()
