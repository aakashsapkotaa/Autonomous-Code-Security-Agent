<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { supabase } from '$lib/supabaseClient';
  import { Lock, Eye, EyeOff, CheckCircle, AlertCircle, ArrowRight } from 'lucide-svelte';

  let password = '';
  let confirm  = '';
  let showPw   = false;
  let showCf   = false;
  let loading  = false;
  let message: { type: 'error' | 'success'; text: string } | null = null;
  let ready    = false;

  const rules = [
    { label: 'At least 8 characters',        test: (p: string) => p.length >= 8 },
    { label: 'One uppercase letter',          test: (p: string) => /[A-Z]/.test(p) },
    { label: 'One lowercase letter',          test: (p: string) => /[a-z]/.test(p) },
    { label: 'One number',                    test: (p: string) => /\d/.test(p) },
    { label: 'One special character',         test: (p: string) => /[^A-Za-z0-9]/.test(p) },
  ];

  $: checks   = rules.map(r => ({ ...r, passed: r.test(password) }));
  $: policyMet = checks.every(c => c.passed);

  onMount(async () => {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) {
      // No active session — link may be expired
      message = { type: 'error', text: 'Reset link is invalid or expired. Please request a new one.' };
    } else {
      ready = true;
    }
  });

  async function handleReset(e: Event) {
    e.preventDefault();
    if (!policyMet) {
      message = { type: 'error', text: 'Password does not meet the requirements.' };
      return;
    }
    if (password !== confirm) {
      message = { type: 'error', text: 'Passwords do not match.' };
      return;
    }
    loading = true; message = null;
    try {
      const { error } = await supabase.auth.updateUser({ password });
      if (error) throw error;
      message = { type: 'success', text: 'Password updated! Redirecting to dashboard...' };
      setTimeout(() => goto('/dashboard'), 1500);
    } catch (err: any) {
      message = { type: 'error', text: err.message || 'Failed to update password.' };
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head><title>Reset Password — SecureShift</title></svelte:head>

<div class="min-h-screen bg-[#060914] flex items-center justify-center px-4">
  <div class="reset-card">
    <div class="card-glow" aria-hidden="true"></div>

    <div class="relative z-10 p-8 sm:p-10">
      <!-- Header -->
      <div class="flex items-center gap-2 mb-5">
        <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-neon-cyan to-neon-blue flex items-center justify-center">
          <Lock class="w-4 h-4 text-[#060914]" />
        </div>
        <span class="text-xs font-bold uppercase tracking-[0.2em] text-neon-cyan/80">Set New Password</span>
      </div>
      <h2 class="text-2xl font-bold text-white mb-1">Choose a new password</h2>
      <p class="text-sm text-white/50 mb-7">Make it strong and unique.</p>

      <!-- Alert -->
      {#if message}
        <div class="mb-5 p-3.5 rounded-xl flex items-start gap-3 border text-sm
          {message.type === 'error'
            ? 'bg-red-500/10 border-red-500/30 text-red-400'
            : 'bg-neon-cyan/10 border-neon-cyan/30 text-neon-cyan/90'}">
          {#if message.type === 'error'}
            <AlertCircle class="w-4 h-4 flex-shrink-0 mt-0.5" />
          {:else}
            <CheckCircle class="w-4 h-4 flex-shrink-0 mt-0.5" />
          {/if}
          <span>{message.text}</span>
        </div>
      {/if}

      {#if ready}
        <form class="space-y-4" on:submit={handleReset}>
          <!-- New password -->
          <div>
            <label class="field-label" for="pw">New Password</label>
            <div class="field-wrap">
              <Lock class="field-icon" />
              <input bind:value={password} id="pw"
                type={showPw ? 'text' : 'password'}
                placeholder="••••••••••" required
                class="field-input pr-11" />
              <button type="button" class="field-eye" on:click={() => showPw = !showPw} tabindex="-1">
                {#if showPw}<EyeOff class="w-4 h-4" />{:else}<Eye class="w-4 h-4" />{/if}
              </button>
            </div>
          </div>

          <!-- Requirements -->
          {#if password.length > 0}
            <ul class="space-y-1.5 px-1">
              {#each checks as c}
                <li class="flex items-center gap-2 text-[11px]
                  {c.passed ? 'text-neon-cyan/90' : 'text-white/30'}">
                  <span class="rule-dot {c.passed ? 'rule-pass' : 'rule-fail'}">
                    {c.passed ? '✓' : '·'}
                  </span>
                  {c.label}
                </li>
              {/each}
            </ul>
          {/if}

          <!-- Confirm -->
          <div>
            <label class="field-label" for="cf">Confirm Password</label>
            <div class="field-wrap">
              <Lock class="field-icon" />
              <input bind:value={confirm} id="cf"
                type={showCf ? 'text' : 'password'}
                placeholder="••••••••••" required
                class="field-input pr-11" />
              <button type="button" class="field-eye" on:click={() => showCf = !showCf} tabindex="-1">
                {#if showCf}<EyeOff class="w-4 h-4" />{:else}<Eye class="w-4 h-4" />{/if}
              </button>
            </div>
          </div>

          <div class="pt-1">
            <button type="submit" disabled={loading || !policyMet} class="submit-btn">
              {#if loading}
                <span class="loader"></span> Updating...
              {:else}
                Update Password <ArrowRight class="w-4 h-4" />
              {/if}
            </button>
          </div>
        </form>
      {:else if !message}
        <div class="flex items-center gap-3 text-white/40 text-sm">
          <div class="w-5 h-5 border-2 border-white/10 border-t-neon-cyan rounded-full animate-spin"></div>
          Verifying reset link...
        </div>
      {:else}
        <a href="/" class="text-sm text-neon-cyan hover:underline">← Back to sign in</a>
      {/if}
    </div>
  </div>
</div>

<style>
  .reset-card {
    position: relative; width: 100%; max-width: 420px;
    border-radius: 1.25rem;
    border: 1px solid rgba(255,255,255,0.08);
    background: rgba(8,11,24,0.9);
    backdrop-filter: blur(24px);
    box-shadow: 0 32px 80px rgba(0,0,0,0.5);
  }
  .card-glow {
    position: absolute; inset: -1px; border-radius: 1.3rem;
    background: linear-gradient(135deg, rgba(0,217,255,0.08), transparent 50%, rgba(157,78,221,0.06));
    pointer-events: none; z-index: 0;
  }
  .field-label {
    display: block; margin-bottom: 0.375rem;
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; color: rgba(184,191,214,0.8);
  }
  .field-wrap { position: relative; display: flex; align-items: center; }
  :global(.field-icon) {
    position: absolute; left: 0.875rem;
    width: 1rem; height: 1rem;
    color: rgba(184,191,214,0.4); pointer-events: none;
  }
  .field-input {
    width: 100%; padding: 0.75rem 0.875rem 0.75rem 2.5rem;
    border-radius: 0.625rem; border: 1px solid rgba(255,255,255,0.08);
    background: rgba(255,255,255,0.04); color: #f0f4ff; font-size: 0.875rem; outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  .field-input::placeholder { color: rgba(107,118,161,0.6); }
  .field-input:focus { border-color: rgba(0,217,255,0.5); box-shadow: 0 0 0 3px rgba(0,217,255,0.08); }
  .field-eye {
    position: absolute; right: 0.875rem;
    color: rgba(184,191,214,0.4); cursor: pointer;
    background: none; border: none; padding: 0; display: flex; align-items: center;
  }
  .field-eye:hover { color: rgba(184,191,214,0.8); }
  .rule-dot {
    display: inline-flex; align-items: center; justify-content: center;
    width: 1rem; height: 1rem; border-radius: 50%;
    font-size: 0.6rem; font-weight: 700; flex-shrink: 0;
  }
  .rule-pass { background: rgba(0,217,255,0.15); color: #00d9ff; }
  .rule-fail { background: rgba(255,255,255,0.06); color: rgba(184,191,214,0.4); }
  .submit-btn {
    width: 100%; display: flex; align-items: center; justify-content: center; gap: 0.5rem;
    padding: 0.875rem 1.5rem; border-radius: 0.75rem;
    font-weight: 600; font-size: 0.9rem; color: #060914;
    background: linear-gradient(135deg, #00d9ff, #3a86ff);
    border: none; cursor: pointer; transition: opacity 0.2s, transform 0.15s;
    box-shadow: 0 4px 20px rgba(0,217,255,0.25);
  }
  .submit-btn:hover:not(:disabled) { opacity: 0.92; transform: translateY(-1px); }
  .submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }
  .loader {
    width: 1rem; height: 1rem;
    border: 2px solid rgba(6,9,20,0.3); border-top-color: #060914;
    border-radius: 50%; animation: spin 0.7s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>
