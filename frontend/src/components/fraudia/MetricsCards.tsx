import { AlertTriangle, AlertCircle, Activity, FileBarChart } from "lucide-react";

interface Metrics {
  totalSiniestros: number;
  alertasRojas: number;
  alertasAmarillas: number;
  scorePromedio: number;
}

export function MetricsCards({ metrics }: { metrics: Metrics }) {
  const items = [
    {
      label: "Total Siniestros",
      value: metrics.totalSiniestros.toLocaleString("es-EC"),
      icon: FileBarChart,
      iconBg: "bg-brand-soft text-brand",
      accent: "border-l-4 border-l-brand",
    },
    {
      label: "Alertas Rojas",
      value: metrics.alertasRojas.toLocaleString("es-EC"),
      icon: AlertCircle,
      iconBg: "bg-risk-red/10 text-risk-red",
      accent: "border-l-4 border-l-risk-red",
    },
    {
      label: "Alertas Amarillas",
      value: metrics.alertasAmarillas.toLocaleString("es-EC"),
      icon: AlertTriangle,
      iconBg: "bg-risk-yellow/10 text-risk-yellow",
      accent: "border-l-4 border-l-risk-yellow",
    },
    {
      label: "Score Promedio",
      value: metrics.scorePromedio.toFixed(1),
      icon: Activity,
      iconBg: "bg-risk-green/10 text-risk-green",
      accent: "border-l-4 border-l-risk-green",
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {items.map((it) => (
        <div
          key={it.label}
          className={`rounded-md border border-border bg-card p-5 shadow-sm ${it.accent}`}
        >
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="text-xs uppercase tracking-wider text-muted-foreground font-medium">
                {it.label}
              </p>
              <p className="mt-2 text-3xl font-semibold text-foreground tabular-nums">
                {it.value}
              </p>
            </div>
            <div
              className={`h-10 w-10 shrink-0 rounded-md flex items-center justify-center ${it.iconBg}`}
            >
              <it.icon className="h-5 w-5" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
