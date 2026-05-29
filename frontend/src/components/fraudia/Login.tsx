import { useState } from "react";
import { Lock, AlertCircle } from "lucide-react";
import { validateCredentials, saveAuthToStorage, type User } from "@/lib/auth";

interface LoginProps {
  onLoginSuccess: (user: User) => void;
}

export function Login({ onLoginSuccess }: LoginProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    // Simular pequeño delay para mejor UX
    await new Promise(resolve => setTimeout(resolve, 500));

    const user = validateCredentials(email, password);

    if (!user) {
      setError("Credenciales inválidas. Por favor, intente de nuevo.");
      setPassword("");
      setLoading(false);
      return;
    }

    // Guardad sesión
    saveAuthToStorage(user);
    setLoading(false);
    onLoginSuccess(user);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1B3A6B] to-[#00AEEF] flex items-center justify-center p-4">
      {/* Contenedor principal */}
      <div className="w-full max-w-md">
        {/* Card de Login */}
        <div className="bg-white rounded-xl shadow-2xl overflow-hidden">
          {/* Header con gradiente */}
          <div className="bg-gradient-to-r from-[#1B3A6B] to-[#00AEEF] px-6 py-8 text-center">
            {/* Logo */}
            <div className="mb-4 flex justify-center">
              <img
                src="/logo.jpg"
                alt="Aseguradora del Sur"
                className="h-16 w-auto"
                onError={(e) => {
                  // Fallback si la imagen no carga
                  e.currentTarget.style.display = "none";
                }}
              />
            </div>

            <h1 className="text-2xl font-bold text-white mb-2">
              FraudIA
            </h1>
            <p className="text-sm text-blue-100">
              Sistema Antifraude
            </p>
            <p className="text-xs text-blue-100 mt-1">
              Acceso exclusivo para analistas autorizados
            </p>
          </div>

          {/* Contenido */}
          <div className="px-6 py-8">
            {/* Aviso de confidencialidad */}
            <div className="mb-6 p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex gap-3">
              <Lock className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div className="text-xs text-yellow-800">
                <p className="font-semibold mb-1">Información Confidencial</p>
                <p>
                  Este sistema contiene información confidencial. El acceso no autorizado
                  está prohibido por ley.
                </p>
              </div>
            </div>

            {/* Error message */}
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex gap-3">
                <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            {/* Formulario */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1.5">
                  Usuario (Email Corporativo)
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="analista@aseguradoradelsur.com"
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                  disabled={loading}
                />
              </div>

              {/* Password */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1.5">
                  Contraseña
                </label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                  disabled={loading}
                />
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading || !email || !password}
                className="w-full bg-gradient-to-r from-[#1B3A6B] to-[#00AEEF] text-white font-semibold py-2.5 rounded-lg hover:shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed mt-6"
              >
                {loading ? "Validando..." : "Iniciar Sesión"}
              </button>
            </form>

            {/* Demo credentials hint */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-xs text-gray-500 mb-2 font-semibold">Credenciales de demostración:</p>
              <div className="space-y-1 text-xs text-gray-600">
                <p>• <span className="font-mono">analista@aseguradoradelsur.com</span> / <span className="font-mono">FraudIA2026</span></p>
                <p>• <span className="font-mono">admin@aseguradoradelsur.com</span> / <span className="font-mono">Admin2026</span></p>
                <p>• <span className="font-mono">jurado@hackiathon.com</span> / <span className="font-mono">Demo2026</span></p>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="bg-gray-50 px-6 py-4 border-t border-gray-200 text-center">
            <p className="text-xs text-gray-600">
              © Aseguradora del Sur - Sistema de uso interno
            </p>
          </div>
        </div>

        {/* Disclaimer abajo */}
        <div className="mt-6 text-center">
          <p className="text-xs text-blue-100 max-w-xs mx-auto">
            Hackathon 2026 - Sistema de Detección de Fraudes en Siniestros de Seguros
          </p>
        </div>
      </div>
    </div>
  );
}
