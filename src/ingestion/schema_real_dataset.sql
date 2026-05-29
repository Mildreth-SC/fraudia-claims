-- Ejecutar en Supabase SQL Editor antes de migrar dataset real
-- FraudIA hackIAthon 2026 - Aseguradora del Sur

-- Columnas nuevas en siniestros
ALTER TABLE siniestros ADD COLUMN IF NOT EXISTS placa_vehiculo text;
ALTER TABLE siniestros ADD COLUMN IF NOT EXISTS proveedor_restrictivo boolean DEFAULT false;
ALTER TABLE siniestros ADD COLUMN IF NOT EXISTS similitud_narrativa numeric;
ALTER TABLE siniestros ADD COLUMN IF NOT EXISTS numero_parte_policial text;
ALTER TABLE siniestros ADD COLUMN IF NOT EXISTS dias_desde_fin_poliza integer;
ALTER TABLE siniestros ADD COLUMN IF NOT EXISTS estado text;
ALTER TABLE siniestros ADD COLUMN IF NOT EXISTS sucursal text;

-- Tabla vehiculos (si no existe)
CREATE TABLE IF NOT EXISTS vehiculos (
  id_vehiculo TEXT PRIMARY KEY,
  id_siniestro TEXT NOT NULL,
  placa TEXT NOT NULL,
  chasis TEXT,
  motor TEXT,
  marca TEXT,
  modelo TEXT,
  anio INTEGER
);

CREATE INDEX IF NOT EXISTS idx_vehiculos_placa ON vehiculos(placa);
CREATE INDEX IF NOT EXISTS idx_vehiculos_siniestro ON vehiculos(id_siniestro);
CREATE INDEX IF NOT EXISTS idx_siniestros_placa ON siniestros(placa_vehiculo);
