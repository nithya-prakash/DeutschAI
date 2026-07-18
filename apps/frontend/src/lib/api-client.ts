import { useAuthStore } from "@/stores/auth-store";
import type { ApiError, TokenResponse } from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export class ApiRequestError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiRequestError";
  }
}

async function refreshAccessToken(): Promise<string | null> {
  const { refreshToken, setTokens, logout } = useAuthStore.getState();
  if (!refreshToken) return null;

  const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!res.ok) {
    logout();
    return null;
  }

  const data: TokenResponse = await res.json();
  setTokens(data.access_token, data.refresh_token);
  return data.access_token;
}

interface RequestOptions extends RequestInit {
  auth?: boolean;
}

export async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { auth = true, headers, ...rest } = options;

  const doFetch = async (token: string | null): Promise<Response> =>
    fetch(`${API_BASE_URL}${path}`, {
      ...rest,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...headers,
      },
    });

  let token = auth ? useAuthStore.getState().accessToken : null;
  let response = await doFetch(token);

  if (auth && response.status === 401) {
    token = await refreshAccessToken();
    if (token) {
      response = await doFetch(token);
    }
  }

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body: ApiError = await response.json();
      detail = body.detail ?? detail;
    } catch {
      // response had no JSON body
    }
    throw new ApiRequestError(response.status, detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}
