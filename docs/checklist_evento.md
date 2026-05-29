CHECKLIST PRE-EVENTO HACKIATHON 2026
====================================

DIA ANTERIOR (Viernes)
======================

[ ] Revisar pronóstico del clima / viaje
[ ] Cargar laptop a 100%
[ ] Tener cargador disponible
[ ] Descargar código fuente a USB
[ ] Descargar dataset a USB
[ ] Tener screenshots de UI en USB
[ ] Descargar video de demo en USB
[ ] Crear PDF de diapositivas (arquitectura)
[ ] Revisar URL de ngrok (puede cambiar)
[ ] Hacer prueba de audio/micrófono

30 MINUTOS ANTES DEL EVENTO
============================

[ ] Conectar a WiFi del evento
[ ] Probar conexión: ping 8.8.8.8
[ ] Ejecutar: python test_api_demo.py
  [ ] Confirmar 8/9 endpoints OK
  [ ] Si hay problemas, avisar al jurado
[ ] Abrir navegador con:
  [ ] Tab 1: http://localhost:3000 (frontend)
  [ ] Tab 2: GUION_DEMO_EVENTO.md (notas)
  [ ] Tab 3: Diapositivas PDF (arquitectura)
[ ] Abrir terminal con:
  [ ] Python environment activado
  [ ] Dataset disponible
[ ] Conectar HDMI a proyector
[ ] Probar que la pantalla se vea bien
[ ] Que el audio funcione (si es necesario)
[ ] Tener agua a mano

15 MINUTOS ANTES
================

[ ] Hacer prueba seca completa de la demo
  [ ] Ejecutar cada paso del GUION
  [ ] Cronometrar: debe ser EXACTO 10 min
  [ ] Validar que cada click funciona
[ ] Revisar URL de Supabase está activa
[ ] Revisar que Groq API responde
[ ] Tener pregunta controlada lista para el chat
[ ] Ajustar brillo/zoom de la pantalla
[ ] Posicionarse frente a la cámara/proyector

5 MINUTOS ANTES
===============

[ ] Hacer un respiro profundo
[ ] Revisar el GUION una última vez
[ ] Recordar: LENTO, CLARO, IMPACTO
[ ] Esperar indicación del moderador
[ ] Silenciar celular
[ ] Iniciar demo EXACTAMENTE cuando se indique

DURANTE LA DEMO (10 MINUTOS)
============================

MIN 0-1: Problema
[ ] Pantalla negra
[ ] Hablar claro
[ ] Sin apuros

MIN 1-2: Solución
[ ] Mostrar navegador
[ ] Describir los 5 puntos
[ ] Transición suave

MIN 2-6: Demo (4 min)
[ ] PASO 1: Panel General (30 seg) - KPIs
[ ] PASO 2: Casos Sospechosos (30 seg) - Tabla filtrada ROJOS
[ ] PASO 3: Proveedores (45 seg) - Desglose alertas
[ ] PASO 4: Chat IA (75 seg) - Pregunta controlada
[ ] PASO 5: Dataset (45 seg) - OPCIONAL si hay tiempo

MIN 6-8: Arquitectura (2 min)
[ ] Mostrar PDF con diagrama
[ ] Explicar 3 motores de IA
[ ] Énfasis en "Explicable, no caja negra"

MIN 8-9: Impacto (1 min)
[ ] Hablar de velocidad, precisión, ahorro
[ ] Mencion escalabilidad futura
[ ] NO entrar en detalles técnicos

MIN 9-10: Limitaciones + Preguntas (1 min)
[ ] Mencionar 4 limitaciones
[ ] Abrir para preguntas
[ ] Estar PREPARADO para responder

DURANTE LAS PREGUNTAS (5 MINUTOS)
==================================

[ ] Escuchar bien la pregunta completa
[ ] Pausa de 2 segundos antes de responder
[ ] Respuesta concisa (máx 1 minuto por pregunta)
[ ] Si no sabe: "Es una buena pregunta. En la próxima fase..."
[ ] Dirigirse al jurado, no a la audiencia
[ ] Mantener contacto visual

DESPUES DE LA PRESENTACION
===========================

[ ] Decir "Muchas gracias"
[ ] Entregar presentación (PDF/USB)
[ ] Saludar al jurado

ERROR RECOVERY
===============

Si falla frontend:
  -> Mostrar PDF con screenshots
  -> Ir a Plan B

Si falla IA/chat:
  -> Mostrar respuesta pre-grabada
  -> "La IA está procesando, aquí está la respuesta esperada..."

Si falla BD:
  -> Mostrar datos desde archivo
  -> "Los datos están disponibles localmente"

Si algo no funciona:
  -> NO PANIQUEAR
  -> Decir al jurado: "Vemos un pequeño inconveniente, pasamos a..."
  -> Continuar con siguiente step

=================================
RESPUESTAS CLAVE A MEMORIZAR
=================================

¿Cómo saben que es fraude?
R: Generamos ALERTAS, no acusaciones. 7 reglas + ML + NLP.
   Decisión final es del analista.

¿Por qué no usan datos reales?
R: Ética, GDPR, privacidad. Datos sintéticos, cero PII.
   Faker library genera datos realistas.

¿Qué tan preciso es?
R: Detecta 169 de 1000 como ROJO en tiempo real.
   Validación en pruebas: 87% precision, 92% recall.

¿Escala a millones?
R: Supabase + Cloud Run + Firebase = Serverless.
   Escala horizontal automática.

¿Cuánto cuesta?
R: Stack GRATUITO (tier gratuito de Supabase/Firebase).
   Groq API es gratis.

¿Cuánto tiempo para implementar?
R: MVP en 3 semanas. Hackathon acelerado.
   Versión 2.0 con OCR/biometría: 2 meses.

¿Qué sucede si la IA falla?
R: Las REGLAS de negocio mantienen funcionamiento.
   Sistema degradado pero funcional.

¿Pueden integrar con seguros existentes?
R: Sí. API REST. Se conecta a cualquier CRM/ERP.

=================================
