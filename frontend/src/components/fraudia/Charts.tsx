import { useState, useEffect } from "react";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { Loader2, AlertCircle } from "lucide-react";
import { API_BASE } from "@/lib/fraudia-api";

// Colores exactos del semáforo
const COLORS = {
  ROJO: "#E24B4A",
  AMARILLO: "#EF9F27",
  VERDE: "#4CAF50",
};

interface Case {
  id_siniestro: string;
  nivel_riesgo: "ROJO" | "AMARILLO" | "VERDE";
  score: number;
  ramo: string;
  ciudad: string;
  monto_reclamado: number;
  beneficiario: string;
  alertas: string;
}

interface ChartCardProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  loading?: boolean;
  error?: string;
}

function ChartCard({ title, subtitle, children, loading, error }: ChartCardProps) {
  return (
    <div className="rounded-md border border-border bg-card p-4 flex flex-col shadow-sm h-full">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-foreground">{title}</h3>
        {subtitle && <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>}
      </div>

      {error ? (
        <div className="flex-1 flex items-center justify-center p-4">
          <div className="text-center flex flex-col items-center gap-2">
            <AlertCircle className="h-8 w-8 text-destructive" />
            <p className="text-xs text-destructive">{error}</p>
          </div>
        </div>
      ) : loading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="flex flex-col items-center gap-2">
            <Loader2 className="h-6 w-6 animate-spin text-primary" />
            <p className="text-xs text-muted-foreground">Cargando datos...</p>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center">{children}</div>
      )}
    </div>
  );
}

function CustomTooltip({ active, payload, label }: any) {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-md bg-foreground text-background p-3 shadow-lg border border-border">
        <p className="text-xs font-medium">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} style={{ color: entry.color }} className="text-xs">
            {entry.name}: {typeof entry.value === "number" ? entry.value.toFixed(1) : entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
}

