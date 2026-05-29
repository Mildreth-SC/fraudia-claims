# Reglas de Negocio — Sistema de Alertas

## Score de Riesgo
El score va de 0 a 100. Se calcula sumando los puntos de cada señal detectada.

| Rango | Nivel | Acción |
|-------|-------|--------|
| 0 - 19 | VERDE | Flujo normal |
| 20 - 39 | AMARILLO | Revisión documental |
| 40+ | ROJO | Revisión especializada de campo |

> Nota: el PDF del reto sugiere umbrales 0–40 / 41–75 / 76–100; el prototipo usa la escala compacta anterior para la demo.

## Señales y Puntuación (RF-01 a RF-12)

| Código | Señal | Puntos |
|--------|-------|--------|
| RF-01 | Siniestro ≤ 10 días desde inicio póliza | 8 pts |
| RF-01b | Siniestro 11-30 días desde inicio póliza | 4 pts |
| RF-02 | Reporte tardío > 7 días | 5 pts |
| RF-02b | Reporte tardío 4-7 días | 3 pts |
| RF-03 | Asegurado con ≥ 3 siniestros en 18 meses | 8 pts |
| RF-03b | Asegurado con 2 siniestros en 18 meses | 4 pts |
| RF-04 | Documentos incompletos | 4 pts |
| RF-05 | Proveedor en lista restrictiva | 10 pts |
| RF-05b | Beneficiario con >2 siniestros en cartera | 5 pts |
| RF-06 | Monto reclamado ≥ 95% suma asegurada | 5 pts |
| RF-07 | Robo reportado con demora (24–48h / >48h) | 4 / 8 pts |
| RF-08 | Misma placa en 3+ siniestros | 6 pts |
| RF-08b | Alta frecuencia conductor (3+ siniestros vehiculares mismo asegurado) | 5 pts |
| RF-09 | Cobertura Responsabilidad Civil sola | 6 pts |
| RF-10 | Narrativa menciona huida o fuga | 5 pts |
| RF-11 | Documentación inconsistente | 8 pts |
| RF-12 | Narrativas muy similares (NLP) | 4 / 8 pts |

## Reglas Críticas Automáticas
- **RF-01 + RF-05 + RF-07 juntas** → clasificación ROJO inmediata (criterio de negocio)
- **Proveedor en lista restrictiva** → siempre escala a revisión

## Datos requeridos para RF vehicular
- Tabla `vehiculos` enlazada por `id_siniestro` (placa, marca, modelo)
- En CSV externos: columnas `placa` y/o `id_asegurado` + `ramo` = Vehiculos
