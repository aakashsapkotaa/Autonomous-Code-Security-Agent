<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import { goto, beforeNavigate } from '$app/navigation';
  import { page } from '$app/stores';
  import { supabase } from '$lib/supabaseClient';
  import { applyTheme, getStoredTheme } from '$lib/theme';

  // ── Apply theme synchronously on every render (client-side nav + first load)
  // The app.html inline script handles the very first paint before JS loads.
  if (typeof document !== 'undefined') {
    applyTheme(getStoredTheme());
  }

  // Public routes — accessible without a session
  const PUBLIC_ROUTES = new Set(['/', '/privacy', '/terms', '/auth/callback']);

  function isPublic(path: string): boolean {
    return PUBLIC_ROUTES.has(path) || path.startsWith('/auth/');
  }

  function isDashboard(path: string): boolean {
    return path.startsWith('/dashboard') || path.startsWith('/admin');
  }

  onMount(async () => {
    // ── Initial session check ──────────────────────────────────────────────
    const { data: { session } } = await supabase.auth.getSession();
    const path = $page.url.pathname;

    if (session && isPublic(path) && path !== '/auth/callback') {
      // Logged-in user landed on a public page → send to dashboard
      await goto('/dashboard', { replaceState: true });
      return;
    }

    if (!session && isDashboard(path)) {
      // Unauthenticated user tried to access a protected page → login
      await goto('/', { replaceState: true });
      return;
    }

    // ── Listen for auth state changes ──────────────────────────────────────
    supabase.auth.onAuthStateChange(async (_event, newSession) => {
      const currentPath = $page.url.pathname;

      if (!newSession && isDashboard(currentPath)) {
        // Session expired / signed out while on dashboard
        await goto('/', { replaceState: true });
      }

      if (newSession && isPublic(currentPath) && currentPath !== '/auth/callback') {
        // Session appeared (e.g. OAuth callback) while on public page
        await goto('/dashboard', { replaceState: true });
      }
    });
  });

  // ── Intercept navigations ──────────────────────────────────────────────────
  // Prevents the browser back button from taking a logged-in user to /
  beforeNavigate(async ({ to, cancel }) => {
    if (!to) return;
    const targetPath = to.url.pathname;

    const { data: { session } } = await supabase.auth.getSession();

    if (session && isPublic(targetPath) && targetPath !== '/auth/callback') {
      cancel();
      goto('/dashboard');
      return;
    }

    if (!session && isDashboard(targetPath)) {
      cancel();
      goto('/');
    }
  });
</script>

<slot />
