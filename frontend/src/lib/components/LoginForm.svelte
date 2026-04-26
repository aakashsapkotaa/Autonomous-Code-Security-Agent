<script lang="ts">
  import { ArrowRight, AlertCircle, CheckCircle, Mail, Lock, User, Eye, EyeOff, ArrowLeft } from 'lucide-svelte';
  import { supabase } from '$lib/supabaseClient';

  let isSignup = false;
  let isForgot = false;   // ← forgot password view
  let loading = false;
  let showPassword = false;
  let showConfirm = false;
  let message: { type: 'error' | 'success'; text: string } | null = null;
  let formData = { name: '', email: '', password: '', confirmPassword: '' };

  // ── Password policy ──────────────────────────────────────────
  const rules = [
    { id: 'len',     label: 'At least 8 characters',          test: (p: string) => p.length >= 8 },
    { id: 'upper',   label: 'One uppercase letter (A–Z)',      test: (p: string) => /[A-Z]/.test(p) },
    { id: 'lower',   label: 'One lowercase letter (a–z)',      test: (p: string) => /[a-z]/.test(p) },
    { id: 'number',  label: 'One number (0–9)',                test: (p: string) => /\d/.test(p) },
    { id: 'special', label: 'One special character (!@#$…)',   test: (p: string) => /[^A-Za-z0-9]/.test(p) },
  ];

  $: checks      = rules.map(r => ({ ...r, passed: r.test(formData.password) }));
  $: passedCount = checks.filter(c => c.passed).length;
  $: strength    = passedCount <= 1 ? 'weak' : passedCount <= 3 ? 'fair' : passedCount === 4 ? 'good' : 'strong';
  $: policyMet   = passedCount === rules.length;
  $: showPolicy  = isSignup && formData.password.length > 0;

  const strengthMeta: Record<string, { label: string; color: string; width: string }> = {
    weak:   { label: 'Weak',   color: '#ef4444', width: '20%'  },
    fair:   { label: 'Fair',   color: '#f59e0b', width: '45%'  },
    good:   { label: 'Good',   color: '#3a86ff', width: '70%'  },
    strong: { label: 'Strong', color: '#00d9ff', width: '100%' },
  };
  // ─────────────────────────────────────────────────────────────

  function reset() {
    formData = { name: '', email: '', password: '', confirmPassword: '' };
    message = null;
    showPassword = false;
    showConfirm = false;
  }

  function goToForgot() {
    isForgot = true;
    message = null;
  }

  function backToLogin() {
    isForgot = false;
    isSignup = false;
    reset();
  }

  // ── Forgot password ──────────────────────────────────────────
  async function handleForgot(e: Event) {
    e.preventDefault();
    if (!formData.email) {
      message = { type: 'error', text: 'Please enter your email address.' };
      return;
    }
    loading = true; message = null;
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(formData.email, {
        redirectTo: `${window.location.origin}/auth/callback?type=recovery`,
      });
      if (error) throw error;
      message = {
        type: 'success',
        text: `Password reset email sent to ${formData.email}. Check your inbox.`,
      };
      formData.email = '';
    } catch (err: any) {
      message = { type: 'error', text: err.message || 'Failed to send reset email.' };
    } finally {
      loading = false;
    }
  }

  async function handleSubmit(e: Event) {
    e.preventDefault();
    loading = true; message = null;
    try {
      if (isSignup) {
        if (!policyMet) {
          message = { type: 'error', text: 'Password does not meet the security requirements.' };
          loading = false; return;
        }
        if (formData.password !== formData.confirmPassword) {
          message = { type: 'error', text: 'Passwords do not match' }; loading = false; return;
        }
        const { error } = await supabase.auth.signUp({
          email: formData.email, password: formData.password,
          options: { emailRedirectTo: `${window.location.origin}/dashboard`, data: { full_name: formData.name } },
        });
        if (error) throw error;
        message = { type: 'success', text: 'Account created! Check your email to verify.' };
        reset();
      } else {
        const { error } = await supabase.auth.signInWithPassword({
          email: formData.email, password: formData.password
        });
        if (error) throw error;
        message = { type: 'success', text: 'Authenticated. Redirecting to dashboard...' };
        setTimeout(() => { window.location.href = '/dashboard'; }, 1200);
      }
    } catch (err: any) {
      message = { type: 'error', text: err.message || 'Authentication failed. Please try again.' };
    } finally { loading = false; }
  }
</script>

