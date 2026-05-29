import { DollarSign, PiggyBank, ClipboardCheck } from "lucide-react";

interface SavingsMetrics {
  montoTotalRojos: number;
  ahorroPotencial: number;
  casosPendientes: number;
  casosBajoRiesgo: number;
}

export function SavingsCard({ metrics }: { metrics: SavingsMetrics }) {
  const fmt = (n: number) =>
    n.toLocaleString("es-EC", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

  return (
    <div className="rounded-md border border-border bg-gradient-to-r from-[#1B3A6B]/5 to-[#00AEEF]/5 p-5 shadow-sm">
      <h3 className="text-sm font-semibold text-foreground mb-4">
        Impacto de negocio — deteccion temprana
      </h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-md border border-border bg-card p-4">
          <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
            <DollarSign className="h-4 w-4 text-risk-red" />
            Monto en casos ROJOS
          </div>
          <p className="text-2xl font-semibold text-risk-red tabular-nums">
            {fmt(metrics.montoTotalRojos)}
          </p>
        </div>
        <div className="rounded-md border border-border bg-card p-4">
          <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
            <PiggyBank className="h-4 w-4 text-brand" />
            Ahorro potencial (30%)
          </div>
          <p className="text-2xl font-semibold text-brand tabular-nums">
            {fmt(metrics.ahorroPotencial)}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Si se revisan a tiempo antes del pago
          </p>
        </div>
        <div className="rounded-md border border-border bg-card p-4">
          <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
            <ClipboardCheck className="h-4 w-4 text-risk-yellow" />
            Pendientes de revision
          </div>
          <p className="text-2xl font-semibold tabular-nums">{metrics.casosPendientes}</p>
          <p className="text-xs text-muted-foreground mt-1">Alertas ROJO + AMARILLO</p>
        </div>
        <div className="rounded-md border border-border bg-card p-4">
          <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
            <ClipboardCheck className="h-4 w-4 text-risk-green" />
            Cartera bajo riesgo
          </div>
          <p className="text-2xl font-semibold tabular-nums">{metrics.casosBajoRiesgo}</p>
          <p className="text-xs text-muted-foreground mt-1">Nivel VERDE</p>
        </div>
      </div>
    </div>
  );
}
