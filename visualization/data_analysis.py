import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import classification_report
from sklearn.cluster import KMeans
from config import DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
df = pd.read_sql("SELECT image_filename, orientation, dominant_colors FROM images", engine)

df = df[df["dominant_colors"].notnull()]
df["colors"] = df["dominant_colors"].apply(lambda c: eval(c) if isinstance(c, str) else [])

df = df[df["colors"].map(len) > 0]

mlb = MultiLabelBinarizer()
X_colors = mlb.fit_transform(df["colors"])
y = df["orientation"]

X_train, X_test, y_train, y_test = train_test_split(
    X_colors, y, test_size=0.2, random_state=42, stratify=y
)

clf = RandomForestClassifier(random_state=42)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

print("\nRapport de classification :")
print(classification_report(y_test, y_pred))

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
df["cluster_rgb"] = kmeans.fit_predict(X_rgb)

print("\nClustering des couleurs moyennes :")
print(df["cluster_rgb"].value_counts().sort_index())
