import { ApiClientError, type AnalyzeResult, type JobView } from "@/lib/types";
import { messageFor } from "@/lib/messages";

const base = () => (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${base()}${path}`, init);
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

export function absoluteDownload(path: string): string {
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  return `${base()}${path}`;
}
