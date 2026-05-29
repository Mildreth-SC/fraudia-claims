import { useState, useRef, useEffect } from "react";
import { Bot, Send } from "lucide-react";
import { API_BASE } from "@/lib/fraudia-api";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const SUGGESTED_QUESTIONS = [
  "Cuales son los 10 casos mas criticos",
  "Por que SIN-00003 es de alto riesgo",
  "Analiza los proveedores con mas alertas",
  "Que ciudades tienen mayor concentracion de fraude",
  "Explica las 7 reglas de deteccion de fraude",
];

function OnlineIndicator() {
  return (
    <div className="flex items-center gap-2">
      <div className="relative">
        <div className="h-2.5 w-2.5 bg-green-500 rounded-full"></div>
        <div className="absolute inset-0 h-2.5 w-2.5 bg-green-500 rounded-full animate-pulse"></div>
      </div>
      <span className="text-xs font-medium text-green-700 bg-green-50 px-2 py-1 rounded">
        En linea
      </span>
    </div>
  );
}

export function AiAgent() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hola. Soy el asistente antifraude de FraudIA. Puedo ayudarte a analizar los siniestros, identificar patrones sospechosos y explicar los scores de riesgo. Como puedo ayudarte hoy?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [usedSuggestions, setUsedSuggestions] = useState<Set<string>>(new Set());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (text: string = input) => {
    if (!text.trim() || loading) return;

    const userMessage: Message = {
      role: "user",
      content: text,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "ngrok-skip-browser-warning": "true",
        },
        body: JSON.stringify({ pregunta: text }),
      });

      if (!response.ok) throw new Error("Error en respuesta del servidor");

      const data = await response.json();
      const assistantMessage: Message = {
        role: "assistant",
        content: data.answer || data.respuesta || "No pude procesar tu pregunta",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error:", error);
      const errorMessage: Message = {
        role: "assistant",
        content:
          "Lo siento, hubo un error procesando tu pregunta. Intenta de nuevo.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestedQuestion = (question: string) => {
    setUsedSuggestions((prev) => new Set([...prev, question]));
    handleSend(question);
  };

  const availableSuggestions = SUGGESTED_QUESTIONS.filter(
    (q) => !usedSuggestions.has(q)
  ).slice(0, 3);

  return (
    <div className="space-y-4">
      {/* Header Panel */}
      <div className="flex flex-col gap-1">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-semibold text-foreground">Agente IA</h2>
            <p className="text-sm text-muted-foreground">
              Consulta en lenguaje natural sobre los siniestros
            </p>
          </div>
          <OnlineIndicator />
        </div>
      </div>

      {/* Chat Container */}
      <div className="rounded-lg border border-border bg-white shadow-sm overflow-hidden flex flex-col h-[650px]">
        {/* Chat Header */}
        <div
          className="px-6 py-4 flex items-center gap-3"
          style={{ background: "linear-gradient(90deg, #1B3A6B 0%, #00AEEF 100%)" }}
        >
          <Bot className="h-5 w-5 text-white" />
          <div>
            <h3 className="font-semibold text-white">Asistente Antifraude FraudIA</h3>
            <p className="text-xs text-blue-100">Powered by Groq + Llama 3.3</p>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto bg-blue-50 p-6 space-y-4">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`flex gap-3 max-w-sm ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
                {msg.role === "assistant" && (
                  <div className="h-8 w-8 rounded-full bg-gradient-to-br from-[#1B3A6B] to-[#00AEEF] flex items-center justify-center flex-shrink-0">
                    <Bot className="h-4 w-4 text-white" />
                  </div>
                )}

                <div>
                  <div
                    className={`rounded-lg px-4 py-3 ${
                      msg.role === "user"
                        ? "bg-[#1B3A6B] text-white rounded-br-none"
                        : "bg-white border border-border text-foreground rounded-bl-none"
                    }`}
                  >
                    <p className="text-sm leading-relaxed">{msg.content}</p>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {msg.timestamp.toLocaleTimeString("es-ES", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="flex gap-3">
                <div className="h-8 w-8 rounded-full bg-gradient-to-br from-[#1B3A6B] to-[#00AEEF] flex items-center justify-center flex-shrink-0">
                  <Bot className="h-4 w-4 text-white" />
                </div>
                <div className="bg-white border border-border rounded-lg px-4 py-3 rounded-bl-none">
                  <p className="text-sm text-muted-foreground">
                    Analizando datos
                    <span className="inline-block ml-1 w-4">
                      <span className="animate-bounce" style={{ animationDelay: "0ms" }}>
                        .
                      </span>
                      <span className="animate-bounce" style={{ animationDelay: "150ms" }}>
                        .
                      </span>
                      <span className="animate-bounce" style={{ animationDelay: "300ms" }}>
                        .
                      </span>
                    </span>
                  </p>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Questions */}
        {availableSuggestions.length > 0 && (
          <div className="border-t border-border px-6 py-3 bg-white">
            <p className="text-xs text-muted-foreground mb-2 font-medium">Preguntas sugeridas:</p>
            <div className="flex flex-wrap gap-2">
              {availableSuggestions.map((question, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSuggestedQuestion(question)}
                  disabled={loading}
                  className="text-xs px-3 py-1.5 rounded-full border border-[#00AEEF] bg-white text-[#1B3A6B] hover:bg-blue-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="border-t border-border bg-white px-6 py-4 flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSend()}
            placeholder="Escribe tu pregunta..."
            disabled={loading}
            className="flex-1 px-4 py-2 rounded-lg border border-border bg-white text-sm focus:outline-none focus:ring-2 focus:ring-[#00AEEF] focus:ring-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
            className="h-10 w-10 rounded-lg bg-gradient-to-br from-[#1B3A6B] to-[#00AEEF] text-white hover:shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
