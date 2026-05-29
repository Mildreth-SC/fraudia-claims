# 🚀 Guía Rápida - Cómo Ejecutar FraudIA

## ⚙️ Requisitos Previos

Asegúrate de tener instalado:
- ✅ **Python 3.12+** → https://www.python.org/downloads/
- ✅ **Node.js 18+** → https://nodejs.org/

## 🎯 Opción 1: Scripts Automáticos (Recomendado - Windows)

### Terminal 1 - Backend
```powershell
cd c:\Users\guano\OneDrive\Documentos\Reto_aseguradora
.\run_backend.bat
```

Deberías ver:
```
Iniciando backend en http://127.0.0.1:8000
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Terminal 2 - Frontend
```powershell
cd c:\Users\guano\OneDrive\Documentos\Reto_aseguradora
.\run_frontend.bat
```

Deberías ver:
```
VITE v... ready in ... ms

➜  Local:   http://127.0.0.1:3000/
```

## 🎯 Opción 2: Comandos Manuales (Si los scripts no funcionan)

### Terminal 1 - Backend

**Paso 1: Instalar dependencias**
```bash
cd c:\Users\guano\OneDrive\Documentos\Reto_aseguradora
python -m pip install --upgrade pip
python -m pip install fastapi uvicorn python-multipart pandas scikit-learn groq python-dotenv supabase-py
```

**Paso 2: Ejecutar servidor**
```bash
python src/app/main.py
```

### Terminal 2 - Frontend

**Paso 1: Instalar dependencias npm**
```bash
cd frontend
npm install
```

**Paso 2: Ejecutar servidor Vite**
```bash
npm run dev
```

## ✅ Verificación

### Backend funcionando:
```
http://127.0.0.1:8000
```
→ Deberías ver: `{"sistema":"FraudIA","version":"1.0.0","estado":"activo"}`

### Frontend funcionando:
```
http://127.0.0.1:3000
```
→ Deberías ver: Pantalla de login

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

## 📊 Gráficos

Una vez logueado, ve a **"Panel General"** para ver los 4 gráficos:

1. ✅ **Distribución por Riesgo** (DONUT)
2. ✅ **Score por Ramo** (BARRAS)
3. ✅ **Top Proveedores** (BARRAS HORIZONTALES)
4. ✅ **Alertas por Ciudad** (BARRAS APILADAS)

Los gráficos cargarán datos reales del endpoint `/casos?limit=1000`

## 🐛 Solución de Problemas

### Problema: "No module named 'fastapi'"

**Solución:**
```bash
# Asegúrate de que estás usando la ruta correcta de Python
python --version  # Debe mostrar 3.12+

# Instala FastAPI explícitamente
python -m pip install fastapi
```

### Problema: "npm: command not found"

**Solución:**
- Instala Node.js desde https://nodejs.org/
- Reinicia la terminal
- Verifica: `node --version` y `npm --version`

### Problema: "Error cargando datos" en gráficos

**Verificar:**
1. ✅ Backend está corriendo (`http://127.0.0.1:8000` accesible)
2. ✅ Endpoint `/casos` responde: `curl http://127.0.0.1:8000/casos -H "ngrok-skip-browser-warning: true"`
3. ✅ Frontend conecta a URL correcta en `frontend/src/lib/fraudia-api.ts`

### Problema: "Puerto 3000 ya está en uso"

**Solución:**
```bash
# Cambia el puerto en vite.config.ts
# O termina el proceso:
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

## 📝 Estructura de Carpetas

```
c:\Users\guano\OneDrive\Documentos\Reto_aseguradora\
├── run_backend.bat       ← ✨ Ejecuta backend
├── run_frontend.bat      ← ✨ Ejecuta frontend
├── src/
│   ├── app/main.py       ← Backend FastAPI
│   └── analysis/
│       └── data_cleaner.R
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── routes/
│       │   ├── __root.tsx
│       │   ├── index.tsx
│       │   └── login.tsx
│       └── components/fraudia/
│           ├── Charts.tsx      ← ✨ Gráficos Recharts
│           ├── Login.tsx
│           └── ...
└── requirements.txt
```

## 🎉 ¡Listo!

Una vez que ambos servidores estén corriendo:
1. Abre http://127.0.0.1:3000
2. Ingresa con cualquier credencial de demo
3. Navega a "Panel General"
4. ¡Disfruta de los gráficos en tiempo real!

---

**¿Aún hay problemas?** Asegúrate de:
- ✓ Cierre todas las ventanas del terminal anterior
- ✓ Abre PowerShell NUEVO como Administrador
- ✓ Navega a la carpeta correcta
- ✓ Ejecuta los scripts
