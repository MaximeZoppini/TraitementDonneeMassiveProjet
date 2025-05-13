import random
import pandas as pd
from sqlalchemy import create_engine
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from config import DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME

CLUSTER_FILE = "image_clusters_from_sql.csv"
USER_PROFILES_FILE = "user_profiles.json"

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

df = pd.read_sql("SELECT * FROM images", engine)

print("Images chargées :", len(df))

df["orientation_code"] = df["orientation"].map({
    "portrait": 0,
    "landscape": 1,
    "square": 2
})

# Extraire la couleur dominante 1
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

# On suppose que la colonne `dominant_colors` est disponible
def extract_first_rgb(color_string):
    try:
        if isinstance(color_string, str) and color_string.startswith("["):
            colors = eval(color_string)
        elif isinstance(color_string, list):
            colors = color_string
        else:
            return 0, 0, 0
        return hex_to_rgb(colors[0])
    except:
        return 0, 0, 0


def safe_rgb(color_str):
    try:
        colors = color_str.split(",")  # car on a enregistré "#a,#b,#c"
        rgb = [tuple(int(color[i:i+2], 16) for i in (1, 3, 5)) for color in colors]
        # moyenne des composantes RGB
        r = int(sum(c[0] for c in rgb) / len(rgb))
        g = int(sum(c[1] for c in rgb) / len(rgb))
        b = int(sum(c[2] for c in rgb) / len(rgb))
        return pd.Series([r, g, b])
    except Exception as e:
        print(f"[recommender] Erreur parsing RGB : {e} ({color_str})")
        return pd.Series([0, 0, 0])
    
    
df[["r", "g", "b"]] = df["dominant_colors"].apply(safe_rgb)

# Clustering
features = df[["width", "height", "orientation_code", "r", "g", "b"]].fillna(0)
X = StandardScaler().fit_transform(features)

kmeans = KMeans(n_clusters=5, n_init='auto', random_state=42)
df["cluster"] = kmeans.fit_predict(X)

df[["image_filename", "cluster"]].to_csv(CLUSTER_FILE, index=False)
print(f"Clustering terminé. Résultats dans {CLUSTER_FILE}")

# Génération de profils utilisateurs fictifs
def generate_users(df_images, num_users=5):
    image_keys = df_images["image_filename"].tolist()
    users = []

    for i in range(1, num_users + 1):
        row = df_images.sample(1).iloc[0]
        user = {
            "id": f"user_{i}",
            "preferred_colors": row["dominant_colors"],
            "preferred_format": row["format"],
            "preferred_orientation": row["orientation"],
            "liked_images": random.sample(image_keys, min(5, len(image_keys)))
        }
        users.append(user)

    return users

users = generate_users(df, num_users=5)

with open(USER_PROFILES_FILE, "w", encoding="utf-8") as f:
    import json
    json.dump(users, f, indent=4, ensure_ascii=False)

print(f"Profils utilisateurs générés dans {USER_PROFILES_FILE}")
