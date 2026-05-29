import { useEffect, useState } from "react";
import { Car, Loader2, ShieldAlert } from "lucide-react";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { api } from "@/lib/fraudia-api";
import type { Risk } from "@/lib/fraudia-mock";

function nivelBadge(nivel: string) {
  const n = nivel.toUpperCase();
  if (n.includes("ROJ")) return "bg-risk-red text-risk-red-foreground";
  if (n.includes("AMAR")) return "bg-risk-yellow text-risk-yellow-foreground";
  return "bg-risk-green text-risk-green-foreground";
}

function nivelLabel(nivel: string) {
  const n = nivel.toUpperCase() as Risk;
  if (n === "ROJO") return "Alto riesgo";
  if (n === "AMARILLO") return "Medio riesgo";
  return "Bajo riesgo";
}

interface Props {
  caseId: string | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CaseDetailSheet({ caseId, open, onOpenChange }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [explicacion, setExplicacion] = useState("");
  const [reglas, setReglas] = useState<string[]>([]);
  const [caso, setCaso] = useState<Record<string, unknown> | null>(null);
  const [vehiculo, setVehiculo] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    if (!open || !caseId) return;

    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.caseDetail(caseId);
        setCaso(data.caso);
        setVehiculo(data.vehiculo ?? null);
        setExplicacion(data.explicacion);
        setReglas(data.reglas_activas ?? []);
      } catch (e) {
        setError((e as Error).message);
        setCaso(null);
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, [open, caseId]);

  const nivel = String(caso?.nivel_riesgo ?? "");
  const score = Number(caso?.score ?? 0);

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full overflow-y-auto sm:max-w-lg">
        <SheetHeader>
          <SheetTitle className="font-mono text-brand">{caseId}</SheetTitle>
          <SheetDescription>Explicacion de alertas y factores de riesgo</SheetDescription>
        </SheetHeader>

        {loading && (
          <div className="flex items-center justify-center gap-2 py-12 text-muted-foreground">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span className="text-sm">Cargando detalle...</span>
          </div>
        )}

        {error && (
          <p className="mt-4 text-sm text-destructive" role="alert">
            {error}
          </p>
        )}

        {caso && !loading && (
          <div className="mt-6 space-y-6">
            <div className="flex flex-wrap items-center gap-2">
              <span
                className={`rounded px-2.5 py-0.5 text-xs font-semibold ${nivelBadge(nivel)}`}
              >
                {nivelLabel(nivel)}
              </span>
              <span className="text-sm text-muted-foreground">
                Score: <strong className="text-foreground">{score}</strong>/100
              </span>
              {Boolean(caso.es_anomalia) && (
                <span className="rounded border border-border bg-secondary px-2 py-0.5 text-xs">
                  Anomalia ML
                </span>
              )}
            </div>

            <dl className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <dt className="text-muted-foreground">Ramo</dt>
                <dd className="font-medium">{String(caso.ramo ?? "-")}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Ciudad</dt>
                <dd className="font-medium">{String(caso.ciudad ?? "-")}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Beneficiario</dt>
                <dd className="font-medium">{String(caso.beneficiario ?? "-")}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Monto reclamado</dt>
                <dd className="font-mono font-medium">
                  ${Number(caso.monto_reclamado ?? 0).toLocaleString("es-EC")}
                </dd>
              </div>
            </dl>

            {(vehiculo || caso.placa) && (
              <div className="rounded-lg border border-border bg-secondary/30 p-4">
                <h4 className="mb-3 flex items-center gap-2 text-sm font-semibold">
                  <Car className="h-4 w-4 text-[#1B3A6B]" />
                  Vehiculo asociado
                </h4>
                <dl className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <dt className="text-muted-foreground">Placa</dt>
                    <dd className="font-mono font-medium">
                      {String(vehiculo?.placa ?? caso.placa ?? "-")}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-muted-foreground">Frecuencia placa</dt>
                    <dd className="font-medium">
                      {Number(caso.frecuencia_placa ?? 0)} siniestro(s)
                    </dd>
                  </div>
                  <div>
                    <dt className="text-muted-foreground">Marca / Modelo</dt>
                    <dd className="font-medium">
                      {String(
                        vehiculo?.marca ??
                          caso.marca_vehiculo ??
                          "-",
                      )}{" "}
                      {String(vehiculo?.modelo ?? caso.modelo_vehiculo ?? "")}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-muted-foreground">Anio</dt>
                    <dd className="font-medium">
                      {String(vehiculo?.anio ?? caso.anio_vehiculo ?? "-")}
                    </dd>
                  </div>
                  {Number(caso.frecuencia_conductor ?? 0) > 0 && (
                    <div className="col-span-2">
                      <dt className="text-muted-foreground">Frecuencia conductor (vehicular)</dt>
                      <dd className="font-medium text-risk-yellow">
                        {Number(caso.frecuencia_conductor)} siniestro(s) del mismo asegurado
                      </dd>
                    </div>
                  )}
                </dl>
                {Number(caso.frecuencia_placa ?? 0) >= 3 && (
                  <p className="mt-2 text-xs text-risk-red">
                    Alerta RF-08: esta placa aparece en 3 o mas siniestros.
                  </p>
                )}
              </div>
            )}

            <div>
              <h4 className="mb-2 flex items-center gap-2 text-sm font-semibold">
                <ShieldAlert className="h-4 w-4 text-[#1B3A6B]" />
                Reglas activadas
              </h4>
              <ul className="space-y-2">
                {reglas.map((r) => (
                  <li
                    key={r}
                    className="rounded-md border border-border bg-secondary/50 px-3 py-2 text-xs leading-relaxed"
                  >
                    {r}
                  </li>
                ))}
                {reglas.length === 0 && (
                  <li className="text-xs text-muted-foreground">Sin alertas registradas.</li>
                )}
              </ul>
            </div>

            <div>
              <h4 className="mb-2 text-sm font-semibold">Resumen para el analista</h4>
              <pre className="whitespace-pre-wrap rounded-md border border-border bg-muted/40 p-3 text-xs leading-relaxed">
                {explicacion}
              </pre>
            </div>

            <p className="text-xs text-muted-foreground">
              Alerta de revision. No constituye acusacion formal. Decision final del analista
              humano.
            </p>
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}
