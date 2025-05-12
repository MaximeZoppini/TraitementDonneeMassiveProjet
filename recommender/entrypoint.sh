#!/bin/bash
set -e

echo "Attente de PostgreSQL à $DB_HOST:$DB_PORT..."
/app/wait-for-it.sh $DB_HOST:$DB_PORT --timeout=60 --strict -- python recommender.py

echo "Démarrage de recommender.py"
python /app/recommender.py
