"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "../services/api";

export default function SignupPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (password.length < 8) {
      setError("Senha deve ter pelo menos 8 caracteres");
      return;
    }
    setLoading(true);
    try {
      await api.signup({ username: username.trim(), email: email.trim(), password });
      router.push("/login");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao criar conta");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ padding: "2rem", maxWidth: 400, margin: "0 auto" }}>
      <h1 style={{ marginBottom: "1.5rem" }}>Criar conta</h1>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="username" style={{ display: "block", marginBottom: "0.25rem", color: "#a1a1aa" }}>
            Usuário (letras, números, _ e -)
          </label>
          <input
            id="username"
            type="text"
            autoComplete="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            minLength={3}
            maxLength={64}
            pattern="[a-zA-Z0-9_-]+"
            style={{ width: "100%", padding: "0.5rem", borderRadius: 6, border: "1px solid #3f3f46", background: "#18181b", color: "#fff" }}
          />
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="email" style={{ display: "block", marginBottom: "0.25rem", color: "#a1a1aa" }}>
            E-mail
          </label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ width: "100%", padding: "0.5rem", borderRadius: 6, border: "1px solid #3f3f46", background: "#18181b", color: "#fff" }}
          />
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="password" style={{ display: "block", marginBottom: "0.25rem", color: "#a1a1aa" }}>
            Senha (mín. 8 caracteres)
          </label>
          <input
            id="password"
            type="password"
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            maxLength={128}
            style={{ width: "100%", padding: "0.5rem", borderRadius: 6, border: "1px solid #3f3f46", background: "#18181b", color: "#fff" }}
          />
        </div>
        {error && <p style={{ color: "#f87171", marginBottom: "1rem", fontSize: "0.875rem" }}>{error}</p>}
        <button
          type="submit"
          disabled={loading}
          style={{ width: "100%", padding: "0.6rem", borderRadius: 6, border: "none", background: "#7c3aed", color: "#fff", cursor: loading ? "not-allowed" : "pointer" }}
        >
          {loading ? "Criando…" : "Criar conta"}
        </button>
      </form>
      <p style={{ marginTop: "1rem", color: "#a1a1aa", fontSize: "0.875rem" }}>
        Já tem conta? <Link href="/login">Entrar</Link>
      </p>
    </main>
  );
}
