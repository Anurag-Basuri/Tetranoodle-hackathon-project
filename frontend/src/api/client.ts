// Base API URL with trailing slash cleanup for reliable routing
const rawBase = import.meta.env.VITE_API_URL || '';
const API_BASE = rawBase.replace(/\/+$/, '');

export class ApiError extends Error {
  status: number;
  code: string;
  detail: string;
  errors: any[];

  constructor(status: number, code: string, detail: string, errors: any[] = []) {
    super(detail || code || `Request failed with status ${status}`);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.detail = detail;
    this.errors = errors;
  }
}

export function getStoredToken(profileId?: string): string | null {
  if (profileId) {
    const token = localStorage.getItem(`scholarpilot_token_${profileId}`);
    if (token) return token;
  }
  return localStorage.getItem('scholarpilot_access_token');
}

export function storeToken(profileId: string, token: string): void {
  localStorage.setItem('scholarpilot_access_token', token);
  localStorage.setItem(`scholarpilot_token_${profileId}`, token);
  localStorage.setItem('scholarpilot_profile_id', profileId);
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  profileId?: string,
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const headers = new Headers(options.headers || {});

  // Inject capability token from storage
  const token = getStoredToken(profileId);
  if (token && !headers.has('X-Access-Token')) {
    headers.set('X-Access-Token', token);
  }

  // Set default JSON Content-Type if payload is present and not multipart
  if (options.body && !(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorData: any = null;
    try {
      errorData = await response.json();
    } catch {
      errorData = null;
    }

    const code = errorData?.code || 'UNKNOWN_ERROR';
    const detail = errorData?.detail || errorData?.title || response.statusText;
    const errors = errorData?.errors || [];

    throw new ApiError(response.status, code, detail, errors);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json() as Promise<T>;
}
