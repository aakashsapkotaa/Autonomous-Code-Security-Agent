<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { supabase } from '$lib/supabaseClient';
  import { page } from '$app/stores';

  onMount(async () => {
    // Supabase puts the token in the URL hash — let the client parse it
    const { data: { session } } = await supabase.auth.getSession();

    // Check if this is a password recovery flow
    const type = $page.url.searchParams.get('type');
    const hashParams = new URLSearchParams(window.location.hash.replace('#', ''));
    const accessToken = hashParams.get('access_token');
    const tokenType   = hashParams.get('type') || type;

    if (tokenType === 'recovery' && accessToken) {
      // Set the session from the recovery token so the user can update password
      await supabase.auth.setSession({
        access_token:  accessToken,
        refresh_token: hashParams.get('refresh_token') || '',
      });
      goto('/auth/reset-password');
      return;
    }

    if (session) {
      goto('/dashboard');
    } else {
      goto('/');
    }
  });
</script>

<div class="min-h-screen bg-[#060914] flex items-center justify-center">
  <div class="flex flex-col items-center gap-4">
    <div class="w-8 h-8 border-2 border-neon-cyan/20 border-t-neon-cyan rounded-full animate-spin"></div>
    <p class="text-sm text-white/40">Authenticating...</p>
  </div>
</div>
