import { useState } from "react";
import { Download, FileText, FileSpreadsheet, Loader2 } from "lucide-react";
import { api } from "@/lib/fraudia-api";

function saveBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export function DownloadActions() {
  const [loadingCsv, setLoadingCsv] = useState(false);
  const [loadingRep, setLoadingRep] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const today = new Date().toISOString().slice(0, 10);

  async function handleCsv() {
    setError(null);
    setLoadingCsv(true);
    try {
      const blob = await api.downloadCasos();
      saveBlob(blob, `fraudia-casos-${today}.csv`);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoadingCsv(false);
    }
  }

  async function handleReporte() {
    setError(null);
    setLoadingRep(true);
    try {
      const blob = await api.downloadReporte();
      const isPdf = blob.type.includes("pdf");
      saveBlob(blob, `fraudia-resumen-ejecutivo-${today}.${isPdf ? "pdf" : "txt"}`);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoadingRep(false);
    }
  }

  return (
    <div className="flex flex-col items-end gap-1">
      <div className="flex flex-wrap gap-2">
        <button
          onClick={handleCsv}
          disabled={loadingCsv}
          className="inline-flex items-center gap-2 rounded-md border border-border bg-card px-3.5 py-2 text-sm font-medium text-foreground hover:bg-secondary transition-colors shadow-sm disabled:opacity-60"
        >
          {loadingCsv ? (
            <Loader2 className="h-4 w-4 animate-spin text-brand" />
          ) : (
            <FileSpreadsheet className="h-4 w-4 text-brand" />
          )}
          Descargar CSV
        </button>
        <button
          onClick={handleReporte}
          disabled={loadingRep}
          className="inline-flex items-center gap-2 rounded-md bg-brand text-brand-foreground px-3.5 py-2 text-sm font-medium hover:opacity-90 transition-opacity shadow-sm disabled:opacity-60"
        >
          {loadingRep ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <FileText className="h-4 w-4" />
          )}
          Resumen Ejecutivo
        </button>
        <button
          onClick={() => window.print()}
          className="inline-flex items-center gap-2 rounded-md border border-border bg-card px-3.5 py-2 text-sm font-medium text-muted-foreground hover:bg-secondary transition-colors shadow-sm"
        >
          <Download className="h-4 w-4" />
          Imprimir
        </button>
      </div>
      {error && <p className="text-xs text-risk-red">Error al descargar: {error}</p>}
    </div>
  );
}
