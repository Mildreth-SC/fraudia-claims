import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useCallback, useEffect, useMemo, useState } from "react";
import { FraudiaHeader } from "@/components/fraudia/Header";
import { MetricsCards } from "@/components/fraudia/MetricsCards";
import { SavingsCard } from "@/components/fraudia/SavingsCard";
import { CasesTable } from "@/components/fraudia/CasesTable";
import { ChatAgent } from "@/components/fraudia/ChatAgent";
import { Charts } from "@/components/fraudia/Charts";
import { ProveedoresTable } from "@/components/fraudia/ProveedoresTable";
import { DownloadActions } from "@/components/fraudia/DownloadActions";
import { LoadingSpinner, ErrorState } from "@/components/fraudia/LoadingState";
import { DataAnalyzer } from "@/components/fraudia/DataAnalyzer";
import { api, API_BASE, type Case, type Metrics, type Proveedor } from "@/lib/fraudia-api";
import { useAuth } from "./__root";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "FraudIA — Detección de Fraudes | Aseguradora del Sur" },
      {
        name: "description",
        content:
          "Sistema FraudIA para detección de posibles fraudes en siniestros de Aseguradora del Sur.",
      },
    ],
  }),
  component: Index,
});

function SectionTitle({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div>
      <h2 className="text-lg font-semibold text-foreground">{title}</h2>
      {subtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
    </div>
  );
}

function Index() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [tab, setTab] = useState("Panel General");
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [cases, setCases] = useState<Case[]>([]);
  const [proveedores, setProveedores] = useState<Proveedor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Redirige al login si no está autenticado
  useEffect(() => {
    if (!user) {
      navigate({ to: "/login" });
    }
  }, [user, navigate]);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [m, c, p] = await Promise.all([
        api.metrics(),
        api.cases({ limit: 5000, prioridad: false }),
        api.proveedores(),
      ]);
      setMetrics(m);
      setCases(c);
      setProveedores(p);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleLogout = () => {
    logout();
    navigate({ to: "/login" });
  };

  const renderBody = () => {
    if (loading) return <LoadingSpinner label="Cargando datos desde el servidor..." />;
    if (error) return <ErrorState message={error} onRetry={load} />;
    if (!metrics) return <ErrorState message="No hay datos disponibles" onRetry={load} />;

    if (tab === "Panel General") {
      return (
        <>
          <MetricsCards metrics={metrics} />
          <SavingsCard
            metrics={{
              montoTotalRojos: metrics.montoTotalRojos,
              ahorroPotencial: metrics.ahorroPotencial,
              casosPendientes: metrics.casosPendientes,
              casosBajoRiesgo: metrics.casosBajoRiesgo,
            }}
          />
          <Charts cases={cases} />
          <CasesTable
            cases={cases}
            title="Top 10 - Prioridad de revision"
            subtitle="Casos con mayor score; use filtros para ver otros niveles"
            defaultFilter="todos"
            maxRows={10}
          />
        </>
      );
    }
    if (tab === "Casos Sospechosos") {
      return (
        <>
          <MetricsCards metrics={metrics} />
          <CasesTable
            cases={cases}
            title="Cartera completa de siniestros"
            subtitle="Filtre por nivel: alto, medio, bajo o solo con alerta"
            defaultFilter="alertas"
          />
        </>
      );
    }
    if (tab === "Proveedores") {
      return (
        <>
          <ProveedoresTable proveedores={proveedores} />
          <Charts cases={cases} />
        </>
      );
    }
    if (tab === "Analizar Dataset") {
      return <DataAnalyzer />;
    }
    if (tab === "Agente IA") {
      return <ChatAgent />;
    }
    return null;
  };

  const subtitles: Record<string, string> = {
    "Panel General": "Resumen de cartera, graficos por nivel y top 10 prioritarios",
    "Casos Sospechosos": "Cartera completa con filtros por alto, medio y bajo riesgo",
    Proveedores: "Análisis de proveedores asociados a alertas",
    "Agente IA": "Consultas en lenguaje natural sobre la cartera",
    "Analizar Dataset": "Carga y analiza tus propios datasets",
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <FraudiaHeader active={tab} onTabChange={setTab} user={user} onLogout={handleLogout} />

      <main className="mx-auto max-w-[1400px] px-4 sm:px-6 py-6 space-y-6">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <SectionTitle title={tab} subtitle={subtitles[tab]} />
          <DownloadActions />
        </div>

        <div className="space-y-6">{renderBody()}</div>

        <footer className="pt-4 pb-8 text-center text-xs text-muted-foreground border-t border-border">
          <p className="pt-4">
            © Aseguradora del Sur · FraudIA · API:{" "}
            <code className="font-mono text-brand">{API_BASE.replace(/^https?:\/\//, "")}</code>
          </p>
        </footer>
      </main>
    </div>
  );
}
