import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useCallback, useEffect, useMemo, useState } from "react";
import { FraudiaHeader } from "@/components/fraudia/Header";
import { MetricsCards } from "@/components/fraudia/MetricsCards";
import { CasesTable } from "@/components/fraudia/CasesTable";
import { AiAgent } from "@/components/fraudia/AiAgent";
import { ChartsGrid } from "@/components/fraudia/ChartsGrid";
import { ProveedoresTable } from "@/components/fraudia/ProveedoresTable";
import { DownloadActions } from "@/components/fraudia/DownloadActions";
import { LoadingSpinner, ErrorState } from "@/components/fraudia/LoadingState";
import { DataAnalyzer } from "@/components/fraudia/DataAnalyzer";
import { api, type Case, type Metrics, type Proveedor } from "@/lib/fraudia-api";
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

const RISK_COLORS = { ROJO: "#E24B4A", AMARILLO: "#F59E0B", VERDE: "#22C55E" } as const;

function deriveCharts(cases: Case[], proveedores: Proveedor[]) {
  const dist = (["ROJO", "AMARILLO", "VERDE"] as const).map((nivel) => ({
    name: nivel.charAt(0) + nivel.slice(1).toLowerCase(),
    value: cases.filter((c) => c.nivel === nivel).length,
    color: RISK_COLORS[nivel],
  }));

  const ramoMap = new Map<string, { sum: number; n: number }>();
  cases.forEach((c) => {
    if (!c.ramo) return;
    const e = ramoMap.get(c.ramo) ?? { sum: 0, n: 0 };
    e.sum += c.score;
    e.n += 1;
    ramoMap.set(c.ramo, e);
  });
  const scorePorRamo = [...ramoMap.entries()]
    .map(([ramo, e]) => ({ ramo, score: Math.round((e.sum / e.n) * 10) / 10 }))
    .sort((a, b) => b.score - a.score);

  const topProveedores = [...proveedores]
    .sort((a, b) => b.alertas - a.alertas)
    .slice(0, 5)
    .map((p) => ({ proveedor: p.nombre, alertas: p.alertas }));

  const ciudadMap = new Map<string, number>();
  cases.forEach((c) => {
    if (!c.ciudad) return;
    if (c.nivel === "VERDE") return;
    ciudadMap.set(c.ciudad, (ciudadMap.get(c.ciudad) ?? 0) + 1);
  });
  const alertasPorCiudad = [...ciudadMap.entries()]
    .map(([ciudad, alertas]) => ({ ciudad, alertas }))
    .sort((a, b) => b.alertas - a.alertas)
    .slice(0, 8);

  return { dist, scorePorRamo, topProveedores, alertasPorCiudad };
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
        api.cases(),
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

  const charts = useMemo(() => deriveCharts(cases, proveedores), [cases, proveedores]);

  const renderBody = () => {
    if (loading) return <LoadingSpinner label="Cargando datos desde el servidor..." />;
    if (error) return <ErrorState message={error} onRetry={load} />;
    if (!metrics) return <ErrorState message="No hay datos disponibles" onRetry={load} />;

    if (tab === "Panel General") {
      return (
        <>
          <MetricsCards metrics={metrics} />
          <ChartsGrid
            distribucionRiesgo={charts.dist}
            scorePorRamo={charts.scorePorRamo}
            topProveedores={charts.topProveedores}
            alertasPorCiudad={charts.alertasPorCiudad}
          />
          <CasesTable cases={cases.slice(0, 10)} />
        </>
      );
    }
    if (tab === "Casos Sospechosos") {
      return (
        <>
          <MetricsCards metrics={metrics} />
          <CasesTable cases={cases} />
        </>
      );
    }
    if (tab === "Proveedores") {
      return (
        <>
          <ProveedoresTable proveedores={proveedores} />
          <ChartsGrid
            distribucionRiesgo={charts.dist}
            scorePorRamo={charts.scorePorRamo}
            topProveedores={charts.topProveedores}
            alertasPorCiudad={charts.alertasPorCiudad}
          />
        </>
      );
    }
    if (tab === "Analizar Dataset") {
      return <DataAnalyzer />;
    }
    return (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <AiAgent />
        </div>
        <div className="space-y-4">
          <MetricsCards metrics={metrics} />
        </div>
      </div>
    );
  };

  const subtitles: Record<string, string> = {
    "Panel General": "Vista consolidada de siniestros y alertas de fraude",
    "Casos Sospechosos": "Siniestros marcados por el motor de detección",
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
            <code className="font-mono text-brand">gilled-founder-plot.ngrok-free.dev</code>
          </p>
        </footer>
      </main>
    </div>
  );
}
