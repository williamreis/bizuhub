"use client";

import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import { api } from "./services/api";

type Message = { role: "user" | "assistant"; text: string };

type RecItem = {
  item_type: string;
  item_id: string;
  title: string;
  description?: string;
  image_url?: string;
};

export default function Home() {
  const [auth, setAuth] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<RecItem[]>([]);
  const [recLoading, setRecLoading] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setAuth(api.isAuthenticated());
  }, []);

  useEffect(() => {
    api.getGuestRecommendations(8).then((r) => {
      setRecommendations(r.items ?? []);
    }).catch(() => setRecommendations([])).finally(() => setRecLoading(false));
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text }]);
    setLoading(true);
    try {
      const res = await api.chatGuest(text);
      setMessages((prev) => [...prev, { role: "assistant", text: res.reply ?? "" }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Não foi possível responder. Tente novamente ou faça login para usar o chat completo." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <header
        style={{
          padding: "0.75rem 1.5rem",
          borderBottom: "1px solid #27272a",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexShrink: 0,
        }}
      >
        <h1 style={{ fontSize: "1.25rem", fontWeight: 600, margin: 0 }}>BizuHub</h1>
        <nav style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
          {auth ? (
            <Link href="/dashboard" style={{ fontSize: "0.875rem" }}>Painel</Link>
          ) : (
            <>
              <Link href="/login" style={{ fontSize: "0.875rem" }}>Entrar</Link>
              <Link href="/signup" style={{ fontSize: "0.875rem" }}>Criar conta</Link>
            </>
          )}
        </nav>
      </header>

      <div className="guest-layout">
        <section
          style={{
            display: "flex",
            flexDirection: "column",
            borderRight: "1px solid #27272a",
            minHeight: "calc(100vh - 52px)",
          }}
        >
          <div
            style={{
              padding: "1rem 1.5rem",
              borderBottom: "1px solid #27272a",
              background: "#18181b",
            }}
          >
            <p style={{ margin: 0, fontSize: "0.875rem", color: "#a1a1aa" }}>
              Modo visitante — experimente o chat. Faça login para histórico e recomendações personalizadas.
            </p>
          </div>

          <div
            style={{
              flex: 1,
              overflowY: "auto",
              padding: "1.5rem",
              display: "flex",
              flexDirection: "column",
              gap: "1rem",
            }}
          >
            {messages.length === 0 && (
              <div
                style={{
                  alignSelf: "center",
                  textAlign: "center",
                  color: "#71717a",
                  fontSize: "0.875rem",
                  marginTop: "2rem",
                }}
              >
                <p>Olá! Sou o assistente do BizuHub.</p>
                <p>Pergunte sobre filmes, séries ou livros para começar.</p>
              </div>
            )}
            {messages.map((m, i) => (
              <div
                key={i}
                style={{
                  alignSelf: m.role === "user" ? "flex-end" : "flex-start",
                  maxWidth: "85%",
                }}
              >
                <div
                  style={{
                    padding: "0.75rem 1rem",
                    borderRadius: 12,
                    background: m.role === "user" ? "#7c3aed" : "#27272a",
                    color: m.role === "user" ? "#fff" : "#e4e4e7",
                    fontSize: "0.9375rem",
                    lineHeight: 1.5,
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                  }}
                >
                  {m.text}
                </div>
              </div>
            ))}
            {loading && (
              <div style={{ alignSelf: "flex-start" }}>
                <div
                  style={{
                    padding: "0.75rem 1rem",
                    borderRadius: 12,
                    background: "#27272a",
                    color: "#a1a1aa",
                    fontSize: "0.875rem",
                  }}
                >
                  Pensando…
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form
            onSubmit={sendMessage}
            style={{
              padding: "1rem 1.5rem",
              borderTop: "1px solid #27272a",
              background: "#18181b",
            }}
          >
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value.slice(0, 2000))}
                placeholder="Pergunte sobre filmes, séries ou livros..."
                maxLength={2000}
                disabled={loading}
                style={{
                  flex: 1,
                  padding: "0.65rem 1rem",
                  borderRadius: 8,
                  border: "1px solid #3f3f46",
                  background: "#0f0f12",
                  color: "#fff",
                }}
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                style={{
                  padding: "0.65rem 1.25rem",
                  borderRadius: 8,
                  border: "none",
                  background: "#7c3aed",
                  color: "#fff",
                  cursor: loading ? "not-allowed" : "pointer",
                  fontWeight: 500,
                }}
              >
                Enviar
              </button>
            </div>
          </form>
        </section>

        <aside
          style={{
            padding: "1rem",
            overflowY: "auto",
            background: "#0f0f12",
          }}
        >
          <h2 style={{ fontSize: "0.9375rem", marginBottom: "0.75rem", color: "#a1a1aa" }}>
            Recomendações
          </h2>
          {recLoading ? (
            <p style={{ fontSize: "0.8125rem", color: "#71717a" }}>Carregando…</p>
          ) : recommendations.length === 0 ? (
            <p style={{ fontSize: "0.8125rem", color: "#71717a" }}>
              Nenhuma no momento. Configure TMDb/Google Books no backend.
            </p>
          ) : (
            <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              {recommendations.map((item) => (
                <li
                  key={`${item.item_type}-${item.item_id}`}
                  style={{
                    padding: "0.5rem",
                    background: "#18181b",
                    borderRadius: 8,
                    border: "1px solid #27272a",
                  }}
                >
                  <div style={{ display: "flex", gap: "0.5rem" }}>
                    {item.image_url && (
                      <img
                        src={item.image_url}
                        alt=""
                        width={48}
                        height={72}
                        style={{ objectFit: "cover", borderRadius: 4 }}
                      />
                    )}
                    <div style={{ minWidth: 0, flex: 1 }}>
                      <div style={{ fontSize: "0.8125rem", fontWeight: 500 }}>{item.title}</div>
                      <div style={{ fontSize: "0.75rem", color: "#71717a" }}>{item.item_type}</div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </aside>
      </div>
    </div>
  );
}
