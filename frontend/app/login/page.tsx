"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "../services/api";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.login({ username: username.trim(), password });
      router.push("/dashboard");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao entrar");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ padding: "2rem", maxWidth: 400, margin: "0 auto" }}>
      <h1 style={{ marginBottom: "1.5rem" }}>Entrar</h1>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="username" style={{ display: "block", marginBottom: "0.25rem", color: "#a1a1aa" }}>
            Usuário
          </label>
          <input
            id="username"
            type="text"
            autoComplete="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            maxLength={64}
            style={{ width: "100%", padding: "0.5rem", borderRadius: 6, border: "1px solid #3f3f46", background: "#18181b", color: "#fff" }}
          />
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="password" style={{ display: "block", marginBottom: "0.25rem", color: "#a1a1aa" }}>
            Senha
          </label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: "100%", padding: "0.5rem", borderRadius: 6, border: "1px solid #3f3f46", background: "#18181b", color: "#fff" }}
          />
        </div>
        {error && <p style={{ color: "#f87171", marginBottom: "1rem", fontSize: "0.875rem" }}>{error}</p>}
        <button
          type="submit"
          disabled={loading}
          style={{ width: "100%", padding: "0.6rem", borderRadius: 6, border: "none", background: "#7c3aed", color: "#fff", cursor: loading ? "not-allowed" : "pointer" }}
        >
          {loading ? "Entrando…" : "Entrar"}
        </button>
      </form>
      <p style={{ marginTop: "1rem", color: "#a1a1aa", fontSize: "0.875rem" }}>
        Não tem conta? <Link href="/signup">Criar conta</Link>
      </p>
    </main>
  );
}
