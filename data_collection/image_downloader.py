import os
import argparse
import requests
from PIL import Image, ExifTags
from io import BytesIO
from tqdm import tqdm
from wikidata_utils import build_sparql_query, run_sparql_query

IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True)
HEADERS = {"User-Agent": "MassiveDataProject/1.0"}

def download_image(url, filename):
    try:
        response = requests.get(url, stream=True, timeout=10, headers=HEADERS)
        response.raise_for_status()
        image_path = os.path.join(IMAGE_DIR, filename)
        with open(image_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return image_path
    except Exception as e:
        print(f"[!] Erreur téléchargement {url} : {e}")
        return None

def get_image_metadata(image_path):
    metadata = {
        "format": None, "width": None, "height": None,
        "orientation": None, "capture_date": None, "device": None
    }
    try:
        with Image.open(image_path) as img:
            metadata["format"] = img.format
            metadata["width"], metadata["height"] = img.size
            metadata["orientation"] = (
                "portrait" if img.height > img.width
                else "landscape" if img.width > img.height
                else "square"
            )
            exif_data = img._getexif()
            if exif_data:
                exif = {ExifTags.TAGS.get(k, k): v for k, v in exif_data.items()}
                metadata["capture_date"] = exif.get("DateTimeOriginal")
                make = exif.get("Make", "")
                model = exif.get("Model", "")
                metadata["device"] = f"{make} {model}".strip()
    except Exception as e:
        print(f"[!] Erreur métadonnées {image_path} : {e}")
    return metadata

def process_images(start, end):
    query = build_sparql_query(limit=end)
    results = run_sparql_query(query)[start:end]

    for entry in tqdm(results, desc=f"Téléchargement {start}-{end-1}"):
        url = entry["image"]["value"]
        filename = os.path.basename(url).split("?")[0]
        local_path = download_image(url, filename)
        if local_path:
            get_image_metadata(local_path)  # Métadonnées analysées, mais pas affichées

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    args = parser.parse_args()

    process_images(args.start, args.end)