<div class="login-card">
  <!-- Card glow ring -->
  <div class="card-glow" aria-hidden="true"></div>

  <div class="relative z-10 p-8 sm:p-10">

    <!-- ══════════════════════════════════════════════════════ -->
    <!-- FORGOT PASSWORD VIEW                                   -->
    <!-- ══════════════════════════════════════════════════════ -->
    {#if isForgot}

      <div class="mb-8">
        <button type="button" class="back-btn" on:click={backToLogin}>
          <ArrowLeft class="w-3.5 h-3.5" /> Back to sign in
        </button>
        <div class="flex items-center gap-2 mt-5 mb-4">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-neon-cyan to-neon-blue flex items-center justify-center">
            <Mail class="w-4 h-4 text-dark-bg" />
          </div>
          <span class="text-xs font-bold uppercase tracking-[0.2em] text-neon-cyan/80">Password Reset</span>
        </div>
        <h2 class="text-2xl sm:text-3xl font-headline font-bold text-white leading-tight">
          Forgot your password?
        </h2>
        <p class="mt-2 text-sm text-on-surface-variant">
          Enter your email and we'll send you a reset link.
        </p>
      </div>

      {#if message}
        <div class="mb-6 p-3.5 rounded-xl flex items-start gap-3 border text-sm
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

      <form class="space-y-4" on:submit={handleForgot}>
        <div class="field-group">
          <label class="field-label" for="forgot-email">Email Address</label>
          <div class="field-wrap">
            <Mail class="field-icon" />
            <input
              bind:value={formData.email}
              id="forgot-email" type="email"
              placeholder="you@company.com"
              required
              class="field-input"
            />
          </div>
        </div>

        <div class="pt-2">
          <button type="submit" disabled={loading} class="submit-btn">
            {#if loading}
              <span class="loader"></span>
              <span>Sending...</span>
            {:else}
              <span>Send Reset Link</span>
              <ArrowRight class="w-4 h-4" />
            {/if}
          </button>
        </div>
      </form>

      <div class="mt-6 text-center">
        <button type="button" on:click={backToLogin}
          class="text-sm text-on-surface-variant hover:text-white transition-colors">
          Remember your password?
          <span class="text-neon-cyan font-semibold ml-1">Sign in</span>
        </button>
      </div>

    <!-- ══════════════════════════════════════════════════════ -->
    <!-- SIGN IN / SIGN UP VIEW                                 -->
    <!-- ══════════════════════════════════════════════════════ -->
    {:else}

      <!-- Header -->
      <div class="mb-8">
        <div class="flex items-center gap-2 mb-5">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-neon-cyan to-neon-blue flex items-center justify-center">
            <Lock class="w-4 h-4 text-dark-bg" />
          </div>
          <span class="text-xs font-bold uppercase tracking-[0.2em] text-neon-cyan/80">
            {isSignup ? 'New Account' : 'Secure Access'}
          </span>
        </div>
        <h2 class="text-2xl sm:text-3xl font-headline font-bold text-white leading-tight">
          {isSignup ? 'Create your account' : 'Welcome back'}
        </h2>
        <p class="mt-2 text-sm text-on-surface-variant">
          {isSignup
            ? 'Start securing your repositories in minutes'
            : 'Sign in to your security dashboard'}
        </p>
      </div>

      <!-- Alert -->
      {#if message}
        <div class="mb-6 p-3.5 rounded-xl flex items-start gap-3 border text-sm
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

      <!-- Form -->
      <form class="space-y-4" on:submit={handleSubmit}>

        {#if isSignup}
          <div class="field-group">
            <label class="field-label" for="name">Full Name</label>
            <div class="field-wrap">
              <User class="field-icon" />
              <input
                bind:value={formData.name}
                id="name" type="text"
                placeholder="Jane Smith"
                required={isSignup}
                class="field-input"
              />
            </div>
          </div>
        {/if}

        <div class="field-group">
          <label class="field-label" for="email">Email Address</label>
          <div class="field-wrap">
            <Mail class="field-icon" />
            <input
              bind:value={formData.email}
              id="email" type="email"
              placeholder="you@company.com"
              required
              class="field-input"
            />
          </div>
        </div>

        <div class="field-group">
          <div class="flex justify-between items-center mb-1.5">
            <label class="field-label !mb-0" for="password">Password</label>
            {#if !isSignup}
              <button type="button" class="forgot-link" on:click={goToForgot}>
                Forgot password?
              </button>
            {/if}
          </div>
          <div class="field-wrap">
            <Lock class="field-icon" />
            <input
              bind:value={formData.password}
              id="password"
              type={showPassword ? 'text' : 'password'}
              placeholder="••••••••••"
              required minlength="6"
              class="field-input pr-11"
            />
            <button type="button" class="field-eye" on:click={() => showPassword = !showPassword} tabindex="-1">
              {#if showPassword}<EyeOff class="w-4 h-4" />{:else}<Eye class="w-4 h-4" />{/if}
            </button>
          </div>
        </div>

        {#if isSignup}
          {#if showPolicy}
            <div class="policy-box">
              <div class="flex items-center justify-between mb-2">
                <span class="text-[10px] font-semibold uppercase tracking-wider text-on-surface-variant/60">
                  Password strength
                </span>
                <span class="text-[11px] font-bold" style="color: {strengthMeta[strength].color}">
                  {strengthMeta[strength].label}
                </span>
              </div>
              <div class="strength-track">
                <div class="strength-bar"
                  style="width: {strengthMeta[strength].width}; background: {strengthMeta[strength].color};">
                </div>
              </div>
              <ul class="mt-3 space-y-1.5">
                {#each checks as c}
                  <li class="flex items-center gap-2 text-[11px] transition-colors duration-200
                    {c.passed ? 'text-neon-cyan/90' : 'text-on-surface-variant/50'}">
                    <span class="rule-dot {c.passed ? 'rule-pass' : 'rule-fail'}">
                      {#if c.passed}✓{:else}·{/if}
                    </span>
                    {c.label}
                  </li>
                {/each}
              </ul>
            </div>
          {/if}

          <div class="field-group">
            <label class="field-label" for="confirmPassword">Confirm Password</label>
            <div class="field-wrap">
              <Lock class="field-icon" />
              <input
                bind:value={formData.confirmPassword}
                id="confirmPassword"
                type={showConfirm ? 'text' : 'password'}
                placeholder="••••••••••"
                required={isSignup} minlength="6"
                class="field-input pr-11"
              />
              <button type="button" class="field-eye" on:click={() => showConfirm = !showConfirm} tabindex="-1">
                {#if showConfirm}<EyeOff class="w-4 h-4" />{:else}<Eye class="w-4 h-4" />{/if}
              </button>
            </div>
          </div>
        {/if}

        <div class="pt-2">
          <button type="submit" disabled={loading || (isSignup && !policyMet)} class="submit-btn">
            {#if loading}
              <span class="loader"></span>
              <span>Authenticating...</span>
            {:else}
              <span>{isSignup ? 'Create Account' : 'Sign In'}</span>
              <ArrowRight class="w-4 h-4 transition-transform group-hover:translate-x-1" />
            {/if}
          </button>
        </div>
      </form>

      <!-- Toggle -->
      <div class="mt-6 text-center">
        <button
          type="button"
          disabled={loading}
          on:click={() => { isSignup = !isSignup; reset(); }}
          class="text-sm text-on-surface-variant hover:text-white transition-colors"
        >
          {#if isSignup}
            Already have an account?
            <span class="text-neon-cyan font-semibold ml-1">Sign in</span>
          {:else}
            Don't have an account?
            <span class="text-neon-cyan font-semibold ml-1">Sign up free</span>
          {/if}
        </button>
      </div>

      <!-- Divider + social proof -->
      <div class="mt-8 pt-6 border-t border-white/[0.06]">
        <div class="flex items-center justify-center gap-4 text-[11px] text-on-surface-variant/60">
          <span class="flex items-center gap-1.5">
            <span class="w-1.5 h-1.5 rounded-full bg-green-400"></span>
            256-bit encryption
          </span>
          <span class="w-px h-3 bg-white/10"></span>
          <span class="flex items-center gap-1.5">
            <span class="w-1.5 h-1.5 rounded-full bg-neon-cyan"></span>
            Supabase Auth
          </span>
          <span class="w-px h-3 bg-white/10"></span>
          <span class="flex items-center gap-1.5">
            <span class="w-1.5 h-1.5 rounded-full bg-neon-purple"></span>
            SOC 2 Ready
          </span>
        </div>
      </div>

    {/if}
  </div>
</div>

<style>
  .login-card {
    position: relative;
    border-radius: 1.25rem;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(8, 11, 24, 0.85);
    backdrop-filter: blur(24px);
    box-shadow:
      0 0 0 1px rgba(0, 217, 255, 0.06),
      0 32px 80px rgba(0, 0, 0, 0.5),
      inset 0 1px 0 rgba(255, 255, 255, 0.06);
    transition: box-shadow 0.4s ease;
  }
  .login-card:hover {
    box-shadow:
      0 0 0 1px rgba(0, 217, 255, 0.12),
      0 32px 80px rgba(0, 0, 0, 0.5),
      0 0 60px rgba(0, 217, 255, 0.06),
      inset 0 1px 0 rgba(255, 255, 255, 0.08);
  }

  .card-glow {
    position: absolute;
    inset: -1px;
    border-radius: 1.3rem;
    background: linear-gradient(135deg, rgba(0,217,255,0.08), transparent 50%, rgba(157,78,221,0.06));
    pointer-events: none;
    z-index: 0;
  }

  .field-group { display: flex; flex-direction: column; }

  .field-label {
    display: block;
    margin-bottom: 0.375rem;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(184, 191, 214, 0.8);
  }

  .field-wrap {
    position: relative;
    display: flex;
    align-items: center;
  }

  :global(.field-icon) {
    position: absolute;
    left: 0.875rem;
    width: 1rem;
    height: 1rem;
    color: rgba(184, 191, 214, 0.4);
    pointer-events: none;
    flex-shrink: 0;
  }

  .field-input {
    width: 100%;
    padding: 0.75rem 0.875rem 0.75rem 2.5rem;
    border-radius: 0.625rem;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(255, 255, 255, 0.04);
    color: #f0f4ff;
    font-size: 0.875rem;
    outline: none;
    transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
  }
  .field-input::placeholder { color: rgba(107, 118, 161, 0.6); }
  .field-input:hover {
    border-color: rgba(255, 255, 255, 0.14);
    background: rgba(255, 255, 255, 0.06);
  }
  .field-input:focus {
    border-color: rgba(0, 217, 255, 0.5);
    background: rgba(0, 217, 255, 0.04);
    box-shadow: 0 0 0 3px rgba(0, 217, 255, 0.08);
  }

  .field-eye {
    position: absolute;
    right: 0.875rem;
    color: rgba(184, 191, 214, 0.4);
    cursor: pointer;
    transition: color 0.2s;
    background: none;
    border: none;
    padding: 0;
    display: flex;
    align-items: center;
  }
  .field-eye:hover { color: rgba(184, 191, 214, 0.8); }

  .submit-btn {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.875rem 1.5rem;
    border-radius: 0.75rem;
    font-weight: 600;
    font-size: 0.9rem;
    color: #060914;
    background: linear-gradient(135deg, #00d9ff 0%, #3a86ff 100%);
    border: none;
    cursor: pointer;
    transition: opacity 0.2s, transform 0.15s, box-shadow 0.3s;
    box-shadow: 0 4px 20px rgba(0, 217, 255, 0.25);
  }
  .submit-btn:hover:not(:disabled) {
    opacity: 0.92;
    transform: translateY(-1px);
    box-shadow: 0 8px 30px rgba(0, 217, 255, 0.4);
  }
  .submit-btn:active:not(:disabled) { transform: translateY(0); }
  .submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }

  .loader {
    width: 1rem;
    height: 1rem;
    border: 2px solid rgba(6, 9, 20, 0.3);
    border-top-color: #060914;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    flex-shrink: 0;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* ── Password policy ── */
  .policy-box {
    padding: 0.875rem 1rem;
    border-radius: 0.75rem;
    border: 1px solid rgba(255, 255, 255, 0.07);
    background: rgba(255, 255, 255, 0.03);
    animation: fadeIn 0.2s ease;
  }

  .strength-track {
    height: 3px;
    border-radius: 9999px;
    background: rgba(255, 255, 255, 0.08);
    overflow: hidden;
  }

  .strength-bar {
    height: 100%;
    border-radius: 9999px;
    transition: width 0.4s ease, background 0.4s ease;
  }

  .rule-dot {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1rem;
    height: 1rem;
    border-radius: 50%;
    font-size: 0.6rem;
    font-weight: 700;
    flex-shrink: 0;
    transition: background 0.2s, color 0.2s;
  }

  .rule-pass {
    background: rgba(0, 217, 255, 0.15);
    color: #00d9ff;
  }

  .rule-fail {
    background: rgba(255, 255, 255, 0.06);
    color: rgba(184, 191, 214, 0.4);
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(-4px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .forgot-link {
    font-size: 0.6875rem;
    color: rgba(184,191,214,0.6);
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
    transition: color 0.2s;
  }
  .forgot-link:hover { color: #00d9ff; }

  .back-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    font-size: 0.75rem;
    font-weight: 500;
    color: rgba(184,191,214,0.5);
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
    transition: color 0.2s;
  }
  .back-btn:hover { color: white; }
</style>
