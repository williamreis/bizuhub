/**
 * Cliente HTTP para a API BizuHub.
 * Token JWT em sessionStorage (não usar localStorage para reduzir janela de XSS).
 * Nunca colocar credenciais ou chaves de API no frontend.
 */

const getBaseUrl = (): string => {
  if (typeof window !== "undefined") {
    return process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  }
  return process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
};

const getToken = (): string | null => {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem("bizuhub_token");
};

export type LoginPayload = { username: string; password: string };
export type SignupPayload = { username: string; email: string; password: string };

async function request<T>(
  path: string,
  options: RequestInit & { params?: Record<string, string> } = {}
): Promise<T> {
  const { params, ...init } = options;
  const url = new URL(path.startsWith("http") ? path : getBaseUrl() + path);
  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  }
  const token = getToken();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string>),
  };
  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(url.toString(), { ...init, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(Array.isArray(err.detail) ? err.detail[0]?.msg : err.detail ?? res.statusText);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  async login(payload: LoginPayload) {
    const data = await request<{ access_token: string; token_type: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    if (typeof window !== "undefined" && data.access_token) {
      sessionStorage.setItem("bizuhub_token", data.access_token);
    }
    return data;
  },

  logout() {
    if (typeof window !== "undefined") sessionStorage.removeItem("bizuhub_token");
  },

  async signup(payload: SignupPayload) {
    return request<{ id: number; username: string; email: string; created_at: string }>(
      "/auth/signup",
      { method: "POST", body: JSON.stringify(payload) }
    );
  },

  async getRecommendations(limit = 10) {
    return request<{ items: Array<{ item_type: string; item_id: string; title: string; description?: string; image_url?: string }> }>(
      `/recommendations?limit=${encodeURIComponent(limit)}`
    );
  },

  async getHistory(limit = 50, offset = 0) {
    return request<{ items: unknown[]; total: number }>(
      `/history?limit=${limit}&offset=${offset}`
    );
  },

  async postInteraction(item: { item_type: string; item_id: string; item_title: string; metadata?: object }) {
    return request<unknown>("/interactions", {
      method: "POST",
      body: JSON.stringify(item),
    });
  },

  async chat(message: string) {
    return request<{ reply: string }>("/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    });
  },

  async getGuestRecommendations(limit = 10) {
    return request<{ items: Array<{ item_type: string; item_id: string; title: string; description?: string; image_url?: string }> }>(
      `/recommendations/guest?limit=${encodeURIComponent(limit)}`
    );
  },

  async chatGuest(message: string) {
    return request<{ reply: string }>("/chat/guest", {
      method: "POST",
      body: JSON.stringify({ message }),
    });
  },

  isAuthenticated(): boolean {
    return !!getToken();
  },
};
