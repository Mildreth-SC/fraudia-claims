# Limitaciones y Consideraciones Éticas

## Limitaciones Técnicas
- El dataset es 100% sintético — no representa patrones reales de fraude
- El score es referencial, no definitivo
- El modelo puede generar falsos positivos
- El agente depende de conectividad con API de Groq

## Consideraciones Éticas
- La solución genera ALERTAS DE REVISIÓN, no acusaciones de fraude
- Ninguna decisión automática de pago o rechazo
- Siempre se requiere revisión humana especializada
- No se usaron datos personales reales en ningún momento

## Sesgos Conocidos
- Dataset sintético puede no reflejar distribución real de fraudes
- Las reglas fueron calibradas para el contexto ecuatoriano
- El modelo no considera factores socioeconómicos

## Próximos Pasos para Producción
1. Entrenar con datos reales anonimizados
2. Calibrar umbrales con analistas expertos
3. Implementar monitoreo de drift del modelo
4. Auditoría externa del sistema antes de producción