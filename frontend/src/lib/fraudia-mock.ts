// Mock fallback data. Deterministic (seeded) so SSR and client render identically.

export type Risk = "ROJO" | "AMARILLO" | "VERDE";

export interface Case {
  id: string;
  nivel: Risk;
  score: number;
  ramo: string;
  ciudad: string;
  monto: number;
  alertas: string[];
  beneficiario?: string;
}

const ramos = ["Automóvil", "Hogar", "Vida", "Salud", "Comercial"];
const ciudades = ["Quito", "Guayaquil", "Cuenca", "Manta", "Ambato", "Loja"];
const alertasPool = [
  "Múltiples siniestros",
  "Proveedor recurrente",
  "Monto atípico",
  "Fecha sospechosa",
  "Documentación incompleta",
  "Beneficiario recurrente",
  "Geolocalización inconsistente",
];

// Mulberry32 deterministic PRNG
function makeRng(seed: number) {
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function generateMockCases(n = 60, seed = 42): Case[] {
  const rng = makeRng(seed);
  const pick = <T,>(arr: T[]) => arr[Math.floor(rng() * arr.length)];
  const cases: Case[] = [];
  for (let i = 0; i < n; i++) {
    const score = Math.round(rng() * 100);
    const nivel: Risk = score >= 70 ? "ROJO" : score >= 40 ? "AMARILLO" : "VERDE";
    const alertCount =
      nivel === "ROJO"
        ? 3 + Math.floor(rng() * 3)
        : nivel === "AMARILLO"
          ? 1 + Math.floor(rng() * 2)
          : Math.floor(rng() * 2);
    const alertas: string[] = [];
    for (let j = 0; j < alertCount; j++) alertas.push(pick(alertasPool));
    cases.push({
      id: `SIN-${String(100000 + i).padStart(6, "0")}`,
      nivel,
      score,
      ramo: pick(ramos),
      ciudad: pick(ciudades),
      monto: Math.round(500 + rng() * 80000),
      alertas: Array.from(new Set(alertas)),
    });
  }
  return cases.sort((a, b) => b.score - a.score);
}

export const mockCases = generateMockCases(60);

export const mockMetrics = {
  totalSiniestros: 1000,
  alertasRojas: 171,
  alertasAmarillas: 104,
  scorePromedio: 15.2,
};

export const mockDistribucionRiesgo = [
  { name: "Rojo", value: 171, color: "#E24B4A" },
  { name: "Amarillo", value: 104, color: "#F59E0B" },
  { name: "Verde", value: 725, color: "#22C55E" },
];

export const mockScorePorRamo = [
  { ramo: "Automóvil", score: 22.4 },
  { ramo: "Hogar", score: 14.1 },
  { ramo: "Vida", score: 9.7 },
  { ramo: "Salud", score: 18.6 },
  { ramo: "Comercial", score: 11.3 },
];

export const mockTopProveedores = [
  { proveedor: "Taller Andes", alertas: 42 },
  { proveedor: "Clínica Norte", alertas: 35 },
  { proveedor: "AutoFix S.A.", alertas: 29 },
  { proveedor: "Repuestos del Sur", alertas: 24 },
  { proveedor: "Hospital Central", alertas: 19 },
];

export const mockAlertasPorCiudad = [
  { ciudad: "Quito", alertas: 88 },
  { ciudad: "Guayaquil", alertas: 71 },
  { ciudad: "Cuenca", alertas: 42 },
  { ciudad: "Manta", alertas: 31 },
  { ciudad: "Ambato", alertas: 25 },
  { ciudad: "Loja", alertas: 18 },
];

export const mockProveedores = mockTopProveedores.map((p, i) => ({
  id: `PRV-${String(1000 + i).padStart(4, "0")}`,
  nombre: p.proveedor,
  alertas: p.alertas,
  siniestrosVinculados: Math.round(p.alertas * 1.8),
  montoTotal: Math.round(p.alertas * 6500),
}));
