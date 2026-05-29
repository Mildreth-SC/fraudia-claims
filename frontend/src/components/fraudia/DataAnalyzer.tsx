import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  AlertCircle,
  CheckCircle2,
  Download,
  FileUp,
  Loader2,
  Play,
  Terminal,
  XCircle,
} from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import { API_BASE, COMMON_HEADERS } from "@/lib/fraudia-api";

interface AnalysisResult {
  status: "success" | "error" | "idle";
  resumen?: {
    total_casos: number;
    rojos: number;
    amarillos: number;
    verdes: number;
    score_promedio: number;
  };
  reporte_limpieza?: string;
  reporte_alertas?: string;
  casos?: Array<{
    id_siniestro: string;
    nivel_riesgo: string;
    score: number;
    alertas: string;
  }>;
  graficos?: {
    distribucion_riesgo?: string;
    score_por_ramo?: string;
    top_proveedores?: string;
    alertas_ciudad?: string;
  };
  columnas_disponibles?: string[];
  error?: string;
}

interface SqlResult {
  columnas?: string[];
  filas?: Record<string, unknown>[];
  total_filas?: number;
  error?: string;
}

const SQL_EJEMPLOS = [
  "SELECT nivel_riesgo, COUNT(*) AS total FROM siniestros GROUP BY nivel_riesgo",
  "SELECT id_siniestro, score, ciudad, ramo FROM siniestros WHERE nivel_riesgo = 'ROJO' ORDER BY score DESC",
  "SELECT beneficiario, COUNT(*) AS alertas FROM siniestros WHERE nivel_riesgo IN ('ROJO','AMARILLO') GROUP BY beneficiario ORDER BY alertas DESC",
];

