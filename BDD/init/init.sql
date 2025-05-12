-- Création de la base de données si elle n'existe pas déjà
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_database
      WHERE datname = 'db_datamassive'
   ) THEN
      CREATE DATABASE db_datamassive;
   END IF;
END
$do$;

-- Connexion à la base et création de la table
\connect db_datamassive

CREATE TABLE IF NOT EXISTS images (
  id SERIAL PRIMARY KEY,
  filename TEXT NOT NULL,
  url TEXT,
  width INT,
  height INT,
  orientation TEXT,
  format TEXT,
  dominant_colors TEXT[],
  device TEXT,
  capture_date TEXT,
  iso TEXT,
  focal_length TEXT,
  exposure_time TEXT,
  gps JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

