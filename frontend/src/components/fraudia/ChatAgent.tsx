import { useEffect, useRef, useState } from "react";
import { Bot, Send } from "lucide-react";
import { API_BASE } from "../../lib/fraudia-api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const WELCOME_MESSAGE =
  "Hola. Soy el agente antifraude de FraudIA. Puedo ayudarte a revisar casos criticos, explicar scores de riesgo y resumir patrones en la cartera. Escribe tu pregunta o elige una sugerencia.";

const SUGGESTED_QUESTIONS = [
  "Cuales son los 10 casos mas criticos",
  "Por que SIN-00003 es de alto riesgo",
  "Que proveedores concentran mas alertas",
  "Que ciudades tienen mayor concentracion",
  "Genera resumen ejecutivo de casos criticos",
  "Recomienda que casos revisar primero",
];

function LoadingDots() {
  return (
    <span className="inline-flex items-center gap-1" aria-label="Cargando">
      <span className="h-1.5 w-1.5 rounded-full bg-gray-500 animate-bounce [animation-delay:0ms]" />
      <span className="h-1.5 w-1.5 rounded-full bg-gray-500 animate-bounce [animation-delay:150ms]" />
      <span className="h-1.5 w-1.5 rounded-full bg-gray-500 animate-bounce [animation-delay:300ms]" />
    </span>
  );
}

export function ChatAgent() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: WELCOME_MESSAGE },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [useUploadedDataset, setUseUploadedDataset] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
          "ngrok-skip-browser-warning": "true",
        },
        body: JSON.stringify({
          pregunta: trimmed,
          usar_dataset_subido: useUploadedDataset,
        }),
      });

      if (!response.ok) {
        throw new Error(`Error del servidor: ${response.status}`);
      }

      const data = (await response.json()) as {
        respuesta?: string;
        answer?: string;
        message?: string;
      };

      const reply =
        data.respuesta ??
        data.answer ??
        data.message ??
        "No pude generar una respuesta. Intenta reformular tu pregunta.";

      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "No fue posible contactar al agente en este momento. Verifica la conexion con el servidor e intenta de nuevo.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void sendMessage(input);
    }
  };

  return (
    <div className="w-full">
      <div className="flex h-screen max-h-[calc(100vh-120px)] w-full flex-col overflow-hidden rounded-lg border border-border bg-white shadow-sm md:h-[720px]">
        <div
          className="flex shrink-0 items-center gap-3 px-4 py-3 sm:px-6 sm:py-4"
          style={{
            background: "linear-gradient(90deg, #1B3A6B 0%, #00AEEF 100%)",
          }}
        >
          <Bot className="h-5 w-5 shrink-0 text-white sm:h-6 sm:w-6" aria-hidden />
          <div className="min-w-0 flex-1">
            <h3 className="truncate text-sm font-semibold text-white sm:text-base">
              Agente Antifraude FraudIA
            </h3>
            <p className="truncate text-xs text-blue-100">
              Consultas en lenguaje natural
            </p>
          </div>
        </div>

        <div className="flex-1 space-y-3 overflow-y-auto bg-slate-50 px-3 py-4 sm:space-y-4 sm:px-6 sm:py-6">
          {messages.map((msg, idx) => (
            <div
              key={`${msg.role}-${idx}`}
              className={`flex w-full ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`break-words rounded-2xl px-3 py-2 text-sm leading-relaxed sm:px-4 sm:py-3 ${
                  msg.role === "user"
                    ? "rounded-br-sm w-full bg-[#1B3A6B] text-white xs:max-w-xs sm:max-w-sm md:max-w-md"
                    : "rounded-bl-sm border border-gray-200 bg-gray-100 text-gray-900 w-full xs:max-w-xs sm:max-w-sm md:max-w-md"
                }`}
              >
                {msg.role === "assistant" && (
                  <div className="mb-1 flex items-center gap-2 text-xs font-medium text-gray-600">
                    <Bot className="h-3 w-3 shrink-0" aria-hidden />
                    <span>Agente FraudIA</span>
                  </div>
                )}
                {msg.role === "user" && (
                  <p className="mb-1 text-right text-xs font-medium text-blue-200">
                    Analista
                  </p>
                )}
                <p className="whitespace-pre-wrap break-words">{msg.content}</p>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex w-full justify-start">
              <div className="break-words rounded-2xl rounded-bl-sm border border-gray-200 bg-gray-100 px-3 py-2 text-sm sm:px-4 sm:py-3">
                <div className="mb-1 flex items-center gap-2 text-xs font-medium text-gray-600">
                  <Bot className="h-3 w-3 shrink-0" aria-hidden />
                  <span>Agente FraudIA</span>
                </div>
                <LoadingDots />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="shrink-0 border-t border-border bg-white px-3 py-2 sm:px-6 sm:py-3">
          <p className="mb-2 text-xs font-medium text-muted-foreground">
            Preguntas sugeridas
          </p>
          <div className="flex flex-wrap gap-1.5 sm:gap-2">
            {SUGGESTED_QUESTIONS.map((question) => (
              <button
                key={question}
                type="button"
                onClick={() => void sendMessage(question)}
                disabled={loading}
                className="truncate rounded-full border border-[#00AEEF] bg-white px-2 py-1 text-xs text-[#1B3A6B] transition hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-50 sm:px-3 sm:py-1.5"
              >
                {question}
              </button>
            ))}
          </div>
        </div>

        <div className="shrink-0 border-t border-border bg-white px-3 py-3 sm:px-6 sm:py-4">
          <label className="mb-3 flex cursor-pointer items-center gap-2 text-xs text-muted-foreground">
            <input
              type="checkbox"
              checked={useUploadedDataset}
              onChange={(e) => setUseUploadedDataset(e.target.checked)}
              className="rounded border-border"
            />
            <span className="truncate">Usar dataset subido</span>
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Escribe tu pregunta..."
              disabled={loading}
              className="flex-1 rounded-lg border border-border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#00AEEF] disabled:cursor-not-allowed disabled:opacity-50"
              aria-label="Mensaje para el agente"
            />
            <button
              type="button"
              onClick={() => void sendMessage(input)}
              disabled={loading || !input.trim()}
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg text-white transition disabled:cursor-not-allowed disabled:opacity-50"
              style={{
                background: "linear-gradient(135deg, #1B3A6B 0%, #00AEEF 100%)",
              }}
              aria-label="Enviar mensaje"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
          <p className="mt-2 text-center text-xs text-muted-foreground sm:mt-3">
            Este sistema genera alertas de revisión, no acusaciones formales.
          </p>
        </div>
      </div>
    </div>
  );
}
