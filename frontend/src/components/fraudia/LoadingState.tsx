import { Loader2, AlertTriangle } from "lucide-react";

export function LoadingSpinner({ label = "Cargando datos..." }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-muted-foreground">
      <Loader2 className="h-8 w-8 animate-spin text-brand" />
      <p className="text-sm">{label}</p>
    </div>
  );
}

export function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="rounded-md border border-risk-red/30 bg-risk-red/5 p-6 flex flex-col items-center gap-3 text-center">
      <AlertTriangle className="h-7 w-7 text-risk-red" />
      <div>
        <p className="font-semibold text-foreground">No se pudieron cargar los datos</p>
        <p className="text-xs text-muted-foreground mt-1 max-w-md">{message}</p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="rounded-md bg-brand text-brand-foreground px-4 py-2 text-sm font-medium hover:opacity-90"
        >
          Reintentar
        </button>
      )}
    </div>
  );
}
