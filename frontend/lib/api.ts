const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export type Website = {
  id: number;
  name: string;
  url: string;
  last_modified_text: string | null;
  last_checked_at: string | null;
  last_changed_at: string | null;
};

export type NotificationLog = {
  id: number;
  website_id: number;
  message: string;
  status: string;
  created_at: string;
};

export type Settings = {
  recipient_phone_number: string | null;
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  listWebsites: () => request<Website[]>("/api/websites"),
  addWebsite: (url: string, name?: string) =>
    request<Website>("/api/websites", {
      method: "POST",
      body: JSON.stringify({ url, name }),
    }),
  deleteWebsite: (id: number) =>
    request<{ ok: boolean }>(`/api/websites/${id}`, { method: "DELETE" }),
  checkWebsite: (id: number) =>
    request<Website>(`/api/websites/${id}/check`, { method: "POST" }),
  getSettings: () => request<Settings>("/api/settings"),
  updateSettings: (recipient_phone_number: string) =>
    request<Settings>("/api/settings", {
      method: "POST",
      body: JSON.stringify({ recipient_phone_number }),
    }),
  listLogs: () => request<NotificationLog[]>("/api/logs"),
};
