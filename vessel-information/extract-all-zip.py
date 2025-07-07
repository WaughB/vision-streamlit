import os
import zipfile
from tqdm import tqdm

# --- Configuration ---
ZIP_DIR = "data/ais_2024"
EXTRACT_DIR = os.path.join(ZIP_DIR, "extracted")
os.makedirs(EXTRACT_DIR, exist_ok=True)

print(f"\n📂 Searching ZIP files in directory: {os.path.abspath(ZIP_DIR)}")
zip_files = [f for f in os.listdir(ZIP_DIR) if f.lower().endswith(".zip")]

print(f"📦 Found {len(zip_files)} zip file(s) to extract.\n")

# --- Extraction loop with tqdm ---
for filename in tqdm(zip_files, desc="Extracting ZIP files"):
    zip_path = os.path.join(ZIP_DIR, filename)
    subfolder_name = os.path.splitext(filename)[0]
    target_path = os.path.join(EXTRACT_DIR, subfolder_name)

    try:
        print(f"\n🔍 Extracting: {filename}")
        print(f"➡️  Target folder: {target_path}")

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            os.makedirs(target_path, exist_ok=True)
            zip_ref.extractall(target_path)

        print(f"✅ Extracted: {filename}\n")

    except Exception as e:
        print(f"❌ Failed to extract {filename}: {e}")

print("\n🎉 All extractions complete.")
