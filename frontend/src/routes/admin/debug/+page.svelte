<script lang="ts">
  import { onMount } from 'svelte';
  import { supabase } from '$lib/supabaseClient';
  import { adminGet } from '$lib/adminApi';
  import { apiGet } from '$lib/api';

  let session: any = null;
  let user: any = null;
  let apiUrl = '';
  let testResults: any = {};
  let loading = true;

  onMount(async () => {
    // Get API URL
    // @ts-ignore
    apiUrl = import.meta.env?.PUBLIC_API_URL || 'http://localhost:8000';
    
    // Get session
    const { data } = await supabase.auth.getSession();
    session = data.session;
    user = session?.user;

    // Run tests
    await runTests();
    loading = false;
  });

  async function runTests() {
    testResults = {
      session: null,
      healthCheck: null,
      profileCheck: null,
      adminOverview: null,
      headers: null,
    };

    // Test 1: Session
    try {
      testResults.session = {
        status: 'success',
        data: {
          userId: user?.id,
          email: user?.email,
          hasSession: !!session,
        }
      };
    } catch (e: any) {
      testResults.session = { status: 'error', error: e.message };
    }

    // Test 2: Health check
    try {
      const health = await fetch(`${apiUrl}/api/health`);
      testResults.healthCheck = {
        status: health.ok ? 'success' : 'error',
        data: await health.json(),
      };
    } catch (e: any) {
      testResults.healthCheck = { status: 'error', error: e.message };
    }

    // Test 3: Profile endpoint (requires auth)
    try {
      const profile = await apiGet('/profile');
      testResults.profileCheck = {
        status: 'success',
        data: profile,
      };
    } catch (e: any) {
      testResults.profileCheck = { status: 'error', error: e.message };
    }

    // Test 4: Admin overview
    try {
      const overview = await adminGet('/overview');
      testResults.adminOverview = {
        status: 'success',
        data: overview,
      };
    } catch (e: any) {
      testResults.adminOverview = { status: 'error', error: e.message };
    }

    // Test 5: Check headers
    try {
      const { data: { session: s } } = await supabase.auth.getSession();
      testResults.headers = {
        status: 'success',
        data: {
          'x-user-id': s?.user?.id || 'NOT SET',
          'Content-Type': 'application/json',
        }
      };
    } catch (e: any) {
      testResults.headers = { status: 'error', error: e.message };
    }
  }

  function getStatusColor(status: string) {
    return status === 'success' ? '#34d399' : '#f87171';
  }
</script>

<svelte:head><title>Admin Debug — SecureShift</title></svelte:head>

<div class="space-y-6">
  <div>
    <h1 class="text-xl font-headline font-bold text-white">Admin Access Debug</h1>
    <p class="text-xs text-on-surface-variant/50 mt-0.5">Diagnostic information for troubleshooting</p>
  </div>

  {#if loading}
    <div class="text-center py-8">
      <div class="w-8 h-8 border-2 border-neon-cyan/20 border-t-neon-cyan rounded-full animate-spin mx-auto"></div>
    </div>
  {:else}
    <!-- Configuration -->
    <div class="debug-card">
      <h2 class="debug-title">Configuration</h2>
      <div class="debug-grid">
        <div class="debug-item">
          <span class="debug-label">API URL:</span>
          <span class="debug-value">{apiUrl}</span>
        </div>
        <div class="debug-item">
          <span class="debug-label">Supabase URL:</span>
          <span class="debug-value">{import.meta.env?.PUBLIC_SUPABASE_URL || 'NOT SET'}</span>
        </div>
      </div>
    </div>

    <!-- Test Results -->
    {#each Object.entries(testResults) as [key, result]}
      <div class="debug-card">
        <div class="flex items-center justify-between mb-3">
          <h2 class="debug-title capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</h2>
          <span 
            class="px-2 py-0.5 rounded text-[10px] font-semibold"
            style="background: {getStatusColor(result.status)}22; color: {getStatusColor(result.status)}"
          >
            {result.status}
          </span>
        </div>
        
        {#if result.error}
          <div class="debug-error">{result.error}</div>
        {:else if result.data}
          <pre class="debug-pre">{JSON.stringify(result.data, null, 2)}</pre>
        {/if}
      </div>
    {/each}

    <!-- Actions -->
    <div class="debug-card">
      <h2 class="debug-title">Actions</h2>
      <div class="flex gap-2">
        <button class="debug-btn" on:click={runTests}>
          Rerun Tests
        </button>
        <button class="debug-btn" on:click={() => location.href = '/admin'}>
          Back to Admin
        </button>
      </div>
    </div>

    <!-- Instructions -->
    <div class="debug-card bg-neon-cyan/5 border-neon-cyan/20">
      <h2 class="debug-title text-neon-cyan">Troubleshooting Steps</h2>
      <ol class="space-y-2 text-xs text-on-surface-variant/70">
        <li>1. Ensure backend is running on {apiUrl}</li>
        <li>2. Check that you're logged in (Session test should pass)</li>
        <li>3. Verify your user has admin role in the database</li>
        <li>4. Run: <code class="debug-code">python backend/test_admin_access.py --promote your@email.com</code></li>
        <li>5. Check browser console for detailed error messages</li>
      </ol>
    </div>
  {/if}
</div>

<style>
  .debug-card {
    padding: 1.25rem;
    border-radius: 0.875rem;
    border: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.02);
  }

  .debug-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: white;
    margin-bottom: 0.75rem;
  }

  .debug-grid {
    display: grid;
    gap: 0.75rem;
  }

  .debug-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem;
    background: rgba(255,255,255,0.03);
    border-radius: 0.5rem;
  }

  .debug-label {
    font-size: 0.75rem;
    color: rgba(184,191,214,0.6);
  }

  .debug-value {
    font-size: 0.75rem;
    font-family: monospace;
    color: #00d9ff;
  }

  .debug-error {
    padding: 0.75rem;
    background: rgba(248,113,113,0.1);
    border: 1px solid rgba(248,113,113,0.2);
    border-radius: 0.5rem;
    color: #f87171;
    font-size: 0.75rem;
    font-family: monospace;
  }

  .debug-pre {
    padding: 0.75rem;
    background: rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 0.5rem;
    color: #34d399;
    font-size: 0.7rem;
    overflow-x: auto;
    max-height: 300px;
  }

  .debug-btn {
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    font-size: 0.75rem;
    font-weight: 500;
    background: rgba(0,217,255,0.1);
    border: 1px solid rgba(0,217,255,0.2);
    color: #00d9ff;
    cursor: pointer;
    transition: all 0.15s;
  }

  .debug-btn:hover {
    background: rgba(0,217,255,0.2);
  }

  .debug-code {
    padding: 0.125rem 0.375rem;
    background: rgba(0,0,0,0.3);
    border-radius: 0.25rem;
    font-family: monospace;
    font-size: 0.7rem;
    color: #34d399;
  }
</style>
