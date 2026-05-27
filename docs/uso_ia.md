# Uso de Inteligencia Artificial

## Enfoque Híbrido
FraudIA combina 4 capas de IA:

### 1. Reglas de Negocio (Determinístico)
- 7 reglas RF implementadas según documento del reto
- Score ponderado por severidad de cada señal
- Trazable y explicable al 100%

### 2. Isolation Forest (ML No Supervisado)
- Detecta siniestros con comportamiento atípico
- Variables: monto, días, historial, ratio cobertura
- Complementa las reglas con anomalías no evidentes

### 3. NLP — Similitud de Narrativas
- Modelo: sentence-transformers (paraphrase-multilingual)
- Detecta narrativas clonadas o muy similares entre reclamos
- Umbral: >85% similitud = alerta de narrativa clonada

### 4. Agente Conversacional (Groq + Llama 3.3 70B)
- Responde preguntas en lenguaje natural en español
- Explica el score de cada caso
- Genera resúmenes ejecutivos
- Modelo open source, sin dependencia de APIs propietarias

## Métricas del Modelo
- Precision, Recall, F1-score sobre etiqueta_fraude_simulada
- AUC-ROC para el modelo supervisado
- % casos marcados por Isolation Forest
- Similitud textual promedio entre narrativas