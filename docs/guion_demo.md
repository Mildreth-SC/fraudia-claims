GUION DE DEMO - FRAUDIA HACKIATHON 2026
Duración total: 10 minutos
Datetime: Evento hackIAthon

==========================================
FASE 0: PRE-DEMO (5 minutos antes)
==========================================

1. Ejecutar script de verificación
   Comando: python test_api_demo.py
   Acción: Confirmar que 8/9 endpoints estén OK
   Si hay problema: Avisar a jurado que habrá 1 limitación

2. Abrir dos pantallas:
   Pantalla 1: Frontend en http://localhost:3000 (o URL desplegada)
   Pantalla 2: Notas del guión (este documento)

3. Tener lista:
   - Pregunta controlada para el agente IA
   - CSV test cargado en el panel
   - Datos backup en PDF

==========================================
MINUTO 0-1: PROBLEMA Y OPORTUNIDAD
==========================================

Pantalla: NEGRA / Solo voz

Decir: (60 segundos)

"Las aseguradoras pierden millones por fraudes no detectados.
Un analista revisa 50 casos por día. Manualmente. Con riesgo de error.

Nuestro reto: Usar Inteligencia Artificial para priorizar casos sospechosos
en segundos, no días. Generando alertas explicables que el analista revisa.

No acusamos. Alertamos. La decisión final es SIEMPRE humana."

Transición: Mostrar cursor sobre pantalla del navegador

==========================================
MINUTO 1-2: SOLUCIÓN
==========================================

Pantalla: NAVEGADOR - URL de FraudIA

Decir: (60 segundos)

"Aquí está FraudIA. Un sistema híbrido que:

1. CARGA siniestros: Se conecta a Supabase, lee datos en tiempo real
2. ANALIZA con 7 reglas de negocio + Machine Learning
3. GENERA score de riesgo Verde-Amarillo-Rojo
4. EXPLICA por qué cada caso es sospechoso
5. CHATEA en lenguaje natural gracias a IA

Todo en una plataforma integrada."

Acción: Pantalla queda en el Tab "Panel General" listo

==========================================
MINUTO 2-6: DEMO FUNCIONAL (4 MINUTOS)
==========================================

[PASO 1] PANEL GENERAL (30 segundos)
----------------------------------
Ubicación: Tab "Panel General"

Mostrar:
- Scroll arriba para ver KPIs
  - TOTAL SINIESTROS: 1000
  - ALERTAS ROJAS: 169 (16.9%)
  - ALERTAS AMARILLAS: 103 (10.3%)
  - SCORE PROMEDIO: 15.0
  
Decir: "Con 1000 siniestros, hemos identificado 169 casos ROJOS.
Sin nuestro sistema, el analista revisaría todos.
Con FraudIA, primero revisa los 169 riesgosos."

Acción: Scroll down para mostrar gráficos
- Pie chart de distribución riesgo
- Barras de score por ramo
Tiempo: 30 segundos


[PASO 2] TABLA DE CASOS SOSPECHOSOS (30 segundos)
----------------------------------------------
Ubicación: Tab "Casos Sospechosos"

Acción: 
1. Click en Tab "Casos Sospechosos"
2. Filter por "Solo Rojos" (button click)
3. Mostrar tabla con casos filtrados

Tabla debe mostrar:
- ID SINIESTRO
- NIVEL: ROJO (badge color rojo)
- SCORE: 48, 52, etc.
- RAMO
- CIUDAD
- ALERTAS

Decir: "Aquí vemos los casos ROJOS. Cada uno tiene un score
justificado. Ej: Score 48 porque:
- Siniestro a los 15 días de vigencia (+8)
- Reporte tardío (+5)
- Proveedor restrictivo (+10)
Total: 48 puntos = Rojo"

Acción: Hover sobre una alerta en la tabla para mostrar el tooltip

Tiempo: 30 segundos


[PASO 3] RANKING DE PROVEEDORES (45 segundos)
-------------------------------------------
Ubicación: Tab "Proveedores"

Acción:
1. Click en Tab "Proveedores"
2. Esperar a que cargue tabla

Tabla debe mostrar:
- PROVEEDOR (nombre)
- TOTAL ALERTAS (número)
- CRITICOS (Rojos)
- MEDIOS (Amarillos)
- MONTO TOTAL

Decir: "Ahora miramos los proveedores. Vemos que algunos
concentran más alertas que otros. Esto es anómalo.

Por ejemplo, el Taller X aparece en 25 casos rojos.
Eso requiere auditoría especializada.

Nuestro sistema identifica estas redes de riesgo
cruzando múltiples variables."

Acción: Click en el nombre del proveedor (si es clickeable, mostrar casos asociados)

Tiempo: 45 segundos


[PASO 4] AGENTE IA - CHAT (75 segundos)
---------------------------------------
Ubicación: Tab "Agente IA"

Acción:
1. Click en Tab "Agente IA"
2. Esperar a que cargue el chat
3. En el input, escribir LENTAMENTE la pregunta:

"¿Cuáles son los 5 proveedores con más alertas rojas?"

4. Presionar Enter
5. Esperar respuesta (máx 15 segundos)
6. Leer respuesta en voz alta (fragmentos)

Respuesta esperada (si funciona):
"Según el análisis de los datos, los 5 proveedores
con mayor concentración de alertas rojas son:
1. Taller X (25 casos ROJOS)
2. Clínica Y (18 casos ROJOS)
..."

Decir: "En lenguaje natural, preguntamos al sistema.
La IA analiza 1000 siniestros en segundos y responde.

Esto es lo que hace un analista en 2 horas,
nuestro sistema lo hace en 3 segundos."

Tiempo: 75 segundos


