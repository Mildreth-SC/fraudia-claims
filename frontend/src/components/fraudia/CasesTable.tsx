import { useMemo, useState } from "react";
import type { Case, Risk } from "@/lib/fraudia-mock";
import { CaseDetailSheet } from "@/components/fraudia/CaseDetailSheet";

const filterDefs = [
  { key: "todos", label: "Todos" },
  { key: "alertas", label: "Con alerta" },
  { key: "rojos", label: "Alto" },
  { key: "amarillos", label: "Medio" },
  { key: "verdes", label: "Bajo" },
] as const;

type FilterKey = (typeof filterDefs)[number]["key"];

function badgeClasses(level: Risk) {
  switch (level) {
    case "ROJO":
      return "bg-risk-red text-risk-red-foreground";
    case "AMARILLO":
      return "bg-risk-yellow text-risk-yellow-foreground";
    case "VERDE":
      return "bg-risk-green text-risk-green-foreground";
  }
}

function scoreBarColor(score: number) {
  if (score >= 40) return "bg-risk-red";
  if (score >= 20) return "bg-risk-yellow";
  return "bg-risk-green";
}

function nivelLabel(nivel: Risk) {
  if (nivel === "ROJO") return "Alto";
  if (nivel === "AMARILLO") return "Medio";
  return "Bajo";
}

export interface CasesTableProps {
  cases: Case[];
  title?: string;
  subtitle?: string;
  defaultFilter?: FilterKey;
  maxRows?: number;
}

export function CasesTable({
  cases,
  title = "Cartera de siniestros",
  subtitle = "Listado ordenado por score de riesgo",
  defaultFilter = "todos",
  maxRows,
}: CasesTableProps) {
  const [filter, setFilter] = useState<FilterKey>(defaultFilter);
  const [detailId, setDetailId] = useState<string | null>(null);
  const [sheetOpen, setSheetOpen] = useState(false);

  const counts = useMemo(
    () => ({
      todos: cases.length,
      alertas: cases.filter((c) => c.nivel === "ROJO" || c.nivel === "AMARILLO").length,
      rojos: cases.filter((c) => c.nivel === "ROJO").length,
      amarillos: cases.filter((c) => c.nivel === "AMARILLO").length,
      verdes: cases.filter((c) => c.nivel === "VERDE").length,
    }),
    [cases],
  );

  const filtered = useMemo(() => {
    const sorted = [...cases].sort((a, b) => b.score - a.score);
    let list = sorted;
    if (filter === "alertas") {
      list = sorted.filter((c) => c.nivel === "ROJO" || c.nivel === "AMARILLO");
    } else if (filter === "rojos") {
      list = sorted.filter((c) => c.nivel === "ROJO");
    } else if (filter === "amarillos") {
      list = sorted.filter((c) => c.nivel === "AMARILLO");
    } else if (filter === "verdes") {
      list = sorted.filter((c) => c.nivel === "VERDE");
    }
    return maxRows ? list.slice(0, maxRows) : list;
  }, [cases, filter, maxRows]);

  const openCase = (id: string) => {
    setDetailId(id);
    setSheetOpen(true);
  };

  return (
    <>
    <section className="rounded-md border border-border bg-card shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3 border-b border-border p-4">
        <div>
          <h2 className="text-base font-semibold text-foreground">{title}</h2>
          <p className="text-xs text-muted-foreground">{subtitle}</p>
          <p className="mt-2 text-xs text-muted-foreground">
            Mostrando <span className="font-semibold text-foreground">{filtered.length}</span>
            {maxRows ? ` de top ${maxRows}` : ""} · Cartera:{" "}
            <span className="text-risk-red-foreground font-medium">{counts.rojos} alto</span>
            {" · "}
            <span className="text-risk-yellow-foreground font-medium">{counts.amarillos} medio</span>
            {" · "}
            <span className="text-risk-green-foreground font-medium">{counts.verdes} bajo</span>
          </p>
        </div>
        <div className="flex flex-wrap gap-1 rounded-md border border-border bg-secondary p-1">
          {filterDefs.map((f) => (
            <button
              key={f.key}
              type="button"
              onClick={() => setFilter(f.key)}
              className={`rounded px-3 py-1.5 text-sm transition-colors ${
                filter === f.key
                  ? "bg-brand text-brand-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {f.label}
              <span className="ml-1 text-[10px] opacity-80">({counts[f.key]})</span>
            </button>
          ))}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-secondary text-left text-xs uppercase tracking-wider text-muted-foreground">
              <th className="px-4 py-3 font-semibold">ID Siniestro</th>
              <th className="px-4 py-3 font-semibold">Nivel</th>
              <th className="min-w-[180px] px-4 py-3 font-semibold">Score</th>
              <th className="px-4 py-3 font-semibold">Ramo</th>
              <th className="px-4 py-3 font-semibold">Ciudad</th>
              <th className="px-4 py-3 text-right font-semibold">Monto Reclamado</th>
              <th className="px-4 py-3 font-semibold">Alertas</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((c) => (
              <tr
                key={c.id}
                className="cursor-pointer border-t border-border transition-colors hover:bg-secondary/60"
                onClick={() => openCase(c.id)}
              >
                <td className="px-4 py-3 font-mono text-xs text-brand underline-offset-2 hover:underline">
                  {c.id}
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`inline-flex items-center rounded px-2.5 py-0.5 text-[11px] font-semibold tracking-wide ${badgeClasses(
                      c.nivel,
                    )}`}
                    title={c.nivel}
                  >
                    {nivelLabel(c.nivel)}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-secondary">
                      <div
                        className={`h-full ${scoreBarColor(c.score)}`}
                        style={{ width: `${Math.min(c.score, 100)}%` }}
                      />
                    </div>
                    <span className="w-8 text-right font-mono text-xs tabular-nums text-foreground">
                      {c.score}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3 text-foreground">{c.ramo}</td>
                <td className="px-4 py-3 text-muted-foreground">{c.ciudad}</td>
                <td className="px-4 py-3 text-right font-mono tabular-nums text-foreground">
                  ${c.monto.toLocaleString("es-EC")}
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1">
                    {c.alertas.slice(0, 2).map((a) => (
                      <span
                        key={a}
                        className="rounded border border-border bg-secondary px-1.5 py-0.5 text-[10px] text-foreground"
                      >
                        {a}
                      </span>
                    ))}
                    {c.alertas.length > 2 && (
                      <span className="rounded border border-border bg-secondary px-1.5 py-0.5 text-[10px] text-muted-foreground">
                        +{c.alertas.length - 2}
                      </span>
                    )}
                  </div>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-10 text-center text-muted-foreground">
                  Sin casos para este filtro.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
    <CaseDetailSheet
      caseId={detailId}
      open={sheetOpen}
      onOpenChange={setSheetOpen}
    />
    </>
  );
}
