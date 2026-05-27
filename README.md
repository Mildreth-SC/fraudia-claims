---

## Instalación y Ejecución

### Requisitos
- Python 3.12+
- R 4.6+
- Cuenta Supabase
- API Key Groq (gratuita)

### 1. Clonar repositorio
```bash
git clone https://github.com/tu-usuario/fraudia-claims.git
cd fraudia-claims
```

### 2. Instalar dependencias Python
```bash
pip install -r requirements.txt
```

### 3. Instalar dependencias R
```bash
Rscript -e "renv::restore()"
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 5. Generar dataset sintético
```bash
py -3.12 src/ingestion/load_data.py
```

### 6. Subir datos a Supabase
```bash
py -3.12 subir_supabase.py
```

### 7. Calcular scores
```bash
py -3.12 src/rules/fraud_rules.py
```

### 8. Generar gráficos R
```bash
Rscript src/features/graficos.R
```

### 9. Iniciar agente IA
```bash
py -3.12 src/ai_agent/claims_agent.py
```

### 10. Iniciar dashboard
```bash
py -3.12 src/app/main.py
```

---

## Casos de Uso

| Código | Caso | Descripción |
|--------|------|-------------|
| CU-01 | Cargar siniestros | Sistema valida estructura y procesa información |
| CU-02 | Calcular score | Cada siniestro recibe score 0-100 |
| CU-03 | Priorizar casos | Analista ve casos ordenados por riesgo |
| CU-04 | Explicar alerta | Sistema muestra factores de riesgo detectados |
| CU-05 | Consultar IA | Usuario obtiene respuestas en lenguaje natural |
| CU-06 | Generar reporte | Resumen ejecutivo de casos críticos |

---

## Score de Riesgo

| Rango | Nivel | Acción |
|-------|-------|--------|
| 0 - 19 | 🟢 VERDE | Flujo normal |
| 20 - 39 | 🟡 AMARILLO | Revisión documental |
| 40+ | 🔴 ROJO | Revisión especializada de campo |

---

## Principio Ético Clave
> La solución genera **alertas de revisión**, no acusaciones automáticas de fraude. Toda decisión final requiere revisión humana especializada.

---

## Equipo
hackIAthon 2026 — Reto Aseguradora del Sur
fraudia-claims/
├── README.md
├── requirements.txt
├── renv.lock
├── .env.example
├── data/
│   ├── raw/
│   ├── processed/
│   └── synthetic/
├── src/
│   ├── ingestion/load_data.py
│   ├── features/graficos.R
│   ├── rules/fraud_rules.py
│   ├── ai_agent/claims_agent.py
│   └── app/main.py
├── docs/
│   ├── arquitectura.md
│   ├── modelo_datos.md
│   ├── reglas_negocio.md
│   ├── uso_ia.md
│   └── limitaciones.md
├── tests/
│   └── test_rules.py
└── presentation/
└── pitch.pdf
 ---

## Instalación y Ejecución

### Requisitos
- Python 3.12+
- R 4.6+
- Cuenta Supabase
- API Key Groq (gratuita)

### 1. Clonar repositorio
```bash
git clone https://github.com/tu-usuario/fraudia-claims.git
cd fraudia-claims
```

### 2. Instalar dependencias Python
```bash
pip install -r requirements.txt
```

### 3. Instalar dependencias R
```bash
Rscript -e "renv::restore()"
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 5. Generar dataset sintético
```bash
py -3.12 src/ingestion/load_data.py
```

### 6. Subir datos a Supabase
```bash
py -3.12 subir_supabase.py
```

### 7. Calcular scores
```bash
py -3.12 src/rules/fraud_rules.py
```

### 8. Generar gráficos R
```bash
Rscript src/features/graficos.R
```

### 9. Iniciar agente IA
```bash
py -3.12 src/ai_agent/claims_agent.py
```

### 10. Iniciar dashboard
```bash
py -3.12 src/app/main.py
```

---

## Casos de Uso

| Código | Caso | Descripción |
|--------|------|-------------|
| CU-01 | Cargar siniestros | Sistema valida estructura y procesa información |
| CU-02 | Calcular score | Cada siniestro recibe score 0-100 |
| CU-03 | Priorizar casos | Analista ve casos ordenados por riesgo |
| CU-04 | Explicar alerta | Sistema muestra factores de riesgo detectados |
| CU-05 | Consultar IA | Usuario obtiene respuestas en lenguaje natural |
| CU-06 | Generar reporte | Resumen ejecutivo de casos críticos |

---

## Score de Riesgo

| Rango | Nivel | Acción |
|-------|-------|--------|
| 0 - 19 | 🟢 VERDE | Flujo normal |
| 20 - 39 | 🟡 AMARILLO | Revisión documental |
| 40+ | 🔴 ROJO | Revisión especializada de campo |

---

## Principio Ético Clave
> La solución genera **alertas de revisión**, no acusaciones automáticas de fraude. Toda decisión final requiere revisión humana especializada.

---

## Equipo
hackIAthon 2026 — Reto Aseguradora del Sur