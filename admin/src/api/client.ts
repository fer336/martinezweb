import type { Catalogo, Trabajo, TrabajoInput } from '../types';

const API_URL = import.meta.env.VITE_API_URL as string;
const TOKEN_KEY = 'cms_token';

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers = new Headers(options.headers);
  if (token) headers.set('Authorization', `Bearer ${token}`);
  if (options.body && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const data = await response.json();
      detail = data.detail ?? JSON.stringify(data);
    } catch {
      // ignore body parse errors
    }
    throw new ApiError(response.status, detail);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export async function login(username: string, password: string): Promise<void> {
  const data = await request<{ access_token: string }>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
  setToken(data.access_token);
}

export function listTrabajos(): Promise<Trabajo[]> {
  return request('/admin/trabajos');
}

export function listCategorias(): Promise<Catalogo[]> {
  return request('/admin/categorias');
}

export function listZonas(): Promise<Catalogo[]> {
  return request('/admin/zonas');
}

export function createCategoria(nombre: string): Promise<Catalogo> {
  return request('/admin/categorias', { method: 'POST', body: JSON.stringify({ nombre }) });
}

export function createTrabajo(data: TrabajoInput): Promise<Trabajo> {
  return request('/admin/trabajos', { method: 'POST', body: JSON.stringify(data) });
}

export function updateTrabajo(id: number, data: TrabajoInput): Promise<Trabajo> {
  return request(`/admin/trabajos/${id}`, { method: 'PUT', body: JSON.stringify(data) });
}

export function deleteTrabajo(id: number): Promise<void> {
  return request(`/admin/trabajos/${id}`, { method: 'DELETE' });
}

export async function uploadImage(file: File, prefix: 'trabajos' | 'hero' = 'trabajos'): Promise<string> {
  const form = new FormData();
  form.append('file', file);
  form.append('prefix', prefix);
  const data = await request<{ url: string }>('/admin/uploads', { method: 'POST', body: form });
  return data.url;
}

export function publish(): Promise<{ status: string }> {
  return request('/admin/publish', { method: 'POST' });
}

export function getConfig(): Promise<{ hero_image_url: string | null }> {
  return request('/admin/config');
}

export function updateConfig(heroImageUrl: string): Promise<{ hero_image_url: string | null }> {
  return request('/admin/config', { method: 'PUT', body: JSON.stringify({ hero_image_url: heroImageUrl }) });
}

export { ApiError };
