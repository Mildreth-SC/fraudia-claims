interface Proveedor {
  id: string;
  nombre: string;
  alertas: number;
  casosRojos: number;
  casosAmarillos: number;
  montoTotal: number;
}

export function ProveedoresTable({ proveedores }: { proveedores: Proveedor[] }) {
  return (
    <section className="rounded-md border border-border bg-card shadow-sm">
      <div className="p-4 border-b border-border">
        <h2 className="text-base font-semibold text-foreground">Proveedores</h2>
        <p className="text-xs text-muted-foreground">
          Ranking por número total de alertas (ROJO + AMARILLO)
        </p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs uppercase tracking-wider text-muted-foreground bg-secondary">
              <th className="px-4 py-3 font-semibold">Proveedor</th>
              <th className="px-4 py-3 font-semibold text-center">Total Alertas</th>
              <th className="px-4 py-3 font-semibold text-center">Críticos</th>
              <th className="px-4 py-3 font-semibold text-center">Medio Riesgo</th>
              <th className="px-4 py-3 font-semibold text-right">Monto Total</th>
            </tr>
          </thead>
          <tbody>
            {proveedores.map((p) => (
              <tr key={p.id} className="border-t border-border hover:bg-secondary/60">
                <td className="px-4 py-3 font-medium text-foreground">{p.nombre}</td>
                <td className="px-4 py-3 text-center">
                  <span className="inline-flex items-center rounded bg-primary/10 text-primary px-2.5 py-0.5 text-xs font-semibold">
                    {p.alertas}
                  </span>
                </td>
                <td className="px-4 py-3 text-center">
                  <span className="inline-flex items-center rounded bg-risk-red/10 text-risk-red px-2.5 py-0.5 text-xs font-semibold">
                    {p.casosRojos}
                  </span>
                </td>
                <td className="px-4 py-3 text-center">
                  <span className="inline-flex items-center rounded bg-risk-yellow/10 text-risk-yellow px-2.5 py-0.5 text-xs font-semibold">
                    {p.casosAmarillos}
                  </span>
                </td>
                <td className="px-4 py-3 text-right font-mono tabular-nums text-foreground">
                  ${p.montoTotal.toLocaleString("es-EC")}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
