# 🔐 Guía de Integración - Sistema de Login FraudIA

## Resumen de los Cambios

Se ha implementado un **sistema de autenticación profesional** con:
- ✅ Pantalla de login personalizada con branding Aseguradora del Sur
- ✅ Credenciales de demostración (hardcodeadas para hackathon)
- ✅ Protección de rutas - solo usuarios autenticados acceden al dashboard
- ✅ Muestra de usuario logueado en header + botón de logout
- ✅ Persistencia de sesión en localStorage

---

## Archivos Creados/Modificados

### ✅ Nuevos Archivos

**1. `frontend/src/lib/auth.ts`**
- Tipos y funciones de autenticación
- 3 credenciales de demostración hardcodeadas
- Validación de credenciales
- Persistencia en localStorage

**2. `frontend/src/components/fraudia/Login.tsx`**
- Componente visual profesional
- Formulario con email y contraseña
- Aviso de confidencialidad con ícono candado
- Mensaje de error rojo si credenciales inválidas
- Ejemplo de credenciales en footer

**3. `frontend/src/routes/login.tsx`**
- Nueva ruta `/login`
- Redirige al dashboard si ya estás logueado
- Llama a `Login.tsx`

### ✅ Archivos Modificados

**1. `frontend/src/routes/__root.tsx`**
```diff
+ Creó AuthContext para estado global
+ useAuth() hook para acceder a usuario/login/logout
+ Carga auth desde localStorage al iniciar
+ Estado de carga mientras se restaura sesión
```

**2. `frontend/src/routes/index.tsx`**
```diff
+ Import useAuth y useNavigate
+ Redirige a /login si no hay usuario
+ Extrae logout del contexto
+ Pasa user y onLogout al Header
+ Llama handleLogout() en botón
```

**3. `frontend/src/components/fraudia/Header.tsx`**
```diff
+ Props opcionales: user y onLogout
+ Muestra nombre del usuario (ej: "Analista Antifraude")
+ Muestra rol del usuario (ej: "analista")
+ Ícono de usuario en circulo
+ Botón "Salir" con icono LogOut
+ Responsive: rol oculto en mobile
```

---

## Credenciales de Demostración

```
USUARIO 1: Analista Antifraude
├─ Email:     analista@aseguradoradelsur.com
├─ Contraseña: FraudIA2026
└─ Rol:       analista

USUARIO 2: Administrador
├─ Email:     admin@aseguradoradelsur.com
├─ Contraseña: Admin2026
└─ Rol:       admin

USUARIO 3: Jurado Hackathon
├─ Email:     jurado@hackiathon.com
├─ Contraseña: Demo2026
└─ Rol:       jurado
```

---

## Flujo de Autenticación

```
Usuario llega a http://localhost:3000
        ↓
__root.tsx carga auth de localStorage
        ↓
¿Hay usuario en localStorage?
        ↓
        ├─ SÍ: Renderiza Dashboard (/index.tsx)
        │
        └─ NO: Redirige a /login
                ↓
                Login.tsx renderiza formulario
                ↓
                Usuario ingresa credenciales
                ↓
                auth.ts valida en DEMO_CREDENTIALS
                ↓
                ¿Credenciales correctas?
                ├─ SÍ: Guarda user en context + localStorage
                │      Redirige a dashboard
                │
                └─ NO: Muestra error en rojo
                       Usuario reintenta
```

---

## Componentes y Uso

### Auth Context (src/routes/__root.tsx)

```typescript
// Usar en cualquier componente
import { useAuth } from "@/routes/__root";

function MyComponent() {
  const { user, login, logout } = useAuth();
  
  if (!user) return <p>No autenticado</p>;
  
  return (
    <div>
      <p>Hola, {user.name}</p>
      <button onClick={logout}>Salir</button>
    </div>
  );
}
```

### Login Component

```typescript
// En routes/login.tsx
import { Login } from "@/components/fraudia/Login";
import { useAuth } from "./__root";

function LoginPage() {
  const { login } = useAuth();
  
  return <Login onLoginSuccess={login} />;
}
```

### Header Component

```typescript
// En routes/index.tsx
<FraudiaHeader 
  active={tab} 
  onTabChange={setTab}
  user={user}              // ← Nuevo
  onLogout={handleLogout}  // ← Nuevo
/>
```

