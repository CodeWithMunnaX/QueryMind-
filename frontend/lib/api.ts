import type {
  AuthResponse,
  AuthUser,
  ChatRequest,
  ChatResponse,
  DashboardResponse,
  DatabaseSchema,
  Dataset,
  HistoryResponse,
  QueryResult,
} from "@/types/analytics";
import { clearToken, getToken } from "./token";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken();
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...init?.headers,
      },
    });
  } catch {
    throw new ApiError("Could not reach the QueryMind backend. Is it running?", 0);
  }

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // response wasn't JSON; fall back to statusText
    }
    if (res.status === 401) {
      // Expired/invalid token — drop it so the UI falls back to the logged-out state.
      clearToken();
    }
    throw new ApiError(detail, res.status);
  }

  return res.json() as Promise<T>;
}

export const api = {
  register: (email: string, password: string) =>
    request<AuthResponse>("/api/auth/register", { method: "POST", body: JSON.stringify({ email, password }) }),

  login: (email: string, password: string) =>
    request<AuthResponse>("/api/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),

  me: () => request<AuthUser>("/api/auth/me"),

  chat: (payload: ChatRequest) =>
    request<ChatResponse>("/api/chat", { method: "POST", body: JSON.stringify(payload) }),

  runQuery: (sql: string) =>
    request<QueryResult>("/api/query", { method: "POST", body: JSON.stringify({ sql }) }),

  getDashboard: () => request<DashboardResponse>("/api/dashboard"),

  getSchema: () => request<DatabaseSchema>("/api/schema"),

  getDatasets: () => request<Dataset[]>("/api/datasets"),

  getHistory: (conversationId?: string) =>
    request<HistoryResponse>(`/api/history${conversationId ? `?conversation_id=${conversationId}` : ""}`),

  health: () => request<{ status: string; database: string; llm: string }>("/api/health"),
};
