// FraudIA API client — VITE_API_BASE en .env.local o localhost por defecto.
import type { Case, Risk } from "./fraudia-mock";

/**
 * URL del backend FastAPI.
 * En desarrollo usa proxy Vite (/api) para evitar errores CORS "Failed to fetch".
 */
function resolveApiBase(): string {
  const fromEnv = (import.meta.env.VITE_API_BASE as string | undefined)?.replace(/\/$/, "");
  if (import.meta.env.DEV) {
    return "/api";
  }
  return fromEnv || "http://127.0.0.1:8000";
}

export const API_BASE = resolveApiBase();

export const COMMON_HEADERS: HeadersInit = {
  "ngrok-skip-browser-warning": "true",
};

export interface VehiculoDetalle {
  id_vehiculo?: string;
  placa?: string;
  marca?: string;
  modelo?: string;
  anio?: number;
  chasis?: string;
  motor?: string;
}

export interface CaseDetail {
  caso: Record<string, unknown>;
  vehiculo?: VehiculoDetalle | null;
  explicacion: string;
  reglas_activas: string[];
}

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "GET",
    headers: { ...COMMON_HEADERS, Accept: "application/json" },
  });
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
  return (await res.json()) as T;
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: {
      ...COMMON_HEADERS,
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`POST ${path} failed: ${res.status}`);
  return (await res.json()) as T;
}

// ---------- Normalizers (be tolerant about field names) ----------

interface RawMetrics {
  total_siniestros?: number;
  totalSiniestros?: number;
  rojos?: number;
  alertas_rojas?: number;
  amarillos?: number;
  alertas_amarillas?: number;
  score_promedio?: number;
  scorePromedio?: number;
  monto_total_rojos?: number;
  ahorro_potencial_30pct?: number;
  casos_pendientes_revision?: number;
  casos_bajo_riesgo?: number;
}

export interface Metrics {
  totalSiniestros: number;
  alertasRojas: number;
  alertasAmarillas: number;
  scorePromedio: number;
  montoTotalRojos: number;
  ahorroPotencial: number;
  casosPendientes: number;
  casosBajoRiesgo: number;
}

function normalizeMetrics(r: RawMetrics): Metrics {
  return {
    totalSiniestros: Number(r.total_siniestros ?? r.totalSiniestros ?? 0),
    alertasRojas: Number(r.rojos ?? r.alertas_rojas ?? 0),
    alertasAmarillas: Number(r.amarillos ?? r.alertas_amarillas ?? 0),
    scorePromedio: Number(r.score_promedio ?? r.scorePromedio ?? 0),
    montoTotalRojos: Number(r.monto_total_rojos ?? 0),
    ahorroPotencial: Number(r.ahorro_potencial_30pct ?? 0),
    casosPendientes: Number(r.casos_pendientes_revision ?? 0),
    casosBajoRiesgo: Number(r.casos_bajo_riesgo ?? 0),
  };
}

function toRisk(v: unknown, score: number): Risk {
  const s = String(v ?? "").toUpperCase();
  if (s.includes("ROJ")) return "ROJO";
  if (s.includes("AMAR")) return "AMARILLO";
  if (s.includes("VERD")) return "VERDE";
  if (score >= 40) return "ROJO";
  if (score >= 20) return "AMARILLO";
  return "VERDE";
}

function toAlertsArray(v: unknown): string[] {
  if (Array.isArray(v)) return v.map((x) => String(x));
  if (typeof v === "string" && v.trim().length > 0)
    return v.split(/[;,|]/).map((s) => s.trim()).filter(Boolean);
  return [];
}

