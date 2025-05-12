import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from sqlalchemy import create_engine
from config import DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME
import numpy as np
from sklearn.cluster import KMeans

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
df = pd.read_sql("SELECT * FROM images", engine)

df["colors"] = df["dominant_colors"].apply(lambda c: eval(c) if isinstance(c, str) else [])

# ---------- GRAPHIQUES ----------

plt.figure(figsize=(6,4))
sns.countplot(data=df, x="format", order=df["format"].value_counts().index)
plt.title("Nombre d'images par format")
plt.savefig("output/images_par_format.png")
plt.close()

plt.figure(figsize=(6,4))
sns.countplot(data=df, x="orientation", order=df["orientation"].value_counts().index)
plt.title("Nombre d'images par orientation")
plt.savefig("output/images_par_orientation.png")
plt.close()

plt.figure(figsize=(6,4))
sns.scatterplot(data=df, x="width", y="height")
plt.title("Dimensions des images")
plt.savefig("output/dimensions.png")
plt.close()

all_colors = sum(df["colors"].tolist(), [])
color_counts = Counter(all_colors)
most_common = color_counts.most_common(10)

plt.figure(figsize=(8,4))
sns.barplot(x=[c[0] for c in most_common], y=[c[1] for c in most_common], palette=[c[0] for c in most_common])
plt.title("Couleurs dominantes les plus fréquentes")
plt.savefig("output/couleurs_dominantes.png")
plt.close()

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_average_rgb(colors):
    if not colors:
        return [0, 0, 0]
    rgbs = [hex_to_rgb(c) for c in colors]
    r = sum(rgb[0] for rgb in rgbs) / len(rgbs)
    g = sum(rgb[1] for rgb in rgbs) / len(rgbs)
    b = sum(rgb[2] for rgb in rgbs) / len(rgbs)
    return [r, g, b]

df["rgb_avg"] = df["colors"].apply(get_average_rgb)

X_rgb = np.array(df["rgb_avg"].tolist())
kmeans = KMeans(n_clusters=3, random_state=42)
df["cluster"] = kmeans.fit_predict(X_rgb)

plt.figure(figsize=(8,2))
for i, center in enumerate(kmeans.cluster_centers_):
    rgb_color = [int(c) for c in center]
    color_hex = '#%02x%02x%02x' % tuple(rgb_color)
    plt.subplot(1, 3, i+1)
    plt.imshow(np.ones((10,10,3), dtype=np.uint8) * np.array(rgb_color, dtype=np.uint8))
    plt.axis("off")
    plt.title(f"Cluster {i}\n{color_hex}")
plt.suptitle("Couleurs moyennes par cluster")
plt.savefig("output/clusters_rgb.png")
plt.close()
