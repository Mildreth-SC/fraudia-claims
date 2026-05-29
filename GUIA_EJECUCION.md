# 🚀 Guía Rápida - Cómo Ejecutar FraudIA

## ⚙️ Setup Inicial (Solo Primera Vez)

**Paso 1: Cierra todas las PowerShell abiertas**

**Paso 2: Abre PowerShell como Administrador**

**Paso 3: Ejecuta setup:**
```powershell
cd c:\Users\guano\OneDrive\Documentos\Reto_aseguradora
.\setup.bat
```

Este script:
✓ Verifica Python 3.12+  
✓ Instala todas las dependencias Python  
✓ Instala todas las dependencias npm  

**Espera a que termine y presiona Enter**

---

## 🎯 Ejecutar FraudIA (Después del Setup)

### Terminal 1 - Backend
```powershell
cd c:\Users\guano\OneDrive\Documentos\Reto_aseguradora
.\start_backend.bat
```

Deberías ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Terminal 2 - Frontend
```powershell
cd c:\Users\guano\OneDrive\Documentos\Reto_aseguradora\frontend
npm run dev
```

Deberías ver:
```
➜  Local:   http://127.0.0.1:3000/
```

### Terminal 3 - Abrir navegador
```
http://localhost:3000
```

---

## 🔐 Login

Usa cualquiera de estas credenciales:

```
📧 analista@aseguradoradelsur.com
🔑 FraudIA2026

📧 admin@aseguradoradelsur.com
🔑 Admin2026

📧 jurado@hackiathon.com
🔑 Demo2026
```

---

## 📊 Ver Gráficos

Una vez logueado:
1. Click en tab **"Panel General"**
2. Verás 4 gráficos Recharts con datos reales:
   - ✅ Distribución por Riesgo (DONUT)
   - ✅ Score por Ramo (BARRAS)
   - ✅ Top Proveedores (BARRAS HORIZONTALES)
   - ✅ Alertas por Ciudad (BARRAS)

---

## ⚠️ Si el backend no funciona

**Problema:** `No module named 'fastapi'`

**Solución - Opción A (Manual):**
```powershell
# Abre PowerShell como Administrador
$python = "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps\python3.12.exe"
& $python -m pip install fastapi uvicorn python-multipart pandas scikit-learn groq python-dotenv supabase-py
& $python c:\Users\guano\OneDrive\Documentos\Reto_aseguradora\src\app\main.py
```

**Solución - Opción B (Si nada funciona):**
1. Desinstala Python completamente
2. Instala desde: https://www.python.org/downloads/
3. **IMPORTANTE**: Marca "Add Python to PATH" durante instalación
4. Reinicia tu computadora
5. Ejecuta `setup.bat` nuevamente

---

## 🎉 ¿Ya funciona?

Deberías ver en el navegador:
- Pantalla de login profesional
- Después del login: Dashboard con gráficos
- Datos actualizados en tiempo real

**Listo! ✓**

---

## 📞 Soporte Rápido

| Problema | Solución |
|----------|----------|
| "Python no encontrado" | Ejecuta `setup.bat` |
| "No module named 'fastapi'" | Ejecuta `setup.bat` |
| "npm not found" | Instala Node.js de nodejs.org |
| "Puerto 3000 ocupado" | Cambia puerto en `vite.config.ts` |
| "Error cargando datos" | Verifica backend está corriendo |


