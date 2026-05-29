# Modelo de Datos

## Tablas

### siniestros (tabla principal)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id_siniestro | text PK | Identificador único |
| id_poliza | text FK | Referencia a póliza |
| id_asegurado | text FK | Referencia a asegurado |
| ramo | text | Vehiculos, Salud, Hogar, Vida, Generales |
| cobertura | text | Choque, Robo, Incendio, etc |
| fecha_ocurrencia | date | Fecha del evento |
| fecha_reporte | date | Fecha de notificación |
| monto_reclamado | numeric | Valor solicitado |
| monto_estimado | numeric | Valor estimado aseguradora |
| monto_pagado | numeric | Valor pagado |
| descripcion | text | Narrativa libre del reclamo |
| documentos_completos | boolean | Indicador documentación |
| dias_desde_inicio_poliza | integer | Días entre inicio póliza y siniestro |
| etiqueta_fraude_simulada | integer | 0/1 para entrenamiento |

### vehiculos
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id_vehiculo | text PK | Identificador único |
| id_siniestro | text FK | Siniestro asociado (1:1 en datos sintéticos) |
| placa | text | Placa del vehículo |
| chasis | text | Número de chasis |
| motor | text | Número de motor |
| marca | text | Marca del vehículo |
| modelo | text | Modelo |
| anio | integer | Año del vehículo |

Script SQL: `src/ingestion/schema_vehiculos.sql`  
Datos: `data/synthetic/vehiculos.csv` (generado con `load_data.py`)

### polizas
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id_poliza | text PK | Identificador único |
| id_asegurado | text FK | Referencia a asegurado |
| ramo | text | Tipo de seguro |
| fecha_inicio | date | Inicio de vigencia |
| fecha_fin | date | Fin de vigencia |
| prima | numeric | Prima del seguro |
| suma_asegurada | numeric | Monto máximo cubierto |

### asegurados
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id_asegurado | text PK | Identificador único |
| segmento | text | Premium, Estandar, Basico |
| score_cliente_simulado | numeric | Score interno 300-900 |
| reclamos_ultimos_12_meses | integer | Historial reciente |

### proveedores
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id_proveedor | text PK | Identificador único |
| restrictivo | boolean | En lista restrictiva |
| porcentaje_casos_observados | numeric | % casos sospechosos |

### documentos
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id_documento | text PK | Identificador único |
| id_siniestro | text FK | Referencia a siniestro |
| inconsistencia_detectada | boolean | Alerta de inconsistencia |

## Campos derivados (pipeline)
| Campo | Origen |
|-------|--------|
| placa | Join con `vehiculos` |
| frecuencia_placa | Conteo de siniestros por placa |
| frecuencia_conductor | Siniestros vehiculares por `id_asegurado` |
| marca_vehiculo, modelo_vehiculo, anio_vehiculo | Join con `vehiculos` |
| doc_inconsistente | Agregado de `documentos` |
| similitud_narrativa | TF-IDF entre descripciones |
