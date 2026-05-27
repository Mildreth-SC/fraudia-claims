# Arquitectura del Sistema FraudIA

## Descripción General
FraudIA es un sistema híbrido de detección de posibles fraudes en siniestros de seguros que combina reglas de negocio, machine learning, NLP y un agente conversacional.

## Capas del Sistema

### Capa 1 — Datos (Supabase)
- Base de datos PostgreSQL en la nube
- 5 tablas: siniestros, polizas, asegurados, proveedores, documentos
- 1000 siniestros sintéticos, 600 pólizas, 400 asegurados, 3500+ documentos

### Capa 2 — Motor de Análisis (Python + R)
- Reglas de negocio RF-01 a RF-07
- Score ponderado 0-100
- Isolation Forest para detección de anomalías
- NLP para similitud entre narrativas
- Gráficos estadísticos con R/ggplot2

### Capa 3 — Agente IA (Groq + Llama 3.3)
- Consultas en lenguaje natural
- Explicación del score por caso
- Resúmenes ejecutivos automáticos

### Capa 4 — Frontend (Lovable + FastAPI)
- Dashboard visual nivel producción
- Semáforo ROJO/AMARILLO/VERDE
- Chat con el agente IA

## Stack Tecnológico
| Capa | Tecnología |
|------|-----------|
| Base de datos | Supabase (PostgreSQL) |
| Backend | Python + FastAPI |
| Análisis | scikit-learn, sentence-transformers |
| Visualización | R + ggplot2 |
| Agente IA | Groq API + Llama 3.3 70B |
| Frontend | Lovable |
| Despliegue | Google Cloud Run + Firebase |