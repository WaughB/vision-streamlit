import os
import shutil

# Paths
ROOT_DIR = "data/ais_2024/extracted"
TARGET_DIR = "data"

# Ensure target directory exists
os.makedirs(TARGET_DIR, exist_ok=True)

moved = 0
skipped = 0

print(f"\n📂 Searching for .csv files in: {os.path.abspath(ROOT_DIR)}\n")

# Walk through subdirectories
for root, dirs, files in os.walk(ROOT_DIR):
    for file in files:
        if file.lower().endswith(".csv"):
            source_path = os.path.join(root, file)
            target_path = os.path.join(TARGET_DIR, file)

            # Avoid overwriting existing files
            if os.path.exists(target_path):
                print(f"⚠️ Skipping (already exists): {file}")
                skipped += 1
                continue

            shutil.move(source_path, target_path)
            print(f"✅ Moved: {file}")
            moved += 1

print(f"\n🎉 Done. Moved {moved} file(s), skipped {skipped} existing.")
print(f"📁 All .csv files are now in: {os.path.abspath(TARGET_DIR)}")
