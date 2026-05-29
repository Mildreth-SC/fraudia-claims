import { useEffect, useState } from "react";
import {
  AlertCircle,
  Eye,
  EyeOff,
  Loader2,
  Lock,
  Mail,
  Shield,
} from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import {
  validateCredentials,
  saveAuthToStorage,
  clearAuthFromStorage,
  loadAuthFromStorage,
  type User,
} from "@/lib/auth";

const REMEMBER_EMAIL_KEY = "fraudia_remember_email";

interface LoginProps {
  onLoginSuccess: (user: User) => void;
}

export function logout(): void {
  clearAuthFromStorage();
}

export function getLoggedInUserName(): string | null {
  const user = loadAuthFromStorage();
  return user?.name ?? null;
}

function FieldIcon({ children }: { children: React.ReactNode }) {
  return (
    <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
      {children}
    </span>
  );
}

export function Login({ onLoginSuccess }: LoginProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberEmail, setRememberEmail] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    try {
      const saved = localStorage.getItem(REMEMBER_EMAIL_KEY);
      if (saved) {
        setEmail(saved);
        setRememberEmail(true);
      }
    } catch {
      /* ignore */
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    await new Promise((resolve) => setTimeout(resolve, 400));

    const user = validateCredentials(email.trim(), password);

    if (!user) {
      setError("Credenciales incorrectas. Verifique su correo y contraseña.");
      setPassword("");
      setLoading(false);
      return;
    }

    try {
      if (rememberEmail) {
        localStorage.setItem(REMEMBER_EMAIL_KEY, email.trim());
      } else {
        localStorage.removeItem(REMEMBER_EMAIL_KEY);
      }
    } catch {
      /* ignore */
    }

    saveAuthToStorage(user);
    setLoading(false);
    onLoginSuccess(user);
  };

  return (
    <div
      className="relative flex min-h-screen items-center justify-center overflow-hidden p-4 sm:p-6"
      style={{
        background:
          "linear-gradient(145deg, #1B3A6B 0%, #15406f 45%, #00AEEF 100%)",
      }}
    >
      {/* Patron sutil de fondo */}
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.07]"
        style={{
          backgroundImage:
            "radial-gradient(circle at 1px 1px, white 1px, transparent 0)",
          backgroundSize: "28px 28px",
        }}
      />
      <div className="pointer-events-none absolute -left-24 -top-24 h-72 w-72 rounded-full bg-white/10 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-32 -right-16 h-96 w-96 rounded-full bg-[#00AEEF]/20 blur-3xl" />

      <div className="relative z-10 w-full max-w-[420px]">
        {/* Logo y marca */}
        <div className="mb-6 flex flex-col items-center text-center">
          <div className="mb-4 flex h-20 w-20 items-center justify-center rounded-2xl bg-white shadow-lg ring-1 ring-white/40">
            <img
              src="/logo.jpg"
              alt="Aseguradora del Sur"
              className="h-14 w-14 object-contain"
              onError={(e) => {
                e.currentTarget.style.display = "none";
              }}
            />
          </div>
          <p className="text-xs font-medium uppercase tracking-[0.2em] text-white/80">
            Aseguradora del Sur
          </p>
        </div>

        {/* Tarjeta de acceso */}
        <div className="overflow-hidden rounded-2xl bg-white shadow-2xl ring-1 ring-black/5">
          <div
            className="px-8 py-5 text-center text-white"
            style={{
              background: "linear-gradient(90deg, #1B3A6B 0%, #00AEEF 100%)",
            }}
          >
            <h1 className="text-2xl font-semibold tracking-tight">FraudIA</h1>
            <p className="mt-1 text-sm text-white/90">Sistema Antifraude</p>
          </div>

          <div className="px-8 py-7">
            <p className="mb-6 text-center text-sm text-muted-foreground">
              Ingrese sus credenciales corporativas para acceder al panel de analisis.
            </p>

            {error && (
              <Alert variant="destructive" className="mb-5">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <form onSubmit={handleSubmit} className="space-y-5" noValidate>
              <div className="space-y-2">
                <Label htmlFor="email" className="text-foreground">
                  Correo corporativo
                </Label>
                <div className="relative">
                  <FieldIcon>
                    <Mail className="h-4 w-4" aria-hidden />
                  </FieldIcon>
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="usuario@aseguradoradelsur.com"
                    autoComplete="username"
                    disabled={loading}
                    required
                    className="h-11 pl-10 text-sm"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="password" className="text-foreground">
                    Contraseña
                  </Label>
                </div>
                <div className="relative">
                  <FieldIcon>
                    <Lock className="h-4 w-4" aria-hidden />
                  </FieldIcon>
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Ingrese su contraseña"
                    autoComplete="current-password"
                    disabled={loading}
                    required
                    className="h-11 pr-11 pl-10 text-sm"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    disabled={loading}
                    className={cn(
                      "absolute right-1 top-1/2 flex h-9 w-9 -translate-y-1/2 items-center justify-center rounded-md",
                      "text-muted-foreground transition-colors hover:bg-muted hover:text-foreground",
                      "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#00AEEF]/50",
                      "disabled:pointer-events-none disabled:opacity-50",
                    )}
                    aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                    tabIndex={0}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" aria-hidden />
                    ) : (
                      <Eye className="h-4 w-4" aria-hidden />
                    )}
                  </button>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Checkbox
                  id="remember"
                  checked={rememberEmail}
                  onCheckedChange={(checked) => setRememberEmail(checked === true)}
                  disabled={loading}
                />
                <Label
                  htmlFor="remember"
                  className="cursor-pointer text-sm font-normal text-muted-foreground"
                >
                  Recordar mi correo en este equipo
                </Label>
              </div>

              <Button
                type="submit"
                disabled={loading || !email.trim() || !password}
                className="h-11 w-full text-sm font-semibold text-white shadow-md"
                style={{
                  background: "linear-gradient(90deg, #1B3A6B 0%, #00AEEF 100%)",
                }}
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Validando acceso...
                  </>
                ) : (
                  "Iniciar sesión"
                )}
              </Button>
            </form>

            <div className="mt-6 flex items-start gap-2.5 rounded-lg border border-border bg-muted/40 px-3 py-3">
              <Shield className="mt-0.5 h-4 w-4 shrink-0 text-[#1B3A6B]" aria-hidden />
              <p className="text-xs leading-relaxed text-muted-foreground">
                Sistema de uso interno. Acceso autorizado únicamente para personal
                de Aseguradora del Sur. Toda actividad queda registrada.
              </p>
            </div>
          </div>
        </div>

        <p className="mt-5 text-center text-xs text-white/70">
          Hackathon 2026 · Detección de posibles fraudes en siniestros
        </p>
      </div>
    </div>
  );
}
