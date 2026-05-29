import { Shield, LogOut, User } from "lucide-react";
import { type User as UserType } from "@/lib/auth";

interface HeaderProps {
  active: string;
  onTabChange: (tab: string) => void;
  user?: UserType | null;
  onLogout?: () => void;
}

const tabs = ["Panel General", "Casos Sospechosos", "Proveedores", "Agente IA", "Analizar Dataset"];

export function FraudiaHeader({ active, onTabChange, user, onLogout }: HeaderProps) {
  return (
    <header
      className="sticky top-0 z-30 shadow-sm text-white"
      style={{ background: "linear-gradient(90deg, #1B3A6B 0%, #00AEEF 100%)" }}
    >
      <div className="mx-auto max-w-[1400px] px-4 sm:px-6 pt-5 pb-0 flex flex-col gap-4">
        {/* Top row: Logo + Title + User Info */}
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <div className="h-12 w-12 rounded-md bg-white flex items-center justify-center shadow flex-shrink-0">
              <img
                src="/logo.jpg"
                alt="Aseguradora del Sur"
                className="h-10 w-10 object-contain"
                onError={(e) => {
                  e.currentTarget.style.display = "none";
                  e.currentTarget.parentElement!.innerHTML =
                    '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-700" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>';
                }}
              />
            </div>
            <div className="min-w-0">
              <h1 className="text-xl sm:text-2xl font-semibold tracking-tight">
                FraudIA
              </h1>
              <p className="text-xs sm:text-sm text-white/80 truncate">
                Sistema de Detección de Posibles Fraudes — Aseguradora del Sur
              </p>
            </div>
          </div>

          {/* User info + Logout */}
          {user && (
            <div className="flex items-center gap-3 flex-shrink-0">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium">{user.name}</p>
                <p className="text-xs text-white/70">{user.role}</p>
              </div>
              <div className="h-10 w-10 rounded-full bg-white/20 flex items-center justify-center">
                <User className="h-5 w-5 text-white" />
              </div>
              {onLogout && (
                <button
                  onClick={onLogout}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-white/10 hover:bg-white/20 transition text-sm font-medium"
                  title="Cerrar sesión"
                >
                  <LogOut className="h-4 w-4" />
                  <span className="hidden sm:inline">Salir</span>
                </button>
              )}
            </div>
          )}
        </div>

        {/* Tabs */}
        <nav className="flex gap-1 overflow-x-auto -mx-1 px-1 scrollbar-none">
          {tabs.map((t) => {
            const isActive = t === active;
            return (
              <button
                key={t}
                onClick={() => onTabChange(t)}
                className={`whitespace-nowrap px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
                  isActive
                    ? "border-white text-white"
                    : "border-transparent text-white/75 hover:text-white"
                }`}
              >
                {t}
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
}