---

## Detalles Visuales

### Pantalla de Login
```
┌─────────────────────────────────────────┐
│  Gradiente azul (#1B3A6B → #00AEEF)    │
│                                         │
│  [Logo Aseguradora del Sur]             │
│  FraudIA                                │
│  Sistema Antifraude                     │
│  Acceso exclusivo para analistas        │
│                                         │
│  ⚠️  Información Confidencial           │
│  El acceso no autorizado está prohibido │
│                                         │
│  Usuario: [___________________]         │
│  Contraseña: [___________________]      │
│                                         │
│  [    Iniciar Sesión    ]               │
│                                         │
│  Credenciales demo:                     │
│  • analista@...  /  FraudIA2026         │
│  • admin@...     /  Admin2026           │
│  • jurado@...    /  Demo2026            │
│                                         │
│  © Aseguradora del Sur                  │
└─────────────────────────────────────────┘
```

### Header después de Login
```
┌──────────────────────────────────────────────────────────┐
│ [Logo] FraudIA                    [Usuario] [Salir]      │
│ Sistema de Detección... Aseguradora del Sur             │
├──────────────────────────────────────────────────────────┤
│ [ Panel General ] [ Casos ] [ Proveedores ] [ IA ] [ Datos ]
└──────────────────────────────────────────────────────────┘
        ↑                                         ↑
    Logo del sistema                     Nombre + rol + botón logout
```

---

## Estados y Manejo de Errores

### Credenciales Inválidas
```
┌─────────────────────────┐
│ ⚠️ Credenciales inválidas│
│ Intente de nuevo        │
└─────────────────────────┘
```
- Mensaje rojo en el formulario
- Campo de contraseña se limpia
- Botón deshabilitado si campos vacíos

### Loading
```
Validando...  (durante validación de 500ms)
```

### Restauración de Sesión
```
┌─────────────────────┐
│ ⏳ Cargando...       │
└─────────────────────┘
(mientras se carga auth de localStorage)
```

---

## Seguridad (Hackathon)

⚠️ **IMPORTANTE**: 

Este es un sistema de **DEMO PARA HACKATHON**:
- Credenciales están **hardcodeadas** en el código
- No hay encriptación de contraseña
- Sesión se guarda en **localStorage** (no seguro en producción)

**Para producción**, implementar:
- Backend con JWT tokens
- Hashing bcrypt de contraseñas
- Sesiones seguras (httpOnly cookies)
- Rate limiting
- Autenticación de 2 factores
- Auditoría de accesos

---

## Testing

### Test 1: Login correcto
1. Ir a http://localhost:3000
2. Entra a /login automáticamente
3. Ingresa: `analista@aseguradoradelsur.com` / `FraudIA2026`
4. Click "Iniciar Sesión"
5. ✓ Redirige a dashboard
6. ✓ Muestra "Analista Antifraude" en header

### Test 2: Logout
1. En el dashboard, click botón "Salir"
2. ✓ Vuelve a /login
3. ✓ localStorage se limpia
4. Recarga página
5. ✓ Sigue en /login (sesión terminada)

### Test 3: Credenciales inválidas
1. En /login, ingresa email/password incorrectos
2. ✓ Muestra error en rojo
3. ✓ Password se limpia
4. ✓ Puedes reintentar

### Test 4: Persistencia
1. Login exitoso
2. Recarga la página (F5)
3. ✓ No redirige a /login
4. ✓ Dashboard sigue mostrando usuario

---

## Próximos Pasos (Opcional)

Si quieres mejorar el sistema:

1. **Agregar validaciones**
   - Email válido (regex)
   - Contraseña mínimo 6 caracteres
   - Mostrar/ocultar password

2. **Mejorar UX**
   - Presionar Enter para submit
   - Auto-focus en email
   - Recordar último usuario

3. **Agregar roles**
   - Diferentes permisos por rol
   - Tabs habilitados/deshabilitados por rol
   - Ocultar ciertos datos según rol

4. **Integrar backend real**
   - POST /auth/login
   - JWT tokens
   - Refresh tokens

---

**Status**: ✅ Completamente implementado
**Testing**: ✅ Listo para usar
**Producción**: ⚠️ Revisar seguridad antes de usar en producción
