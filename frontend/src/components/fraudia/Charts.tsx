import { useMemo } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  type TooltipProps,
} from "recharts";
import type { Case } from "@/lib/fraudia-api";

const RISK_COLORS = {
  ROJO: "#E24B4A",
  AMARILLO: "#EF9F27",
  VERDE: "#4CAF50",
} as const;

const STACK_LEGEND = {
  rojos: "Alto riesgo",
  amarillos: "Medio riesgo",
  verdes: "Bajo riesgo",
} as const;

function ChartCard({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-full flex-col rounded-md border border-border bg-card p-4 shadow-sm">
      <div className="mb-3">
        <h3 className="text-sm font-semibold text-foreground">{title}</h3>
        {subtitle && <p className="mt-1 text-xs text-muted-foreground">{subtitle}</p>}
      </div>
      <div className="flex-1">{children}</div>
    </div>
  );
}

interface ChartsProps {
  /** Cartera completa (todos los niveles de riesgo) */
  cases: Case[];
}

export function Charts({ cases }: ChartsProps) {
  const charts = useMemo(() => {
    const total = cases.length || 1;

    const distribucion = (["ROJO", "AMARILLO", "VERDE"] as const).map((nivel) => ({
      name: nivel === "ROJO" ? "Alto" : nivel === "AMARILLO" ? "Medio" : "Bajo",
      nivel,
      value: cases.filter((c) => c.nivel === nivel).length,
      color: RISK_COLORS[nivel],
      pct: ((cases.filter((c) => c.nivel === nivel).length / total) * 100).toFixed(1),
    }));

    const ramoMap = new Map<string, { rojos: number; amarillos: number; verdes: number }>();
    cases.forEach((c) => {
      const e = ramoMap.get(c.ramo) ?? { rojos: 0, amarillos: 0, verdes: 0 };
      if (c.nivel === "ROJO") e.rojos += 1;
      else if (c.nivel === "AMARILLO") e.amarillos += 1;
      else e.verdes += 1;
      ramoMap.set(c.ramo, e);
    });
    const riesgoPorRamo = [...ramoMap.entries()]
      .map(([ramo, e]) => ({ ramo, ...e, total: e.rojos + e.amarillos + e.verdes }))
      .sort((a, b) => b.total - a.total);

    const provMap = new Map<string, { rojos: number; amarillos: number; verdes: number }>();
    cases.forEach((c) => {
      const prov = c.beneficiario || "Sin proveedor";
      const e = provMap.get(prov) ?? { rojos: 0, amarillos: 0, verdes: 0 };
      if (c.nivel === "ROJO") e.rojos += 1;
      else if (c.nivel === "AMARILLO") e.amarillos += 1;
      else e.verdes += 1;
      provMap.set(prov, e);
    });
    const topProveedores = [...provMap.entries()]
      .map(([proveedor, e]) => ({
        proveedor,
        rojos: e.rojos,
        amarillos: e.amarillos,
        verdes: e.verdes,
        total: e.rojos + e.amarillos + e.verdes,
      }))
      .sort((a, b) => b.rojos + b.amarillos - (a.rojos + a.amarillos))
      .slice(0, 5);

    const ciudadMap = new Map<string, { rojos: number; amarillos: number; verdes: number }>();
    cases.forEach((c) => {
      const e = ciudadMap.get(c.ciudad) ?? { rojos: 0, amarillos: 0, verdes: 0 };
      if (c.nivel === "ROJO") e.rojos += 1;
      else if (c.nivel === "AMARILLO") e.amarillos += 1;
      else e.verdes += 1;
      ciudadMap.set(c.ciudad, e);
    });
    const riesgoPorCiudad = [...ciudadMap.entries()]
      .map(([ciudad, e]) => ({ ciudad, ...e, total: e.rojos + e.amarillos + e.verdes }))
      .sort((a, b) => b.total - a.total)
      .slice(0, 8);

    return { distribucion, riesgoPorRamo, topProveedores, riesgoPorCiudad, total };
  }, [cases]);

  if (cases.length === 0) {
    return (
      <div className="rounded-md border border-border bg-card p-6 text-center text-sm text-muted-foreground">
        No hay datos para graficar.
      </div>
    );
  }

  const stackTooltipProps: TooltipProps<number, string> = {
    formatter: (value: number, name: string) => [
      value,
      STACK_LEGEND[name as keyof typeof STACK_LEGEND] ?? name,
    ],
  };

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <ChartCard
        title="Distribucion de Riesgo"
        subtitle={`Cartera completa: ${charts.total} siniestros`}
      >
        <ResponsiveContainer width="100%" height={260}>
          <PieChart>
            <Pie
              data={charts.distribucion}
              dataKey="value"
              nameKey="name"
              innerRadius={58}
              outerRadius={95}
              paddingAngle={2}
              stroke="#fff"
              strokeWidth={2}
            >
              {charts.distribucion.map((entry) => (
                <Cell key={entry.nivel} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              formatter={(value: number, name: string, props: { payload?: { pct?: string } }) => [
                `${value} casos (${props.payload?.pct ?? 0}%)`,
                name,
              ]}
            />
          </PieChart>
        </ResponsiveContainer>
        <div className="mt-2 flex flex-wrap justify-center gap-4 text-xs text-muted-foreground">
          {charts.distribucion.map((d) => (
            <span key={d.nivel} className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-sm" style={{ background: d.color }} />
              {d.name}: {d.value} ({d.pct}%)
            </span>
          ))}
        </div>
      </ChartCard>

      <ChartCard
        title="Casos por Ramo y Nivel de Riesgo"
        subtitle="Barras apiladas: alto, medio y bajo en cada ramo"
      >
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={charts.riesgoPorRamo} margin={{ top: 8, right: 8, left: 0, bottom: 56 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#EEF2F7" />
            <XAxis dataKey="ramo" angle={-35} textAnchor="end" height={70} tick={{ fontSize: 10 }} />
            <YAxis tick={{ fontSize: 10 }} allowDecimals={false} />
            <Tooltip {...stackTooltipProps} />
            <Legend />
            <Bar dataKey="rojos" stackId="riesgo" fill={RISK_COLORS.ROJO} name={STACK_LEGEND.rojos} />
            <Bar
              dataKey="amarillos"
              stackId="riesgo"
              fill={RISK_COLORS.AMARILLO}
              name={STACK_LEGEND.amarillos}
            />
            <Bar dataKey="verdes" stackId="riesgo" fill={RISK_COLORS.VERDE} name={STACK_LEGEND.verdes} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard
        title="Top 5 Proveedores"
        subtitle="Desglose alto / medio / bajo riesgo por beneficiario"
      >
        <ResponsiveContainer width="100%" height={260}>
          <BarChart
            data={charts.topProveedores}
            layout="vertical"
            margin={{ top: 4, right: 16, left: 8, bottom: 4 }}
          >
            <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#EEF2F7" />
            <XAxis type="number" tick={{ fontSize: 10 }} allowDecimals={false} />
            <YAxis type="category" dataKey="proveedor" width={118} tick={{ fontSize: 9 }} />
            <Tooltip {...stackTooltipProps} />
            <Legend />
            <Bar dataKey="rojos" stackId="prov" fill={RISK_COLORS.ROJO} name={STACK_LEGEND.rojos} />
            <Bar
              dataKey="amarillos"
              stackId="prov"
              fill={RISK_COLORS.AMARILLO}
              name={STACK_LEGEND.amarillos}
            />
            <Bar dataKey="verdes" stackId="prov" fill={RISK_COLORS.VERDE} name={STACK_LEGEND.verdes} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard
        title="Riesgo por Ciudad"
        subtitle="Top 8 ciudades con desglose alto / medio / bajo"
      >
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={charts.riesgoPorCiudad} margin={{ top: 8, right: 8, left: 0, bottom: 56 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#EEF2F7" />
            <XAxis dataKey="ciudad" angle={-35} textAnchor="end" height={70} tick={{ fontSize: 10 }} />
            <YAxis tick={{ fontSize: 10 }} allowDecimals={false} />
            <Tooltip {...stackTooltipProps} />
            <Legend />
            <Bar dataKey="rojos" stackId="ciudad" fill={RISK_COLORS.ROJO} name={STACK_LEGEND.rojos} />
            <Bar
              dataKey="amarillos"
              stackId="ciudad"
              fill={RISK_COLORS.AMARILLO}
              name={STACK_LEGEND.amarillos}
            />
            <Bar dataKey="verdes" stackId="ciudad" fill={RISK_COLORS.VERDE} name={STACK_LEGEND.verdes} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  );
}
