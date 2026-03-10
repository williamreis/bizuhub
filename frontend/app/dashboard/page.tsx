"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "../services/api";

type RecItem = { item_type: string; item_id: string; title: string; description?: string; image_url?: string };

export default function DashboardPage() {
  const router = useRouter();
  const [recommendations, setRecommendations] = useState<RecItem[]>([]);
  const [chatMessage, setChatMessage] = useState("");
  const [chatReply, setChatReply] = useState("");
  const [loadingRec, setLoadingRec] = useState(true);
  const [loadingChat, setLoadingChat] = useState(false);

  useEffect(() => {
    if (!api.isAuthenticated()) {
      router.push("/login");
      return;
    }
    api.getRecommendations(10).then((r) => {
      setRecommendations(r.items ?? []);
    }).catch(() => {
      setRecommendations([]);
    }).finally(() => setLoadingRec(false));
  }, [router]);

  const handleLogout = () => {
    api.logout();
    router.push("/");
    router.refresh();
  };

  const handleChat = async (e: React.FormEvent) => {
    e.preventDefault();
    const msg = chatMessage.trim();
    if (!msg || loadingChat) return;
    setLoadingChat(true);
    setChatReply("");
    try {
      const res = await api.chat(msg);
      setChatReply(res.reply ?? "");
      setChatMessage("");
    } catch {
      setChatReply("Erro ao enviar mensagem. Tente novamente.");
    } finally {
      setLoadingChat(false);
    }
  };

  if (!api.isAuthenticated()) return null;

  return (
    <main style={{ padding: "2rem", maxWidth: 900, margin: "0 auto" }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
        <h1 style={{ fontSize: "1.5rem" }}>BizuHub</h1>
        <nav>
          <Link href="/" style={{ marginRight: "1rem" }}>Início</Link>
          <button type="button" onClick={handleLogout} style={{ background: "none", border: "none", color: "#a78bfa", cursor: "pointer", padding: 0 }}>
            Sair
          </button>
        </nav>
      </header>

      <section style={{ marginBottom: "2rem" }}>
        <h2 style={{ fontSize: "1.25rem", marginBottom: "1rem" }}>Recomendações</h2>
        {loadingRec ? (
          <p style={{ color: "#a1a1aa" }}>Carregando…</p>
        ) : recommendations.length === 0 ? (
          <p style={{ color: "#a1a1aa" }}>Nenhuma recomendação no momento. Configure as chaves de API no backend (TMDb, Google Books).</p>
        ) : (
          <ul style={{ listStyle: "none", padding: 0, display: "grid", gap: "1rem" }}>
            {recommendations.map((item) => (
              <li
                key={`${item.item_type}-${item.item_id}`}
                style={{ padding: "1rem", background: "#18181b", borderRadius: 8, border: "1px solid #27272a" }}
              >
                <div style={{ display: "flex", gap: "1rem", alignItems: "flex-start" }}>
                  {item.image_url && (
                    <img src={item.image_url} alt="" width={80} height={120} style={{ objectFit: "cover", borderRadius: 4 }} />
                  )}
                  <div>
                    <strong>{item.title}</strong>
                    <span style={{ marginLeft: "0.5rem", color: "#71717a", fontSize: "0.875rem" }}>({item.item_type})</span>
                    {item.description && <p style={{ margin: "0.5rem 0 0", fontSize: "0.875rem", color: "#a1a1aa" }}>{item.description.slice(0, 150)}…</p>}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h2 style={{ fontSize: "1.25rem", marginBottom: "1rem" }}>Chat com a IA</h2>
        <form onSubmit={handleChat}>
          <textarea
            value={chatMessage}
            onChange={(e) => setChatMessage(e.target.value.slice(0, 2000))}
            placeholder="Pergunte sobre filmes, séries ou livros..."
            rows={2}
            maxLength={2000}
            style={{ width: "100%", padding: "0.5rem", borderRadius: 6, border: "1px solid #3f3f46", background: "#18181b", color: "#fff", resize: "vertical" }}
          />
          <button
            type="submit"
            disabled={loadingChat || !chatMessage.trim()}
            style={{ marginTop: "0.5rem", padding: "0.5rem 1rem", borderRadius: 6, border: "none", background: "#7c3aed", color: "#fff", cursor: loadingChat ? "not-allowed" : "pointer" }}
          >
            {loadingChat ? "Enviando…" : "Enviar"}
          </button>
        </form>
        {chatReply && (
          <div style={{ marginTop: "1rem", padding: "1rem", background: "#18181b", borderRadius: 8, border: "1px solid #27272a", whiteSpace: "pre-wrap" }}>
            {chatReply}
          </div>
        )}
      </section>
    </main>
  );
}
