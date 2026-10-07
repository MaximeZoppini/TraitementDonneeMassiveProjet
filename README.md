<h1 align="center">🖼️ Traitement de données massives — Pipeline d'images & IA</h1>

<p align="center">
  <strong>De la collecte automatisée d'images à la recommandation personnalisée : un pipeline de données complet, du téléchargement parallélisé jusqu'aux modèles de machine learning.</strong><br>
  <em>Projet du module d'initiation à l'IA et au traitement de données massives — CPE Lyon</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/scikit--learn-F7931E?logo=scikitlearn&logoColor=white" alt="scikit-learn">
  <img src="https://img.shields.io/badge/OpenCV-5C3EE8?logo=opencv&logoColor=white" alt="OpenCV">
  <img src="https://img.shields.io/badge/pandas-150458?logo=pandas&logoColor=white" alt="pandas">
  <img src="https://img.shields.io/badge/Jupyter-F37626?logo=jupyter&logoColor=white" alt="Jupyter">
  <img src="https://img.shields.io/badge/Wikidata-SPARQL-006699?logo=wikidata&logoColor=white" alt="Wikidata">
</p>

---

## Objectif

Construire de bout en bout une chaîne de traitement de données sur un jeu d'images réelles :

1. **Collecter** des images libres de droits depuis Wikidata / Wikimedia Commons, en parallèle
2. **Stocker** les fichiers et leurs métadonnées dans une base PostgreSQL
3. **Annoter** automatiquement chaque image (couleurs dominantes, métadonnées EXIF, GPS)
4. **Analyser et visualiser** le jeu de données
5. **Entraîner des modèles** : classification supervisée et clustering non supervisé
6. **Recommander** des images à des utilisateurs selon leurs préférences

## Pipeline

```
 Wikidata (SPARQL)
        │
        ▼
 scheduler.py ──► N conteneurs Docker `image_downloader` en parallèle
                       │  téléchargement + métadonnées (Exif, Commons)
                       ▼
          images/  +  PostgreSQL (table `images`)
                       │
                       ▼
 annotation/   ── couleurs dominantes (KMeans sur les pixels, OpenCV) + EXIF + GPS ──► annotations.json
                       │
          ┌────────────┼──────────────────────────┐
          ▼            ▼                          ▼
 visualization/   visualization/            recommender/
 statistiques     data_analysis :           profils utilisateurs simulés
 et graphiques    RandomForest + KMeans     + filtrage par le contenu
```

## Étapes en détail

### 1. Collecte distribuée — `data_collection/`, `scheduler.py`
- Requête **SPARQL** sur Wikidata pour obtenir des URL d'images Wikimedia Commons.
- Le `scheduler.py` découpe la liste en plages et lance **plusieurs conteneurs Docker en parallèle** ; chaque worker télécharge sa plage d'images.
- Les métadonnées (format, dimensions, orientation, date de capture, appareil) sont extraites avec Pillow puis insérées dans **PostgreSQL** via SQLAlchemy.

### 2. Annotation automatique — `annotation/generate_annotations.ipynb`
- **Couleurs dominantes** : les pixels de chaque image sont regroupés par **KMeans** ; les centres des clusters donnent la palette de l'image (codes hexadécimaux).
- **Métadonnées EXIF** : appareil, date, ISO, exposition, focale, et coordonnées **GPS** converties en latitude / longitude.
- Les images trop volumineuses ou illisibles sont écartées. Le résultat est un fichier `annotations.json` qui alimente toutes les étapes suivantes.

### 3. Visualisation — `visualization/visualization.ipynb`
Analyse descriptive du dataset avec pandas, Matplotlib et Seaborn : répartition des formats, orientations et tailles, couleurs les plus fréquentes, appareils utilisés.

### 4. Apprentissage automatique — `visualization/data_analysis.ipynb`
- **Classification supervisée** : un **RandomForest** prédit l'orientation d'une image (paysage / portrait) à partir de ses couleurs dominantes, avec rapport de classification (précision, rappel, F1).
- **Clustering non supervisé** : un **KMeans** sur la couleur moyenne regroupe les images par style visuel, sans étiquette préalable.

### 5. Recommandation — `recommender/`
- `user_profile.ipynb` génère des **profils utilisateurs** fictifs (couleurs, orientations et tailles préférées).
- `recommender.ipynb` implémente un **filtrage basé sur le contenu** : chaque image est comparée au profil de l'utilisateur pour lui proposer les plus pertinentes.

## Lancer le projet

### Prérequis
- Docker et Docker Compose
- Python 3 et Jupyter (pour les notebooks)

### 1. Démarrer l'infrastructure

```bash
docker compose up -d
```

Cette commande crée le réseau `backend` et lance :
- **PostgreSQL** (`postgres-db`, base `db_datamassive`)
- **pgAdmin** : http://localhost:5050
- l'image **`image_downloader`**, prête à être lancée par le scheduler
- une petite **API Flask** : http://localhost:5080

### 2. Collecter les images

```bash
python scheduler.py
```

Le scheduler lance plusieurs conteneurs `image_downloader` (éphémères, `--rm`) qui se partagent le travail. Les images sont enregistrées dans `images/` (volume partagé) et leurs métadonnées dans PostgreSQL.

Vérification :

```bash
docker exec -it postgres-db psql -U user -d db_datamassive -c "SELECT * FROM images LIMIT 5;"
```

### 3. Exécuter les notebooks

Dans l'ordre : `annotation/` → `visualization/` → `recommender/` (`user_profile` puis `recommender`).

## Structure

```
├── data_collection/   # Worker de téléchargement (Dockerfile, requêtes Wikidata)
├── scheduler.py       # Orchestration des workers en parallèle
├── BDD/init/          # Script d'initialisation PostgreSQL
├── annotation/        # Couleurs dominantes + EXIF → annotations.json
├── visualization/     # Analyse descriptive, classification et clustering
├── recommender/       # Profils utilisateurs et recommandation
├── flask_api/         # Interface web minimale
├── docker-compose.yml
└── Villeroy Zoppini.pdf   # Rapport du projet
```

## Compétences mobilisées

Traitement parallèle et conteneurisation · requêtes SPARQL · ingestion en base relationnelle · extraction de caractéristiques d'images · apprentissage supervisé et non supervisé · système de recommandation · visualisation de données.

## Auteurs

- **Côme Villeroy de Galhau** — [@DayRob](https://github.com/DayRob)
- **Maxime Zoppini** — [@MaximeZoppini](https://github.com/MaximeZoppini)