function normalizeCase(r: Record<string, unknown>): Case {
  const score = Number(r.score ?? r.puntaje ?? r.risk_score ?? 0);
  let nivel_riesgo = r.nivel_riesgo ?? r.nivel ?? r.riesgo ?? r.level;

  // Si no viene nivel_riesgo, calcularlo del score
  if (!nivel_riesgo) {
    if (score >= 40) nivel_riesgo = "ROJO";
    else if (score >= 20) nivel_riesgo = "AMARILLO";
    else nivel_riesgo = "VERDE";
  }

  return {
    id: String(r.id ?? r.id_siniestro ?? r.siniestro ?? r.codigo ?? ""),
    nivel: toRisk(nivel_riesgo, score),
    score,
    ramo: String(r.ramo ?? r.linea ?? ""),
    ciudad: String(r.ciudad ?? r.city ?? ""),
    monto: Number(r.monto ?? r.monto_reclamado ?? r.valor ?? 0),
    alertas: toAlertsArray(r.alertas ?? r.motivos ?? r.razones),
    beneficiario: String(r.beneficiario ?? r.proveedor ?? ""),
  };
}

export interface Proveedor {
  id: string;
  nombre: string;
  alertas: number;
  casosRojos: number;
  casosAmarillos: number;
  montoTotal: number;
}

function normalizeProveedor(r: Record<string, unknown>, i: number): Proveedor {
  return {
    id: String(r.proveedor ?? r.id ?? r.codigo ?? `PRV-${String(1000 + i).padStart(4, "0")}`),
    nombre: String(r.proveedor ?? r.nombre ?? r.name ?? "—"),
    alertas: Number(r.total_alertas ?? r.alertas ?? 0),
    casosRojos: Number(r.casos_rojos ?? 0),
    casosAmarillos: Number(r.casos_amarillos ?? 0),
    montoTotal: Number(r.monto_total ?? r.montoTotal ?? r.monto ?? 0),
  };
}

// ---------- Public API ----------

export const api = {
  async metrics(): Promise<Metrics> {
    const raw = await getJson<RawMetrics>("/resumen");
    return normalizeMetrics(raw);
  },
  async cases(options?: {
    limit?: number;
    nivel?: string;
    /** true = top por score; false = cartera completa (graficos / filtros) */
    prioridad?: boolean;
  }): Promise<Case[]> {
    const params = new URLSearchParams();
    if (options?.limit != null) params.set("limit", String(options.limit));
    if (options?.nivel) params.set("nivel", options.nivel);
    if (options?.prioridad === false) params.set("prioridad", "false");

    const qs = params.toString();
    const raw = await getJson<unknown>(`/casos${qs ? `?${qs}` : ""}`);
    const arr = Array.isArray(raw)
      ? raw
      : Array.isArray((raw as { casos?: unknown[] })?.casos)
        ? (raw as { casos: unknown[] }).casos
        : [];
    return arr
      .map((r) => normalizeCase(r as Record<string, unknown>))
      .sort((a, b) => b.score - a.score);
  },
  async proveedores(): Promise<Proveedor[]> {
    const raw = await getJson<unknown>("/proveedores");
    const arr = Array.isArray(raw)
      ? raw
      : Array.isArray((raw as { proveedores?: unknown[] })?.proveedores)
        ? (raw as { proveedores: unknown[] }).proveedores
        : [];
    return arr.map((r, i) => normalizeProveedor(r as Record<string, unknown>, i));
  },
  async caseDetail(id: string): Promise<CaseDetail> {
    const raw = await getJson<CaseDetail & { error?: string }>(
      `/caso/${encodeURIComponent(id)}`,
    );
    if (raw.error) throw new Error(raw.error);
    return raw;
  },
  async chat(pregunta: string): Promise<{ answer: string }> {
    const raw = await postJson<Record<string, unknown>>("/chat", { pregunta });
    const answer =
      (raw.respuesta as string) ??
      (raw.answer as string) ??
      (raw.message as string) ??
      (raw.texto as string) ??
      JSON.stringify(raw);
    return { answer: String(answer) };
  },
  async downloadCasos(): Promise<Blob> {
    const res = await fetch(`${API_BASE}/descargar/casos`, {
      headers: COMMON_HEADERS,
    });
    if (!res.ok) throw new Error(`GET /descargar/casos failed: ${res.status}`);
    return await res.blob();
  },
  async downloadReporte(): Promise<Blob> {
    const res = await fetch(`${API_BASE}/descargar/reporte`, {
      headers: COMMON_HEADERS,
    });
    if (!res.ok) throw new Error(`GET /descargar/reporte failed: ${res.status}`);
    return await res.blob();
  },
};

export type { Case };
