export const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5000";

export type ApiResult<T> =
  | { ok: true; data: T }
  | { ok: false; error: string; status: number };

const TOKEN_KEY = "debttracker_token";

export function getAuthToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setAuthToken(token: string | null) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null
): Promise<ApiResult<T>> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> | undefined),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
    });

    let payload: any = null;
    try {
      payload = await response.json();
    } catch {
      payload = null;
    }

    if (!response.ok) {
      return {
        ok: false,
        status: response.status,
        error: payload?.error || response.statusText || "Request failed",
      };
    }

    return { ok: true, data: payload as T };
  } catch (error) {
    return { ok: false, status: 0, error: "Network error" };
  }
}

export function apiGet<T>(path: string, token?: string | null) {
  return apiRequest<T>(path, { method: "GET" }, token);
}

export function apiPost<T>(path: string, body: any, token?: string | null) {
  return apiRequest<T>(
    path,
    {
      method: "POST",
      body: JSON.stringify(body ?? {}),
    },
    token
  );
}

export function apiPut<T>(path: string, body: any, token?: string | null) {
  return apiRequest<T>(
    path,
    {
      method: "PUT",
      body: JSON.stringify(body ?? {}),
    },
    token
  );
}
