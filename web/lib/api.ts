import { ApiClientError, type AnalyzeResult, type JobView } from "@/lib/types";
import { messageFor } from "@/lib/messages";

const base = () => (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${base()}${path}`, { credentials: "include", ...init });
  } catch {
    throw new ApiClientError("blocked", "Can't reach the server. Check your connection and try again.");
  }
  const text = await response.text();
  let body: { code?: string; message?: string; position?: number } = {};
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      throw new ApiClientError("blocked", "The server could not complete that request. Try again.");
    }
  }
  if (!response.ok) {
    throw new ApiClientError(
      body.code || "blocked",
      messageFor(body.code, body.message, body.position),
      body.position,
    );
  }
  return body as T;
}

export function analyze(url: string, turnstileToken?: string | null): Promise<AnalyzeResult> {
  return request<AnalyzeResult>("/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, turnstile_token: turnstileToken || undefined }),
  });
}

export function createJob(url: string, formatId: string, itemIndex: number | null, turnstileToken?: string | null): Promise<JobView> {
  return request<JobView>("/api/jobs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      url,
      format_id: formatId,
      item_index: itemIndex,
      turnstile_token: turnstileToken || undefined,
    }),
  });
}

export function getJob(id: string): Promise<JobView> {
  return request<JobView>(`/api/jobs/${id}`);
}

export function cancelJob(id: string): Promise<JobView> {
  return request<JobView>(`/api/jobs/${id}`, { method: "DELETE" });
}

export type SessionState = { signed_in: boolean; username: string | null };

export function getSession(): Promise<SessionState> {
  return request<SessionState>("/api/auth/session");
}

export function loginInstagram(username: string, password: string, turnstileToken?: string | null): Promise<{ status: string; username?: string; challenge_id?: string }> {
  return request("/api/auth/instagram/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password, turnstile_token: turnstileToken || undefined }),
  });
}

export function verifyInstagram(username: string, challengeId: string, code: string, turnstileToken?: string | null): Promise<{ status: string; username: string }> {
  return request("/api/auth/instagram/verify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, challenge_id: challengeId, code, turnstile_token: turnstileToken || undefined }),
  });
}

export function logoutInstagram(): Promise<{ status: string }> {
  return request("/api/auth/logout", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
}

export function absoluteDownload(path: string): string {
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  return `${base()}${path}`;
}
