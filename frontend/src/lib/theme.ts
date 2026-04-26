/**
 * Global theme manager for SecureShift.
 *
 * Strategy:
 *   - Tailwind darkMode: 'class' — we toggle `dark` on <html>
 *   - CSS custom properties in app.css respond to html.dark / html:not(.dark)
 *   - localStorage persists the choice across reloads
 *   - app.html inline script applies the class before CSS loads (no flash)
 *   - This module provides a reactive Svelte store + imperative helpers
 */

import { writable, get } from 'svelte/store';

export type ThemeValue = 'dark' | 'light' | 'system';

const STORAGE_KEY = 'secureshift-theme';

// ── Helpers ───────────────────────────────────────────────────────────────────

function isServer(): boolean {
  return typeof window === 'undefined';
}

function systemPrefersDark(): boolean {
  if (isServer()) return true;
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

function resolveIsDark(t: ThemeValue): boolean {
  if (t === 'dark')   return true;
  if (t === 'light')  return false;
  return systemPrefersDark();
}

/** Write the dark/light class to <html> and update color-scheme. */
function applyToDOM(t: ThemeValue): void {
  if (isServer()) return;
  const isDark = resolveIsDark(t);
  const html = document.documentElement;
  html.classList.toggle('dark', isDark);
  html.style.colorScheme = isDark ? 'dark' : 'light';
}

function readStorage(): ThemeValue {
  if (isServer()) return 'dark';
  return (localStorage.getItem(STORAGE_KEY) as ThemeValue) || 'dark';
}

function writeStorage(t: ThemeValue): void {
  if (isServer()) return;
  localStorage.setItem(STORAGE_KEY, t);
}

// ── Store ─────────────────────────────────────────────────────────────────────

const _store = writable<ThemeValue>(readStorage());

// Apply on module load (browser only) — covers SvelteKit client-side navigation
if (!isServer()) {
  applyToDOM(readStorage());

  // Re-apply when OS preference changes (only matters in 'system' mode)
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (get(_store) === 'system') applyToDOM('system');
  });
}

// ── Public API ────────────────────────────────────────────────────────────────

/** Reactive store — use `$theme` in Svelte components. */
export const theme = { subscribe: _store.subscribe };

/**
 * Set a new theme, apply it to the DOM immediately, and persist to localStorage.
 * Call this from the settings page when the user clicks a theme option.
 */
export function applyTheme(t: ThemeValue): void {
  _store.set(t);
  writeStorage(t);
  applyToDOM(t);
}

/** Read the persisted theme without subscribing. */
export function getStoredTheme(): ThemeValue {
  return readStorage();
}
