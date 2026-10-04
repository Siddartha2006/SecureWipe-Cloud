const API = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";
export const token = () => typeof window === "undefined" ? "" : sessionStorage.getItem("securewipe_token") || "";
export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API}/api${path}`, { ...init, headers: { ...(init.body instanceof FormData ? {} : {"Content-Type":"application/json"}), ...(token() ? {Authorization:`Bearer ${token()}`} : {}), ...init.headers } });
  if (!response.ok) { const body = await response.json().catch(() => ({})); throw new Error(body.detail || `Request failed (${response.status})`); }
  return response.json();
}
export { API };
