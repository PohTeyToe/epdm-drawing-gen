import type {
  Drawing,
  DrawingListResponse,
  DisciplineOption,
  GenerateRequest,
} from "./types";

const ENV_URL = (import.meta.env.VITE_API_URL as string | undefined) ?? "";

function baseUrl(): string {
  if (ENV_URL) return ENV_URL.replace(/\/$/, "");
  return "/api";
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${baseUrl()}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new Error(`${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export interface ListParams {
  page?: number;
  size?: number;
  sort_by?: string;
  descending?: boolean;
  discipline?: string;
  search?: string;
}

export function listDrawings(params: ListParams = {}): Promise<DrawingListResponse> {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") qs.set(k, String(v));
  });
  const suffix = qs.toString() ? `?${qs.toString()}` : "";
  return request<DrawingListResponse>(`/drawings${suffix}`);
}

export function getDrawing(id: string): Promise<Drawing> {
  return request<Drawing>(`/drawings/${encodeURIComponent(id)}`);
}

export function generateDrawing(payload: GenerateRequest): Promise<Drawing> {
  return request<Drawing>(`/drawings/generate`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listDisciplines(): Promise<DisciplineOption[]> {
  return request<DisciplineOption[]>(`/disciplines`);
}

export function listDrawingTypes(): Promise<string[]> {
  return request<string[]>(`/drawing-types`);
}

export function apiBaseUrl(): string {
  return baseUrl();
}
