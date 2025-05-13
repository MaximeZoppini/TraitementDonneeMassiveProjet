import os
import requests
import pandas as pd
from PIL import Image, ExifTags
from io import BytesIO
from tqdm import tqdm
from sqlalchemy import create_engine
from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME

# Configuration
SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
IMAGE_DIR = "/app/images"
HEADERS = {"User-Agent": "MassiveDataProject/1.0 (cmvilleroy@gmail.com)"}
TABLE_NAME = "images"

os.makedirs(IMAGE_DIR, exist_ok=True)

def build_sparql_query(limit=10):
    return f"""
    SELECT DISTINCT ?ville ?villeLabel ?pays ?paysLabel ?image WHERE {{
      ?ville wdt:P31 wd:Q1549591;
             wdt:P17 ?pays;
             wdt:P18 ?image.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "fr". }}
    }}
    LIMIT {limit}
    """

def run_sparql_query(query):
    response = requests.get(SPARQL_ENDPOINT, params={"query": query, "format": "json"}, headers=HEADERS)
    response.raise_for_status()
    return response.json()["results"]["bindings"]

def download_image(url, filename):
    try:
        response = requests.get(url, stream=True, timeout=10, headers=HEADERS)
        response.raise_for_status()
        image_path = os.path.join(IMAGE_DIR, filename)
        if not os.path.exists(image_path):
            with open(image_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        return image_path
    except Exception as e:
        print(f"[✘] Erreur téléchargement {url} : {e}")
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

def get_commons_metadata(file_url):
    filename = os.path.basename(file_url)
    api_url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": f"File:{filename}",
        "prop": "imageinfo",
        "iiprop": "timestamp|user|url|extmetadata"
    }
    try:
        response = requests.get(api_url, params=params, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        page = next(iter(data["query"]["pages"].values()))
        info = page.get("imageinfo", [{}])[0]
        meta = info.get("extmetadata", {})
        return {
            "author": meta.get("Artist", {}).get("value", ""),
            "license": meta.get("LicenseShortName", {}).get("value", ""),
            "description": meta.get("ImageDescription", {}).get("value", "")
        }
    except Exception as e:
        print(f"[!] Erreur Wikimedia metadata : {e}")
        return {
            "author": "", "license": "", "description": ""
        }

def process_images(limit=10):
    print(f"[→] Téléchargement de {limit} images et insertion dans la BDD.")
    query = build_sparql_query(limit)
    results = run_sparql_query(query)
    
    all_rows = []

    for entry in tqdm(results, desc="Traitement"):
        ville = entry["villeLabel"]["value"]
        pays = entry["paysLabel"]["value"]
        image_url = entry["image"]["value"]
        image_filename = os.path.basename(image_url).split("?")[0]

        local_path = download_image(image_url, image_filename)
        if local_path:
            exif_meta = get_image_metadata(local_path)
            commons_meta = get_commons_metadata(image_url)
            all_rows.append({
                "ville": ville,
                "pays": pays,
                "image_url": image_url,
                "image_filename": image_filename,
                "format": exif_meta["format"],
                "width": exif_meta["width"],
                "height": exif_meta["height"],
                "orientation": exif_meta["orientation"],
                "capture_date": exif_meta["capture_date"],
                "device": exif_meta["device"],
                "author": commons_meta["author"],
                "license": commons_meta["license"],
                "description": commons_meta["description"]
            })

    engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    df = pd.DataFrame(all_rows)
    # juste avant d’insérer dans la DB
    for col in df.select_dtypes(include='object'):
        df[col] = df[col].str.replace('\x00', '', regex=False)

    df.to_sql(TABLE_NAME, engine, if_exists="append", index=False)
    print(f"{len(df)} images insérées dans la table '{TABLE_NAME}'.")

# Lancement
if __name__ == "__main__":
    process_images(limit=10)
