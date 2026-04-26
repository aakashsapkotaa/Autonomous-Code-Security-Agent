/**
 * Admin API helper — same pattern as api.ts but for /api/admin/* endpoints.
 */
import { supabase } from './supabaseClient';

function getBase(): string {
  // Works in browser (Vite injects import.meta.env at build time)
  // @ts-ignore
  const url = typeof import.meta !== 'undefined'
    // @ts-ignore
    ? (import.meta.env?.VITE_PUBLIC_API_URL ?? import.meta.env?.PUBLIC_API_URL)
    : undefined;
  return url || 'http://localhost:8000';
}

async function adminHeaders(): Promise<Record<string, string>> {
  const { data: { session } } = await supabase.auth.getSession();
  const h: Record<string, string> = { 'Content-Type': 'application/json' };
  if (session?.user?.id) {
    h['x-user-id'] = session.user.id;
  }
  console.debug('[adminApi] user-id:', session?.user?.id ?? 'none');
  return h;
}

export async function adminGet<T = unknown>(path: string): Promise<T> {
  const base = getBase();
  const url = `${base}/api/admin${path}`;
  console.debug('[adminApi] GET', url);
  let res: Response;
  try {
    res = await fetch(url, { headers: await adminHeaders() });
  } catch (e: any) {
    console.error('[adminApi] network error on GET', url, e);
    throw new Error(`Network error: cannot reach ${base}. Is the backend running?`);
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    console.error('[adminApi] GET', url, res.status, body);
    throw new Error(body.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function adminPut<T = unknown>(path: string, body: unknown): Promise<T> {
  const base = getBase();
  const url = `${base}/api/admin${path}`;
  console.debug('[adminApi] PUT', url, body);
  let res: Response;
  try {
    res = await fetch(url, {
      method: 'PUT',
      headers: await adminHeaders(),
      body: JSON.stringify(body),
    });
  } catch (e: any) {
    console.error('[adminApi] network error on PUT', url, e);
    throw new Error(`Network error: cannot reach ${base}. Is the backend running?`);
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    console.error('[adminApi] PUT', url, res.status, err);
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function adminPost<T = unknown>(path: string, body: unknown = {}): Promise<T> {
  const base = getBase();
  const url = `${base}/api/admin${path}`;
  console.debug('[adminApi] POST', url, body);
  let res: Response;
  try {
    res = await fetch(url, {
      method: 'POST',
      headers: await adminHeaders(),
      body: JSON.stringify(body),
    });
  } catch (e: any) {
    console.error('[adminApi] network error on POST', url, e);
    throw new Error(`Network error: cannot reach ${base}. Is the backend running?`);
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    console.error('[adminApi] POST', url, res.status, err);
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function adminDelete<T = unknown>(path: string): Promise<T> {
  const base = getBase();
  const url = `${base}/api/admin${path}`;
  console.debug('[adminApi] DELETE', url);
  let res: Response;
  try {
    res = await fetch(url, {
      method: 'DELETE',
      headers: await adminHeaders(),
    });
  } catch (e: any) {
    console.error('[adminApi] network error on DELETE', url, e);
    throw new Error(`Network error: cannot reach ${base}. Is the backend running?`);
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    console.error('[adminApi] DELETE', url, res.status, err);
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}
