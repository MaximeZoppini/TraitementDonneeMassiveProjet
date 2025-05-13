import os
import json
import cv2
import numpy as np
import pandas as pd
from PIL import Image, ExifTags
from sqlalchemy import create_engine, text
from sklearn.cluster import KMeans
from config import DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME
from urllib.parse import unquote
IMAGE_FOLDER = "images"
ANNOTATION_FILE = "annotations.json"

os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Connexion à la base de données
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
import time

# Attendre que des images soient bien présentes dans la base
def wait_for_images():
    while True:
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM images"))

                count = result.scalar()
                if count > 0:
                    print(f"[annotation] {count} images trouvées dans la base.")
                    break
                else:
                    print("[annotation] En attente d'images dans la base...")
        except Exception as e:
            print(f"[annotation] Erreur en vérifiant la base : {e}")
        time.sleep(2)

wait_for_images()

print("[annotation] Lecture des noms de fichiers d'images depuis la base...")
df_images = pd.read_sql("SELECT image_filename FROM images", engine)
print(f"[annotation] Images à traiter : {df_images.shape[0]}")

def convert_to_serializable(obj):
    try:
        return float(obj)
    except (TypeError, ValueError):
        return str(obj)

def safe_div(num, denom):
    try:
        return float(num) / float(denom) if denom != 0 else 0
    except:
        return 0

def get_exif_data(image):
    try:
        exif_data = image._getexif()
        if not exif_data:
            return {}
        return {
            ExifTags.TAGS.get(tag, tag): convert_to_serializable(value)
            for tag, value in exif_data.items()
        }
    except AttributeError:
        return {}

def get_gps_info(exif_data):
    if "GPSInfo" not in exif_data:
        return None
    gps_info = exif_data["GPSInfo"]
    if 2 not in gps_info or 4 not in gps_info:
        return None
    try:
        lat = [safe_div(x[0], x[1]) if isinstance(x, tuple) else float(x) for x in gps_info[2]]
        lon = [safe_div(x[0], x[1]) if isinstance(x, tuple) else float(x) for x in gps_info[4]]
        latitude = lat[0] + (lat[1] / 60.0) + (lat[2] / 3600.0)
        longitude = lon[0] + (lon[1] / 60.0) + (lon[2] / 3600.0)
        if gps_info.get(1) == 'S':
            latitude = -latitude
        if gps_info.get(3) == 'W':
            longitude = -longitude
        return {"latitude": latitude, "longitude": longitude}
    except Exception as e:
        print(f"Erreur GPS : {e}")
        return None

def get_dominant_colors(image_path, num_colors=3):
    img = cv2.imread(image_path)
    if img is None:
        return []
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (200, 200))
    pixels = img.reshape(-1, 3)
    kmeans = KMeans(n_clusters=num_colors, n_init=10, random_state=42).fit(pixels)
    return ["#{:02x}{:02x}{:02x}".format(int(r), int(g), int(b)) for r, g, b in kmeans.cluster_centers_]

def get_image_metadata(image_path):
    with Image.open(image_path) as img:
        exif_data = get_exif_data(img)
        gps_info = get_gps_info(exif_data)
        return {
            "format": img.format,
            "size": img.size,
            "mode": img.mode,
            "device": exif_data.get("Make", "Unknown") + " " + exif_data.get("Model", "Unknown"),
            "capture_date": exif_data.get("DateTimeOriginal", "Unknown"),
            "iso": exif_data.get("ISOSpeedRatings", "Unknown"),
            "focal_length": exif_data.get("FocalLength", "Unknown"),
            "exposure_time": exif_data.get("ExposureTime", "Unknown"),
            "gps": gps_info if gps_info else "No GPS Data"
        }

def process_images():
    annotations = {}

    for filename in df_images["image_filename"]:
        image_path = os.path.join(IMAGE_FOLDER, unquote(filename))

        if not os.path.exists(image_path):
            print(f"[!] Image non trouvée : {filename}")
            continue

        if os.path.getsize(image_path) > 50 * 1024 * 1024:
            print(f"[!] Image trop lourde : {filename}")
            continue

        try:
            dominant_colors = get_dominant_colors(image_path)
            metadata = get_image_metadata(image_path)

            # Mise à jour dans la base de données
            with engine.connect() as conn:
                conn.execute(
                    text("UPDATE images SET dominant_colors = :colors WHERE image_filename = :fname"),
                    {
                        "colors": ','.join(dominant_colors),  # convertit en chaîne "#aaa,#bbb,#ccc"
                        "fname": filename
                    }
                    print(f"[annotation] Mise à jour en base réussie pour {filename}")
)
            annotations[filename] = {
                "dominant_colors": dominant_colors,
                "metadata": metadata
            }
        except Exception as e:
            print(f"[!] Erreur sur {filename} : {e}")

    with open(ANNOTATION_FILE, "w", encoding="utf-8") as f:
        json.dump(annotations, f, indent=4, ensure_ascii=False)

    print(f"{len(annotations)} annotations générées.")

if __name__ == "__main__":
    process_images()
