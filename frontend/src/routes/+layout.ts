// Client-side layout load — runs on every route.
// Exposes the Supabase session to all pages via `data.session`.
import { browser } from '$app/environment';
import type { LayoutLoad } from './$types';

export const ssr = false; // pure SPA — no server rendering needed

export const load: LayoutLoad = async () => {
  // Session is read in +layout.svelte via onMount; nothing to do here.
  // Returning an empty object keeps the type system happy.
  return {};
};