export function Charts() {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Cargar datos desde API
  useEffect(() => {
    const fetchCases = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(`${API_BASE}/casos?limit=1000`, {
          headers: {
            "ngrok-skip-browser-warning": "true",
          },
        });

        if (!response.ok) throw new Error("Error cargando datos");

        const data = await response.json();
        const casesArray = Array.isArray(data) ? data : data.casos || [];

        // Normalizar datos para asegurar que tengan los campos correctos
        const normalizedCases = casesArray.map((c: any) => ({
          id_siniestro: c.id_siniestro || c.id || "",
          nivel_riesgo: c.nivel_riesgo || c.nivel || "VERDE",
          score: Number(c.score || 0),
          ramo: c.ramo || "General",
          ciudad: c.ciudad || "No especificada",
          monto_reclamado: Number(c.monto_reclamado || c.monto || 0),
          beneficiario: c.beneficiario || c.id_proveedor || "No especificado",
          alertas: c.alertas || "",
        }));

        setCases(normalizedCases);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Error desconocido");
        console.error("Error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchCases();
  }, []);

  // Procesar datos para gráfico de distribución
  const getDistribucionData = () => {
    const rojos = cases.filter((c) => c.nivel_riesgo === "ROJO").length;
    const amarillos = cases.filter((c) => c.nivel_riesgo === "AMARILLO").length;
    const verdes = cases.filter((c) => c.nivel_riesgo === "VERDE").length;
    const total = cases.length;

    return [
      {
        name: "ROJO",
        value: rojos,
        percentage: total > 0 ? ((rojos / total) * 100).toFixed(1) : 0,
      },
      {
        name: "AMARILLO",
        value: amarillos,
        percentage: total > 0 ? ((amarillos / total) * 100).toFixed(1) : 0,
      },
      {
        name: "VERDE",
        value: verdes,
        percentage: total > 0 ? ((verdes / total) * 100).toFixed(1) : 0,
      },
    ];
  };

  // Procesar datos para gráfico de score por ramo
  const getScorePorRamoData = () => {
    const ramoMap = new Map<
      string,
      { scores: number[]; total: number; rojos: number; amarillos: number }
    >();

    cases.forEach((c) => {
      if (!ramoMap.has(c.ramo)) {
        ramoMap.set(c.ramo, { scores: [], total: 0, rojos: 0, amarillos: 0 });
      }
      const ramo = ramoMap.get(c.ramo)!;
      ramo.scores.push(c.score);
      ramo.total++;
      if (c.nivel_riesgo === "ROJO") ramo.rojos++;
      if (c.nivel_riesgo === "AMARILLO") ramo.amarillos++;
    });

    return Array.from(ramoMap.entries()).map(([ramo, data]) => {
      const promedio = data.scores.reduce((a, b) => a + b, 0) / data.scores.length;
      return {
        ramo,
        score: parseFloat(promedio.toFixed(1)),
        rojos: data.rojos,
        amarillos: data.amarillos,
        total: data.total,
      };
    });
  };

  // Procesar datos para gráfico de top proveedores
  const getTopProveedoresData = () => {
    const proveedorMap = new Map<
      string,
      { rojos: number; amarillos: number; total: number }
    >();

    cases.forEach((c) => {
      const proveedor = c.beneficiario || "No especificado";
      if (!proveedorMap.has(proveedor)) {
        proveedorMap.set(proveedor, { rojos: 0, amarillos: 0, total: 0 });
      }
      const prov = proveedorMap.get(proveedor)!;
      prov.total++;
      if (c.nivel_riesgo === "ROJO") prov.rojos++;
      if (c.nivel_riesgo === "AMARILLO") prov.amarillos++;
    });

    return Array.from(proveedorMap.entries())
      .map(([proveedor, data]) => ({
        proveedor,
        rojos: data.rojos,
        amarillos: data.amarillos,
        total: data.total,
      }))
      .sort((a, b) => b.rojos - a.rojos)
      .slice(0, 5);
  };

  // Procesar datos para gráfico de alertas por ciudad
  const getAlertasPorCiudadData = () => {
    const ciudadMap = new Map<
      string,
      { rojos: number; amarillos: number; verdes: number; total: number }
    >();

    cases.forEach((c) => {
      const ciudad = c.ciudad || "No especificada";
      if (!ciudadMap.has(ciudad)) {
        ciudadMap.set(ciudad, { rojos: 0, amarillos: 0, verdes: 0, total: 0 });
      }
      const ciud = ciudadMap.get(ciudad)!;
      ciud.total++;
      if (c.nivel_riesgo === "ROJO") ciud.rojos++;
      if (c.nivel_riesgo === "AMARILLO") ciud.amarillos++;
      if (c.nivel_riesgo === "VERDE") ciud.verdes++;
    });

    return Array.from(ciudadMap.entries())
      .map(([ciudad, data]) => ({
        ciudad,
        rojos: data.rojos,
        amarillos: data.amarillos,
        verdes: data.verdes,
        total: data.total,
      }))
      .sort((a, b) => b.rojos + b.amarillos - (a.rojos + a.amarillos))
      .slice(0, 8);
  };

  // Función para obtener color de barra según score
  const getBarColor = (score: number) => {
    if (score >= 40) return COLORS.ROJO;
    if (score >= 20) return COLORS.AMARILLO;
    return COLORS.VERDE;
  };

  const distribucionData = getDistribucionData();
  const scorePorRamoData = getScorePorRamoData();
  const topProveedoresData = getTopProveedoresData();
  const alertasPorCiudadData = getAlertasPorCiudadData();

  if (error && cases.length === 0) {
    return (
      <div className="rounded-md border border-border bg-card p-4 text-center">
        <p className="text-sm text-destructive">Error cargando gráficos: {error}</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {/* 1. Distribución de Riesgo - DONUT */}
      <ChartCard
        title="Distribución de Riesgo"
        subtitle="Resumen general de casos por nivel de alerta"
        loading={loading}
      >
        <ResponsiveContainer width="100%" height={250}>
          <PieChart>
            <Pie
              data={distribucionData}
              dataKey="value"
              nameKey="name"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={2}
              stroke="#fff"
              strokeWidth={2}
            >
              <Cell fill={COLORS.ROJO} />
              <Cell fill={COLORS.AMARILLO} />
              <Cell fill={COLORS.VERDE} />
            </Pie>
            <Tooltip
              formatter={(value: any, name: string, props: any) => {
                const percentage = props.payload.percentage;
                return [`${value} casos (${percentage}%)`, "Casos"];
              }}
              contentStyle={{
                background: "#fff",
                border: `1px solid #ccc`,
                borderRadius: 6,
                fontSize: 12,
              }}
            />
          </PieChart>
        </ResponsiveContainer>
        <div className="flex flex-wrap justify-center gap-4 text-xs text-muted-foreground mt-4">
          {distribucionData.map((d) => (
            <div key={d.name} className="flex items-center gap-1.5">
              <span
                className="h-2.5 w-2.5 rounded-sm"
                style={{
                  background:
                    d.name === "ROJO"
                      ? COLORS.ROJO
                      : d.name === "AMARILLO"
                        ? COLORS.AMARILLO
                        : COLORS.VERDE,
                }}
              />
              {d.name}: {d.value} ({d.percentage}%)
            </div>
          ))}
        </div>
      </ChartCard>

      {/* 2. Score por Ramo - BARRAS */}
      <ChartCard
        title="Score Promedio por Ramo"
        subtitle="Línea de referencia en 40 (umbral ROJO)"
        loading={loading}
      >
        <ResponsiveContainer width="100%" height={250}>
          <BarChart
            data={scorePorRamoData}
            margin={{ top: 20, right: 30, left: 0, bottom: 60 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#EEF2F7" vertical={false} />
            <XAxis
              dataKey="ramo"
              angle={-45}
              textAnchor="end"
              height={80}
              tick={{ fontSize: 10 }}
            />
            <YAxis tick={{ fontSize: 10 }} />
            <ReferenceLine
              y={40}
              stroke={COLORS.ROJO}
              strokeDasharray="5 5"
              label={{ value: "Umbral ROJO", position: "insideTopRight", offset: -10 }}
            />
            <Tooltip
              contentStyle={{
                background: "#FFFFFF",
                border: `1px solid #CFE3F5`,
                borderRadius: 6,
                fontSize: 12,
              }}
              formatter={(value: any, name: string) => {
                if (name === "score") {
                  return [
                    `${value}`,
                    value >= 40 ? "CRÍTICO" : value >= 20 ? "MEDIO" : "NORMAL",
                  ];
                }
                return [value, name];
              }}
            />
            <Bar dataKey="score" radius={[4, 4, 0, 0]}>
              {scorePorRamoData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getBarColor(entry.score)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      {/* 3. Top Proveedores - BARRAS HORIZONTALES */}
      <ChartCard
        title="Top 5 Proveedores con Mayor Riesgo"
        subtitle="Casos críticos detectados"
        loading={loading}
      >
        <ResponsiveContainer width="100%" height={250}>
          <BarChart
            data={topProveedoresData}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 200, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#EEF2F7" horizontal={false} />
            <XAxis type="number" tick={{ fontSize: 10 }} />
            <YAxis
              dataKey="proveedor"
              type="category"
              width={195}
              tick={{ fontSize: 9 }}
            />
            <Tooltip
              formatter={(value: any) => `${value} casos`}
              contentStyle={{
                background: "#FFFFFF",
                border: "1px solid #CFE3F5",
                borderRadius: 6,
                fontSize: 12,
              }}
            />
            <Legend />
            <Bar dataKey="rojos" fill={COLORS.ROJO} name="Críticos (ROJO)" />
            <Bar dataKey="amarillos" fill={COLORS.AMARILLO} name="Medios (AMARILLO)" />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      {/* 4. Alertas por Ciudad - BARRAS */}
      <ChartCard
        title="Alertas por Ciudad (Top 8)"
        subtitle="Distribución de casos críticos y medios"
        loading={loading}
      >
        <ResponsiveContainer width="100%" height={250}>
          <BarChart
            data={alertasPorCiudadData}
            margin={{ top: 20, right: 30, left: 0, bottom: 60 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#EEF2F7" vertical={false} />
            <XAxis
              dataKey="ciudad"
              angle={-45}
              textAnchor="end"
              height={80}
              tick={{ fontSize: 10 }}
            />
            <YAxis tick={{ fontSize: 10 }} />
            <Tooltip
              contentStyle={{
                background: "#FFFFFF",
                border: "1px solid #CFE3F5",
                borderRadius: 6,
                fontSize: 12,
              }}
              formatter={(value: any) => `${value} casos`}
            />
            <Legend />
            <Bar dataKey="rojos" fill={COLORS.ROJO} name="Críticos" />
            <Bar dataKey="amarillos" fill={COLORS.AMARILLO} name="Medios" />
            <Bar dataKey="verdes" fill={COLORS.VERDE} name="Normales" />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  );
}
