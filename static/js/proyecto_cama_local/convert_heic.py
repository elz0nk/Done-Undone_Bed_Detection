import os
from PIL import Image
import pillow_heif

# REGISTRO OBLIGATORIO
pillow_heif.register_heif_opener()

DATASET_DIR = "dataset"
CATEGORIES = ["hecha", "no_hecha"]

def convert_image(path):
    try:
        img = Image.open(path)
        new_path = path.rsplit(".", 1)[0] + ".jpg"
        img.save(new_path, "JPEG", quality=95)
        return True, new_path
    except Exception as e:
        print(f"ERROR convirtiendo {path}: {e}")
        return False, None

for category in CATEGORIES:
    folder = os.path.join(DATASET_DIR, category)

    for file in os.listdir(folder):
        if file.lower().endswith(".heic"):
            heic_path = os.path.join(folder, file)
            print(f"Procesando {heic_path}")

            ok, jpg_path = convert_image(heic_path)

            if ok and os.path.exists(jpg_path):
                os.remove(heic_path)
                print(f"✔ Convertido y borrado: {file}")
            else:
                print(f"✖ NO se pudo convertir: {file} (NO borrado)")
