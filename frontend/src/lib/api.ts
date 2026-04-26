/**
 * API helper — injects X-User-Id from the active Supabase session.
 *
 * NOTE: $env/static/public cannot be imported from plain .ts lib files in
 * SvelteKit — it only works inside .svelte files or +page/+layout files.
 * We read the env var via window.__SVELTEKIT_ENV__ or fall back to a
 * hardcoded default so the module works everywhere.
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

async function authHeaders(): Promise<Record<string, string>> {
  const { data: { session } } = await supabase.auth.getSession();
  const h: Record<string, string> = { 'Content-Type': 'application/json' };
  if (session?.user?.id) {
    h['x-user-id'] = session.user.id;
  }
  console.debug('[api] user-id:', session?.user?.id ?? 'none');
  return h;
}

export async function apiGet<T = unknown>(path: string): Promise<T> {
  const base = getBase();
  const url = `${base}${path}`;
  console.debug('[api] GET', url);
  let res: Response;
  try {
    res = await fetch(url, { headers: await authHeaders() });
  } catch (e: any) {
    console.error('[api] network error on GET', url, e);
    throw new Error(`Network error: cannot reach ${base}. Is the backend running?`);
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    console.error('[api] GET', url, res.status, body);
    throw new Error(body.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function apiPut<T = unknown>(path: string, body: unknown): Promise<T> {
  const base = getBase();
  const url = `${base}${path}`;
  console.debug('[api] PUT', url, body);
  let res: Response;
  try {
    res = await fetch(url, {
      method: 'PUT',
      headers: await authHeaders(),
      body: JSON.stringify(body),
    });
  } catch (e: any) {
    console.error('[api] network error on PUT', url, e);
    throw new Error(`Network error: cannot reach ${base}. Is the backend running?`);
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    console.error('[api] PUT', url, res.status, err);
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function apiPost<T = unknown>(path: string, body: unknown = {}): Promise<T> {
  const base = getBase();
  const url = `${base}${path}`;
  console.debug('[api] POST', url, body);
  let res: Response;
  try {
    res = await fetch(url, {
      method: 'POST',
      headers: await authHeaders(),
      body: JSON.stringify(body),
    });
  } catch (e: any) {
    console.error('[api] network error on POST', url, e);
    throw new Error(`Network error: cannot reach ${base}. Is the backend running?`);
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    console.error('[api] POST', url, res.status, err);
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}
