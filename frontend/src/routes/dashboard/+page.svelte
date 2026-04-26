<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { supabase } from '$lib/supabaseClient';
  import AuroraBackground from '$lib/components/AuroraBackground.svelte';
  import Dashboard from '$lib/components/Dashboard.svelte';
  import type { User } from '@supabase/supabase-js';

  let user: User | null = null;
  let loading = true;

  onMount(async () => {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) { goto('/'); return; }
    user = session.user;
    loading = false;
    supabase.auth.onAuthStateChange((_e, s) => { if (!s) goto('/'); else user = s.user; });
  });
</script>

<svelte:head><title>Dashboard — SecureShift</title></svelte:head>

<div class="min-h-screen flex flex-col bg-[#060914]">
  <AuroraBackground />
  <div class="relative z-10 flex flex-col min-h-screen">
    {#if loading}
      <div class="flex-1 flex items-center justify-center">
        <div class="flex flex-col items-center gap-4">
          <div class="w-10 h-10 border-2 border-neon-cyan/20 border-t-neon-cyan rounded-full animate-spin"></div>
          <p class="text-sm text-on-surface-variant/60">Loading...</p>
        </div>
      </div>
    {:else if user}
      <Dashboard {user} />
    {/if}
  </div>
</div>
