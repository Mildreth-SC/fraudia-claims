-- Ejecutar en Supabase SQL Editor antes de subir_supabase.py
CREATE TABLE IF NOT EXISTS vehiculos (
  id_vehiculo TEXT PRIMARY KEY,
  id_siniestro TEXT NOT NULL REFERENCES siniestros(id_siniestro),
  placa TEXT NOT NULL,
  chasis TEXT,
  motor TEXT,
  marca TEXT,
  modelo TEXT,
  anio INTEGER
);

CREATE INDEX IF NOT EXISTS idx_vehiculos_placa ON vehiculos(placa);
CREATE INDEX IF NOT EXISTS idx_vehiculos_siniestro ON vehiculos(id_siniestro);