export function DataAnalyzer() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult>({ status: "idle" });
  const [dragActive, setDragActive] = useState(false);
  const [sqlQuery, setSqlQuery] = useState(SQL_EJEMPLOS[0]);
  const [sqlLoading, setSqlLoading] = useState(false);
  const [sqlResult, setSqlResult] = useState<SqlResult | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const files = e.dataTransfer.files;
    if (files?.[0]) {
      setFile(files[0]);
      setResult({ status: "idle" });
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
      setResult({ status: "idle" });
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;

    const ext = file.name.split(".").pop()?.toLowerCase() ?? "";
    if (!["csv", "xlsx", "xls"].includes(ext)) {
      setResult({
        status: "error",
        error: "Formato no soportado. Use CSV o Excel (.xlsx).",
      });
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), 120_000);

    try {
      const response = await fetch(`${API_BASE}/analizar-dataset`, {
        method: "POST",
        body: formData,
        signal: controller.signal,
        headers: { ...COMMON_HEADERS },
      });

      let data: AnalysisResult & { error?: string };
      try {
        data = (await response.json()) as AnalysisResult & { error?: string };
      } catch {
        throw new Error(`Respuesta invalida del servidor (${response.status})`);
      }

      if (response.ok && data.status === "success") {
        setResult({ status: "success", ...data });
      } else {
        setResult({
          status: "error",
          error:
            data.error ||
            `Error del servidor (${response.status}). Verifique que el backend este activo en el puerto 8000.`,
        });
      }
    } catch (error) {
      const msg = String(error);
      const hint =
        msg.includes("abort")
          ? "El analisis tardo demasiado. Pruebe con un CSV mas pequeno."
          : `No se pudo conectar a ${API_BASE}. Inicie el backend: python src/app/main_local_test.py y reinicie npm run dev.`;
      setResult({
        status: "error",
        error: `Error de conexion: ${msg}. ${hint}`,
      });
    } finally {
      window.clearTimeout(timeoutId);
      setLoading(false);
    }
  };

  const downloadFile = async (tipo: "csv" | "limpieza" | "alertas") => {
    try {
      const response = await fetch(
        `${API_BASE}/descargar/analisis/${tipo}`,
        { headers: { ...COMMON_HEADERS } }
      );
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = tipo === "csv"
        ? "datos_limpios.csv"
        : tipo === "limpieza"
        ? "reporte_limpieza.txt"
        : "reporte_alertas.txt";
      a.click();
    } catch (error) {
      console.error("Error descargando archivo:", error);
    }
  };

  const runSqlQuery = async () => {
    setSqlLoading(true);
    setSqlResult(null);
    try {
      const response = await fetch(`${API_BASE}/dataset/consulta`, {
        method: "POST",
        headers: {
          ...COMMON_HEADERS,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ sql: sqlQuery, limit: 50 }),
      });
      const data = (await response.json()) as SqlResult;
      setSqlResult(data);
    } catch (error) {
      setSqlResult({ error: `Error de conexion: ${String(error)}` });
    } finally {
      setSqlLoading(false);
    }
  };

  const downloadGrafico = async (nombre: string) => {
    try {
      const response = await fetch(
        `${API_BASE}/graficos/${nombre}`,
        { headers: { ...COMMON_HEADERS } }
      );
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = nombre;
      a.click();
    } catch (error) {
      console.error("Error descargando gráfico:", error);
    }
  };

  return (
    <div className="space-y-6 p-6">
      {/* Sección de carga */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">1. Cargar Dataset</h2>

        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition ${
            dragActive
              ? "border-primary bg-primary/5"
              : "border-border hover:border-primary/50"
          }`}
        >
          <FileUp className="mx-auto mb-2 h-8 w-8 text-muted-foreground" />
          <p className="font-medium text-sm mb-1">
            Arrastra tu archivo CSV aquí o haz clic para seleccionar
          </p>
          <p className="text-xs text-muted-foreground">
            Soporta CSV o Excel (.xlsx) del evento — cualquier estructura de columnas
          </p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={handleFileChange}
            className="hidden"
          />
          <Button
            variant="outline"
            size="sm"
            onClick={() => fileInputRef.current?.click()}
            className="mt-4"
          >
            Seleccionar archivo
          </Button>
        </div>

        {file && (
          <div className="mt-4 p-3 bg-secondary rounded-lg flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-green-500" />
            <span className="text-sm font-medium">{file.name}</span>
            <span className="text-xs text-muted-foreground">
              ({(file.size / 1024).toFixed(1)} KB)
            </span>
          </div>
        )}
      </Card>

      {/* Botón de análisis */}
      {file && (
        <Button
          onClick={handleAnalyze}
          disabled={loading}
          className="w-full h-10"
          size="lg"
        >
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Analizando...
            </>
          ) : (
            "Analizar Dataset"
          )}
        </Button>
      )}

      {/* Resumen de limpieza */}
      {result.status === "success" && result.resumen && (
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">2. Resumen de Limpieza</h2>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-secondary p-3 rounded-lg">
              <p className="text-xs text-muted-foreground mb-1">Total Casos</p>
              <p className="text-2xl font-bold">{result.resumen.total_casos}</p>
            </div>

            <div className="bg-risk-red/10 p-3 rounded-lg">
              <p className="text-xs text-muted-foreground mb-1">Críticos (ROJO)</p>
              <p className="text-2xl font-bold text-risk-red">
                {result.resumen.rojos}
              </p>
            </div>

            <div className="bg-risk-yellow/10 p-3 rounded-lg">
              <p className="text-xs text-muted-foreground mb-1">Medio (AMARILLO)</p>
              <p className="text-2xl font-bold text-risk-yellow">
                {result.resumen.amarillos}
              </p>
            </div>

            <div className="bg-risk-green/10 p-3 rounded-lg">
              <p className="text-xs text-muted-foreground mb-1">Normal (VERDE)</p>
              <p className="text-2xl font-bold text-risk-green">
                {result.resumen.verdes}
              </p>
            </div>
          </div>

          <div className="mt-4 p-3 bg-secondary rounded-lg">
            <p className="text-sm">
              <span className="font-medium">Score Promedio:</span>{" "}
              {result.resumen.score_promedio}/100
            </p>
          </div>

          {result.reporte_limpieza && (
            <div className="mt-4">
              <h3 className="text-sm font-semibold mb-2">Detalles de Limpieza</h3>
              <pre className="bg-secondary p-3 rounded text-xs overflow-auto max-h-48">
                {result.reporte_limpieza}
              </pre>
            </div>
          )}
        </Card>
      )}

      {/* Gráficos */}
      {result.status === "success" && result.graficos && (
        <Card className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">3b. Gráficos Generados</h2>
            <p className="text-xs text-muted-foreground">Haz clic en las imágenes para descargar</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Gráfico 1 */}
            {result.graficos.distribucion_riesgo && (
              <div className="border rounded-lg p-4 bg-secondary hover:shadow-md transition cursor-pointer"
                   onClick={() => downloadGrafico("distribucion_riesgo.png")}>
                <div className="flex justify-between items-start mb-2">
                  <p className="text-sm font-semibold">Distribución de Riesgo</p>
                  <Download className="h-4 w-4 text-muted-foreground" />
                </div>
                <img
                  src={`${API_BASE}${result.graficos.distribucion_riesgo}`}
                  alt="Distribución"
                  className="w-full rounded"
                  onError={(e) => { e.currentTarget.style.display = 'none'; }}
                />
              </div>
            )}

            {/* Gráfico 2 */}
            {result.graficos.score_por_ramo && (
              <div className="border rounded-lg p-4 bg-secondary hover:shadow-md transition cursor-pointer"
                   onClick={() => downloadGrafico("score_por_ramo.png")}>
                <div className="flex justify-between items-start mb-2">
                  <p className="text-sm font-semibold">Score por Ramo</p>
                  <Download className="h-4 w-4 text-muted-foreground" />
                </div>
                <img
                  src={`${API_BASE}${result.graficos.score_por_ramo}`}
                  alt="Score por Ramo"
                  className="w-full rounded"
                  onError={(e) => { e.currentTarget.style.display = 'none'; }}
                />
              </div>
            )}

            {/* Gráfico 3 */}
            {result.graficos.top_proveedores && (
              <div className="border rounded-lg p-4 bg-secondary hover:shadow-md transition cursor-pointer"
                   onClick={() => downloadGrafico("top_proveedores.png")}>
                <div className="flex justify-between items-start mb-2">
                  <p className="text-sm font-semibold">Top Proveedores</p>
                  <Download className="h-4 w-4 text-muted-foreground" />
                </div>
                <img
                  src={`${API_BASE}${result.graficos.top_proveedores}`}
                  alt="Top Proveedores"
                  className="w-full rounded"
                  onError={(e) => { e.currentTarget.style.display = 'none'; }}
                />
              </div>
            )}

            {/* Gráfico 4 */}
            {result.graficos.alertas_ciudad && (
              <div className="border rounded-lg p-4 bg-secondary hover:shadow-md transition cursor-pointer"
                   onClick={() => downloadGrafico("alertas_ciudad.png")}>
                <div className="flex justify-between items-start mb-2">
                  <p className="text-sm font-semibold">Alertas por Ciudad</p>
                  <Download className="h-4 w-4 text-muted-foreground" />
                </div>
                <img
                  src={`${API_BASE}${result.graficos.alertas_ciudad}`}
                  alt="Alertas Ciudad"
                  className="w-full rounded"
                  onError={(e) => { e.currentTarget.style.display = 'none'; }}
                />
              </div>
            )}
          </div>

          <p className="text-xs text-muted-foreground mt-4">💡 Haz clic en cualquier gráfico para descargarlo como PNG</p>
        </Card>
      )}

      {/* Alertas detectadas */}
      {result.status === "success" && result.casos && (
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">4. Alertas Detectadas</h2>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2 font-medium">ID Siniestro</th>
                  <th className="text-left p-2 font-medium">Nivel</th>
                  <th className="text-left p-2 font-medium">Score</th>
                  <th className="text-left p-2 font-medium">Alertas</th>
                </tr>
              </thead>
              <tbody>
                {result.casos.slice(0, 20).map((caso, idx) => (
                  <tr key={idx} className="border-b hover:bg-secondary">
                    <td className="p-2 font-mono text-xs">{caso.id_siniestro}</td>
                    <td className="p-2">
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${
                          caso.nivel_riesgo === "ROJO"
                            ? "bg-risk-red/20 text-risk-red"
                            : caso.nivel_riesgo === "AMARILLO"
                            ? "bg-risk-yellow/20 text-risk-yellow"
                            : "bg-risk-green/20 text-risk-green"
                        }`}
                      >
                        {caso.nivel_riesgo}
                      </span>
                    </td>
                    <td className="p-2 font-semibold">{caso.score}</td>
                    <td className="p-2 text-xs text-muted-foreground">
                      {caso.alertas?.split(" | ").slice(0, 2).join(" • ")}
                      {caso.alertas?.split(" | ").length > 2 && "..."}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {result.casos.length > 20 && (
            <p className="text-xs text-muted-foreground mt-2">
              Mostrando 20 de {result.casos.length} casos
            </p>
          )}
        </Card>
      )}

      {/* Informe detallado */}
      {result.status === "success" && result.reporte_alertas && (
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">5. Informe Ejecutivo Detallado</h2>

          <pre className="bg-secondary p-4 rounded text-xs overflow-auto max-h-96 whitespace-pre-wrap">
            {result.reporte_alertas}
          </pre>
        </Card>
      )}

      {/* Consola SQL sobre el dataset subido */}
      {result.status === "success" && (
        <Card className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <Terminal className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold">7. Consola del dataset (SQL)</h2>
          </div>
          <p className="text-sm text-muted-foreground mb-3">
            Consulta el CSV analizado como si fuera una tabla{" "}
            <code className="bg-secondary px-1 rounded">siniestros</code>.
            Solo lectura (SELECT). Motor DuckDB en memoria.
          </p>

          {result.columnas_disponibles && (
            <p className="text-xs text-muted-foreground mb-3">
              Columnas: {result.columnas_disponibles.slice(0, 12).join(", ")}
              {result.columnas_disponibles.length > 12 && "..."}
            </p>
          )}

          <div className="flex flex-wrap gap-2 mb-3">
            {SQL_EJEMPLOS.map((ej) => (
              <Button
                key={ej.slice(0, 30)}
                variant="outline"
                size="sm"
                className="text-xs h-7"
                onClick={() => setSqlQuery(ej)}
              >
                Ejemplo
              </Button>
            ))}
          </div>

          <Textarea
            value={sqlQuery}
            onChange={(e) => setSqlQuery(e.target.value)}
            className="font-mono text-xs min-h-[100px] mb-3"
            spellCheck={false}
          />

          <Button onClick={runSqlQuery} disabled={sqlLoading} className="mb-4">
            {sqlLoading ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Play className="mr-2 h-4 w-4" />
            )}
            Ejecutar consulta
          </Button>

          {sqlResult?.error && (
            <p className="text-sm text-red-600 bg-red-50 p-3 rounded">{sqlResult.error}</p>
          )}

          {sqlResult?.filas && sqlResult.columnas && (
            <div className="overflow-x-auto border rounded-lg">
              <table className="w-full text-xs">
                <thead>
                  <tr className="bg-secondary border-b">
                    {sqlResult.columnas.map((col) => (
                      <th key={col} className="text-left p-2 font-medium">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {sqlResult.filas.map((row, idx) => (
                    <tr key={idx} className="border-b hover:bg-secondary/50">
                      {sqlResult.columnas!.map((col) => (
                        <td key={col} className="p-2 font-mono">
                          {String(row[col] ?? "")}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="text-xs text-muted-foreground p-2">
                {sqlResult.total_filas} fila(s) devuelta(s)
              </p>
            </div>
          )}
        </Card>
      )}

      {/* Botones de descarga */}
      {result.status === "success" && (
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">6. Descargar Resultados</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <Button
              onClick={() => downloadFile("csv")}
              variant="outline"
              className="justify-start"
            >
              <Download className="mr-2 h-4 w-4" />
              Datos Limpios (CSV)
            </Button>

            <Button
              onClick={() => downloadFile("limpieza")}
              variant="outline"
              className="justify-start"
            >
              <Download className="mr-2 h-4 w-4" />
              Reporte de Limpieza
            </Button>

            <Button
              onClick={() => downloadFile("alertas")}
              variant="outline"
              className="justify-start"
            >
              <Download className="mr-2 h-4 w-4" />
              Informe de Alertas
            </Button>
          </div>
        </Card>
      )}

      {/* Error */}
      {result.status === "error" && (
        <Card className="p-6 border-red-200 bg-red-50">
          <div className="flex gap-3">
            <XCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-900">Error en análisis</h3>
              <p className="text-sm text-red-700 mt-1">{result.error}</p>
            </div>
          </div>
        </Card>
      )}

      {/* Info */}
      <Card className="p-4 bg-blue-50 border-blue-200">
        <div className="flex gap-3">
          <AlertCircle className="h-5 w-5 text-blue-500 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-blue-800">
            El sistema soporta archivos CSV con cualquier estructura de columnas.
            Detecta automáticamente: fecha, monto, proveedor, cobertura, etc.
            Compatible con nombres de columnas en inglés o español.
          </p>
        </div>
      </Card>
    </div>
  );
}
