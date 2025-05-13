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
DROP TABLE IF EXISTS images;

CREATE TABLE IF NOT EXISTS images (
  id SERIAL PRIMARY KEY,
  ville TEXT,
  pays TEXT,
  image_url TEXT,
  image_filename TEXT,
  format TEXT,
  width INT,
  height INT,
  orientation TEXT,
  capture_date TEXT,
  device TEXT,
  author TEXT,
  license TEXT,
  description TEXT,
  dominant_colors TEXT[],
  iso TEXT,
  focal_length TEXT,
  exposure_time TEXT,
  gps JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE images 
ALTER COLUMN dominant_colors TYPE TEXT;