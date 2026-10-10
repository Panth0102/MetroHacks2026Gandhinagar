// Typed fetch wrapper. All server access goes through here — no scattered fetch
// calls in components. Does NOT fabricate fallback business data on failure; it
// surfaces a structured ApiError so the UI can show an honest error state.

const BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"
).replace(/\/$/, "");

export class ApiError extends Error {
  status: number;
  detail: unknown;
  constructor(status: number, message: string, detail?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

type QueryValue = string | number | boolean | null | undefined;

function buildQuery(params?: Record<string, QueryValue>): string {
  if (!params) return "";
  const sp = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== null && value !== undefined && value !== "") {
      sp.append(key, String(value));
    }
  }
  const s = sp.toString();
  return s ? `?${s}` : "";
}

async function request<T>(
  path: string,
  init?: RequestInit,
  signal?: AbortSignal,
): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      ...init,
      signal,
      headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    });
  } catch (err) {
    if ((err as Error).name === "AbortError") throw err;
    throw new ApiError(
      0,
      "Cannot reach the API. Is the backend running on " + BASE_URL + "?",
    );
  }

  if (!res.ok) {
    let detail: unknown;
    try {
      detail = await res.json();
    } catch {
      detail = await res.text().catch(() => undefined);
    }
    const message =
      (detail && typeof detail === "object" && "detail" in detail
        ? String((detail as { detail: unknown }).detail)
        : undefined) ?? `Request failed with status ${res.status}`;
    throw new ApiError(res.status, message, detail);
  }

  return (await res.json()) as T;
}

export const api = {
  baseUrl: BASE_URL,
  /** Absolute URL for file endpoints (PDF/CSV) opened/downloaded directly by the browser. */
  downloadUrl(path: string, params?: Record<string, QueryValue>): string {
    return `${BASE_URL}${path}${buildQuery(params)}`;
  },
  get<T>(
    path: string,
    params?: Record<string, QueryValue>,
    signal?: AbortSignal,
  ): Promise<T> {
    return request<T>(`${path}${buildQuery(params)}`, { method: "GET" }, signal);
  },
  post<T>(path: string, body: unknown, signal?: AbortSignal): Promise<T> {
    return request<T>(
      path,
      { method: "POST", body: JSON.stringify(body) },
      signal,
    );
  },
  patch<T>(path: string, body: unknown, signal?: AbortSignal): Promise<T> {
    return request<T>(
      path,
      { method: "PATCH", body: JSON.stringify(body) },
      signal,
    );
  },
};
