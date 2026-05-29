# FraudIA — Pitch hackIAthon 2026
## Reto Aseguradora del Sur (10 min)

---

## 1. Problema y oportunidad (1 min)

- Miles de siniestros al mes; revision manual lenta y costosa.
- Fraudes no detectados a tiempo generan pagos indebidos.
- Oportunidad: priorizar casos de alto riesgo antes del pago.

---

## 2. Solucion FraudIA (1 min)

- Dashboard con semaforo ROJO / AMARILLO / VERDE.
- Motor hibrido: **12 reglas de negocio** + **Isolation Forest** (AUC-ROC 0.88).
- Agente IA (Groq + Llama 3.3) para consultas en espanol.
- Principio etico: **alertas de revision, no acusaciones automaticas**.

---

## 3. Demo funcional (4 min)

1. Login corporativo (`jurado@hackiathon.com` / `Demo2026`)
2. Panel General: KPIs + ahorro potencial 30% en casos ROJOS
3. Click en caso critico: explicacion de reglas + vehiculo/placa
4. Graficos Recharts por ramo, proveedor, ciudad
5. Agente IA: "Cuales son los 10 casos mas criticos?"
6. Analizar Dataset: subir CSV + consola SQL

---

## 4. Arquitectura e IA (2 min)

```
Excel/CSV -> Supabase -> FastAPI -> React Dashboard
                |            |
           Reglas RF    Groq Chat
                |            |
         Isolation Forest + NLP similitud narrativas
```

- Datos: 500 siniestros reales + documentos + vehiculos
- Explicabilidad: cada score desglosado por regla activa
- ML complementa reglas; no reemplaza al analista humano

---

## 5. Impacto de negocio (1 min)

- Monto expuesto en casos ROJOS visible en dashboard
- Ahorro potencial estimado: **30%** si se detecta antes del pago
- Priorizacion: top 10 casos por score para revision de campo

---

## 6. Limitaciones y proximos pasos (1 min)

- Prototipo; umbrales calibrables con historico real
- Integracion con core de siniestros y workflow de ajustadores
- OCR sobre PDFs (facturas, partes policiales)
- Metricas F1 en produccion con etiquetas confirmadas

---

**Equipo FraudIA — Aseguradora del Sur — hackIAthon 2026**

Exportar a PDF: abrir en VS Code / Typora / Google Docs -> Imprimir -> Guardar como PDF -> `presentation/pitch.pdf`