[PASO 5] PANEL DE ANÁLISIS (OPCIONAL si hay tiempo - 45 segundos)
---------
Ubicación: Tab "Analizar Dataset"

Acción:
1. Click en Tab "Analizar Dataset"
2. Mostrar el área de drag & drop
3. Si hay CSV test, arrastrarlo
4. Click en "Analizar"

Decir: "El analista puede cargar su PROPIO dataset.
CSV con cualquier estructura. Nuestro sistema:
1. Detecta columnas automáticamente
2. Limpia datos
3. Aplica el modelo
4. Genera reportes"

Mostrar: Los 3 reportes generados (si están listos)
- Cleaned data (CSV)
- Reporte de limpieza
- Alertas detalladas

Tiempo: 45 segundos (SOLO si está funcionando)


==========================================
MINUTO 6-8: ARQUITECTURA Y USO DE IA (2 MINUTOS)
==========================================

Pantalla: CAMBIAR a PDF/Imagen con Arquitectura

Decir: (2 minutos)

"Brevemente, la arquitectura:

DATOS: Supabase PostgreSQL en nube
BACKEND: FastAPI (Python) con 3 motores de IA
  - Reglas de negocio (7 señales)
  - Machine Learning (Isolation Forest para anomalías)
  - NLP (análisis de narrativas)
FRONTEND: React con gráficos interactivos
AGENTE IA: Groq + Claude para consultas

Todo gratuito, integrado, escalable.

Lo IMPORTANTE: Combinamos Reglas + ML + NLP + Agente.
No es pura caja negra. Cada alerta es explicable."

Acción: Mostrar diagrama por 2 minutos

Tiempo: 2 minutos


==========================================
MINUTO 8-9: IMPACTO Y NEGOCIO (1 MINUTO)
==========================================

Pantalla: TEXTO / SLIDE

Decir: (60 segundos)

"¿Por qué esto importa?

VELOCIDAD: De 2 horas analizando a 3 segundos.
PRECISIÓN: 169 casos ROJOS identificados de 1000.
AHORRO: Si cada caso revisado cuesta $100, recuperamos $16.900 en priorización.
CONFIABILIDAD: Sistema explicable que el analista ENTIENDE.

Para escalar:
- Deploy en Google Cloud Run (backend)
- Firebase Hosting (frontend)
- Integración con sistemas legacy de aseguradoras"

Tiempo: 60 segundos


==========================================
MINUTO 9-10: LIMITACIONES + PREGUNTAS (1 MINUTO)
==========================================

Decir: (60 segundos)

"Limitaciones actuales:

1. Dataset sintético (para hackathon)
2. 7 reglas de negocio (pueden ampliarse a 15+)
3. Sin análisis de documentos OCR (próxima fase)
4. Sin integración biométrica

Pero: El MVP funciona. El equipo está listo.
Y la arquitectura escala.

Preguntas del jurado..."

Acción: Abrir Q&A, estar listo para responder preguntas técnicas

Tiempo: 60 segundos


==========================================
PREGUNTAS ANTICIPADAS DEL JURADO
==========================================

P1: ¿Cómo detectan similitud de narrativas?
R: Usamos embeddings de text con sentence-transformers.
   Comparamos vectores con cosine similarity > 85%.

P2: ¿Por qué no acusan de fraude?
R: Ética y legal. Generamos alertas.
   Decisión final = Siempre humana.
   Evitamos falsos positivos que arruinen reputaciones.

P3: ¿Qué tan rápido es el sistema?
R: Score por siniestro: <100ms.
   Análisis de 1000 siniestros: <3 segundos.
   Chat con IA: <5 segundos promedio.

P4: ¿Cómo escala?
R: Supabase (auto-escalable).
   Cloud Run (serverless, pago por uso).
   Firebase (global CDN).

P5: ¿Qué datos usan?
R: Sintéticos. Cero PII.
   Faker library para generar datos realistas.
   Respetan GDPR y normativas.


==========================================
PLAN B: SI ALGO FALLA EN VIVO
==========================================

Falla: Frontend no carga
Solución: Mostrar PDF con screenshots de la UI
Fallback: Mostrar SQL queries en terminal con resultados

Falla: Groq/IA no responde
Solución: Mostrar respuesta pre-grabada
Fallback: Explicar con diapositiva el resultado esperado

Falla: Base de datos no disponible
Solución: Cargar datos desde archivo JSON local
Fallback: Mostrar datos en CSV en terminal

Falla: Gráficos no renderizan
Solución: Mostrar PNG pre-generados
Fallback: Explicar números verbalmente

Máxima falla: Sistema completamente caído
Solución: Mostrar video de 2 min del sistema funcionando
Fallback: Demo en código + explicación detallada

==========================================
NOTAS IMPORTANTES PARA EL EQUIPO
==========================================

1. LLEGAR 15 MIN ANTES
   - Probar conexión WiFi
   - Ejecutar test_api_demo.py
   - Confirmar que Frontend carga
   
2. TENER TODO EN PANTALLA LISTA
   - NO cambies tabs durante la demo
   - Todas las URLs abiertas
   - Chat ya escritas las preguntas

3. HABLAR CLARO Y LENTO
   - No técnico para audiencia general
   - Énfasis en el PROBLEMA y el IMPACTO
   - Demo es el 40% de la nota

4. TIMING ESTRICTO
   - Ensayar 3 veces antes
   - Cumplir 10 minutos exactos
   - Dejar 5 min para preguntas

5. CUERPO Y VOZ
   - Estar frente a la pantalla
   - Señalar con la mano lo importante
   - Voz de conversación, no monólogo

6. BACKUP DE TODA LA INFO
   - PDF con diapositivas
   - Video de demo funcionando
   - Código fuente en USB
   - Dataset en USB

==========================================
