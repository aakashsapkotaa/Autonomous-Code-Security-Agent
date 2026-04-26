<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { supabase } from '$lib/supabaseClient';
  import { apiGet, apiPut } from '$lib/api';
  import { applyTheme } from '$lib/theme';
  import type { ThemeValue } from '$lib/theme';
  import AuroraBackground from '$lib/components/AuroraBackground.svelte';
  import {
    ArrowLeft, Loader, Save, CheckCircle, Eye, EyeOff,
    Bell, Palette, Key, Shield, User
  } from 'lucide-svelte';

  let loading = true;
  let saving = false;
  let saved = false;
  let error = '';

  // Settings state
  let theme: ThemeValue = 'dark';
  let notifyScanComplete = true;
  let notifyCriticalVuln = true;
  let notifyPrCreated = true;
  let githubToken = '';
  let githubTokenSet = false;
  let nvdApiKey = '';
  let nvdApiKeySet = false;
  let openrouterKey = '';
  let openrouterKeySet = false;

  // Password change
  let currentPassword = '';
  let newPassword = '';
  let confirmPassword = '';
  let showPw = false;
  let pwError = '';
  let pwSaving = false;
  let pwSaved = false;

  // Reveal toggles for API keys
  let showGithub = false;
  let showNvd = false;
  let showOpenrouter = false;

  onMount(async () => {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) { goto('/'); return; }
    await loadSettings();
  });

  async function loadSettings() {
    loading = true;
    try {
      const s: any = await apiGet('/api/settings');
      theme = s.theme as ThemeValue;
      applyTheme(theme);   // apply persisted theme on load
      notifyScanComplete = s.notify_scan_complete;
      notifyCriticalVuln = s.notify_critical_vuln;
      notifyPrCreated = s.notify_pr_created;
      githubTokenSet = s.github_token_set;
      nvdApiKeySet = s.nvd_api_key_set;
      openrouterKeySet = s.openrouter_api_key_set;
    } catch (e: any) { error = e.message; }
    finally { loading = false; }
  }

  async function saveSettings() {
    saving = true; error = '';
    try {
      await apiPut('/api/settings', {
        theme,
        notify_scan_complete: notifyScanComplete,
        notify_critical_vuln: notifyCriticalVuln,
        notify_pr_created: notifyPrCreated,
        ...(githubToken ? { github_token: githubToken } : {}),
        ...(nvdApiKey    ? { nvd_api_key: nvdApiKey }    : {}),
        ...(openrouterKey ? { openrouter_api_key: openrouterKey } : {}),
      });
      saved = true;
      githubToken = ''; nvdApiKey = ''; openrouterKey = '';
      await loadSettings();
      setTimeout(() => saved = false, 2500);
    } catch (e: any) { error = e.message; }
    finally { saving = false; }
  }

  async function changePassword() {
    pwError = '';
    if (newPassword !== confirmPassword) { pwError = 'Passwords do not match'; return; }
    if (newPassword.length < 8) { pwError = 'Password must be at least 8 characters'; return; }
    pwSaving = true;
    try {
      const { error: err } = await supabase.auth.updateUser({ password: newPassword });
      if (err) throw err;
      pwSaved = true;
      currentPassword = ''; newPassword = ''; confirmPassword = '';
      setTimeout(() => pwSaved = false, 2500);
    } catch (e: any) { pwError = e.message; }
    finally { pwSaving = false; }
  }

  const THEMES = [
    { value: 'dark',   label: 'Dark',   desc: 'Cyber dark theme' },
    { value: 'light',  label: 'Light',  desc: 'Light mode' },
    { value: 'system', label: 'System', desc: 'Follow OS preference' },
  ];

  const SECTIONS = [
    { id: 'account',       label: 'Account',       icon: User    },
    { id: 'notifications', label: 'Notifications',  icon: Bell    },
    { id: 'theme',         label: 'Theme',          icon: Palette },
    { id: 'api',           label: 'API Keys',       icon: Key     },
    { id: 'security',      label: 'Security',       icon: Shield  },
  ];

  let activeSection = 'account';
</script>

<svelte:head><title>Settings — SecureShift</title></svelte:head>

<div class="min-h-screen bg-[#060914]">
  <AuroraBackground />
  <div class="relative z-10 max-w-4xl mx-auto px-5 sm:px-8 py-10">

    <a href="/dashboard" class="inline-flex items-center gap-2 text-sm text-on-surface-variant/60 hover:text-neon-cyan transition-colors mb-8">
      <ArrowLeft class="w-4 h-4" /> Back to Dashboard
    </a>

    <h1 class="text-2xl font-headline font-bold text-white mb-6">Settings</h1>

    {#if loading}
      <div class="flex items-center justify-center py-20">
        <Loader class="w-6 h-6 text-neon-cyan animate-spin" />
      </div>
    {:else}
      <div class="flex flex-col lg:flex-row gap-6">

        <!-- Sidebar nav -->
        <nav class="lg:w-48 flex-shrink-0">
          <div class="settings-nav">
            {#each SECTIONS as s}
              <button
                class="nav-item {activeSection === s.id ? 'nav-item-active' : ''}"
                on:click={() => activeSection = s.id}
              >
                <svelte:component this={s.icon} class="w-4 h-4" />
                {s.label}
              </button>
            {/each}
          </div>
        </nav>

        <!-- Content -->
        <div class="flex-1 space-y-4">

          {#if error}
            <p class="text-xs text-red-400 p-3 rounded-lg bg-red-500/10 border border-red-500/20">{error}</p>
          {/if}

          <!-- Account -->
          {#if activeSection === 'account'}
            <div class="settings-card">
              <h2 class="settings-section-title">Account Settings</h2>
              <p class="text-xs text-on-surface-variant/50 mb-5">
                Manage your name and password. Email changes require re-verification.
              </p>

              <div class="space-y-4">
                <div>
                  <label class="field-label">Change Password</label>
                  <div class="space-y-2 mt-1">
                    <div class="relative">
                      <input
                        bind:value={newPassword}
                        type={showPw ? 'text' : 'password'}
                        placeholder="New password (8+ chars)"
                        class="field-input pr-10"
                      />
                      <button type="button" class="pw-eye" on:click={() => showPw = !showPw}>
                        {#if showPw}<EyeOff class="w-4 h-4" />{:else}<Eye class="w-4 h-4" />{/if}
                      </button>
                    </div>
                    <input
                      bind:value={confirmPassword}
                      type="password"
                      placeholder="Confirm new password"
                      class="field-input"
                    />
                  </div>
                  {#if pwError}
                    <p class="text-xs text-red-400 mt-1">{pwError}</p>
                  {/if}
                  <button class="save-btn mt-3" disabled={pwSaving || !newPassword} on:click={changePassword}>
                    {#if pwSaving}<Loader class="w-3.5 h-3.5 animate-spin" /> Updating…
                    {:else if pwSaved}<CheckCircle class="w-3.5 h-3.5" /> Updated!
                    {:else}Update Password{/if}
                  </button>
                </div>
              </div>
            </div>

          <!-- Notifications -->
          {:else if activeSection === 'notifications'}
            <div class="settings-card">
              <h2 class="settings-section-title">Notification Settings</h2>
              <p class="text-xs text-on-surface-variant/50 mb-5">Choose when to receive email notifications.</p>

              <div class="space-y-4">
                <div class="toggle-row">
                  <div>
                    <p class="text-sm font-medium text-white">Scan Complete</p>
                    <p class="text-xs text-on-surface-variant/50">Notify when a security scan finishes</p>
                  </div>
                  <button class="toggle {notifyScanComplete ? 'toggle-on' : ''}" on:click={() => notifyScanComplete = !notifyScanComplete}>
                    <span class="toggle-thumb"></span>
                  </button>
                </div>
                <div class="toggle-row">
                  <div>
                    <p class="text-sm font-medium text-white">Critical Vulnerability</p>
                    <p class="text-xs text-on-surface-variant/50">Alert on CVSS 9.0+ findings</p>
                  </div>
                  <button class="toggle {notifyCriticalVuln ? 'toggle-on' : ''}" on:click={() => notifyCriticalVuln = !notifyCriticalVuln}>
                    <span class="toggle-thumb"></span>
                  </button>
                </div>
                <div class="toggle-row">
                  <div>
                    <p class="text-sm font-medium text-white">PR Created</p>
                    <p class="text-xs text-on-surface-variant/50">Notify when a security fix PR is opened</p>
                  </div>
                  <button class="toggle {notifyPrCreated ? 'toggle-on' : ''}" on:click={() => notifyPrCreated = !notifyPrCreated}>
                    <span class="toggle-thumb"></span>
                  </button>
                </div>
              </div>
            </div>

          <!-- Theme -->
          {:else if activeSection === 'theme'}
            <div class="settings-card">
              <h2 class="settings-section-title">Theme</h2>
              <p class="text-xs text-on-surface-variant/50 mb-4">Changes apply instantly. Save to persist across devices.</p>
              <div class="grid grid-cols-3 gap-3 mt-2">
                {#each THEMES as t}
                  <button
                    class="theme-option {theme === t.value ? 'theme-option-active' : ''}"
                    on:click={() => { theme = t.value as ThemeValue; applyTheme(theme); }}
                  >
                    <span class="theme-preview theme-preview-{t.value}"></span>
                    <span class="text-sm font-semibold">{t.label}</span>
                    <span class="text-[11px] text-on-surface-variant/50">{t.desc}</span>
                  </button>
                {/each}
              </div>
            </div>

          <!-- API Keys -->
          {:else if activeSection === 'api'}
            <div class="settings-card">
              <h2 class="settings-section-title">API Keys</h2>
              <p class="text-xs text-on-surface-variant/50 mb-5">Keys are stored encrypted. Leave blank to keep existing.</p>

              <div class="space-y-5">
                <!-- GitHub Token -->
                <div>
                  <label class="field-label">
                    GitHub Personal Access Token
                    {#if githubTokenSet}<span class="key-set-badge">● Set</span>{/if}
                  </label>
                  <div class="relative">
                    <input
                      bind:value={githubToken}
                      type={showGithub ? 'text' : 'password'}
                      placeholder={githubTokenSet ? '••••••••••••••••' : 'ghp_…'}
                      class="field-input pr-10"
                    />
                    <button type="button" class="pw-eye" on:click={() => showGithub = !showGithub}>
                      {#if showGithub}<EyeOff class="w-4 h-4" />{:else}<Eye class="w-4 h-4" />{/if}
                    </button>
                  </div>
                  <p class="text-[11px] text-on-surface-variant/40 mt-1">Needs <code>repo</code> scope for PR Agent</p>
                </div>

                <!-- NVD API Key -->
                <div>
                  <label class="field-label">
                    NVD API Key
                    {#if nvdApiKeySet}<span class="key-set-badge">● Set</span>{/if}
                  </label>
                  <div class="relative">
                    <input
                      bind:value={nvdApiKey}
                      type={showNvd ? 'text' : 'password'}
                      placeholder={nvdApiKeySet ? '••••••••••••••••' : 'Optional — raises rate limit'}
                      class="field-input pr-10"
                    />
                    <button type="button" class="pw-eye" on:click={() => showNvd = !showNvd}>
                      {#if showNvd}<EyeOff class="w-4 h-4" />{:else}<Eye class="w-4 h-4" />{/if}
                    </button>
                  </div>
                </div>

                <!-- OpenRouter Key -->
                <div>
                  <label class="field-label">
                    OpenRouter API Key
                    {#if openrouterKeySet}<span class="key-set-badge">● Set</span>{/if}
                  </label>
                  <div class="relative">
                    <input
                      bind:value={openrouterKey}
                      type={showOpenrouter ? 'text' : 'password'}
                      placeholder={openrouterKeySet ? '••••••••••••••••' : 'sk-or-v1-…'}
                      class="field-input pr-10"
                    />
                    <button type="button" class="pw-eye" on:click={() => showOpenrouter = !showOpenrouter}>
                      {#if showOpenrouter}<EyeOff class="w-4 h-4" />{:else}<Eye class="w-4 h-4" />{/if}
                    </button>
                  </div>
                </div>
              </div>
            </div>

          <!-- Security -->
          {:else if activeSection === 'security'}
            <div class="settings-card">
              <h2 class="settings-section-title">Security</h2>
              <div class="space-y-4 mt-4">
                <div class="placeholder-feature">
                  <Shield class="w-5 h-5 text-neon-purple" />
                  <div>
                    <p class="text-sm font-semibold text-white">Two-Factor Authentication</p>
                    <p class="text-xs text-on-surface-variant/50">Coming soon — TOTP-based 2FA</p>
                  </div>
                  <span class="coming-soon-badge">Soon</span>
                </div>
                <div class="placeholder-feature">
                  <Key class="w-5 h-5 text-neon-cyan" />
                  <div>
                    <p class="text-sm font-semibold text-white">Active Sessions</p>
                    <p class="text-xs text-on-surface-variant/50">View and revoke active sessions</p>
                  </div>
                  <span class="coming-soon-badge">Soon</span>
                </div>
              </div>
            </div>
          {/if}

          <!-- Save button (shared) -->
          {#if activeSection !== 'account' && activeSection !== 'security'}
            <div class="flex items-center gap-3">
              <button class="save-btn" disabled={saving} on:click={saveSettings}>
                {#if saving}<Loader class="w-4 h-4 animate-spin" /> Saving…
                {:else if saved}<CheckCircle class="w-4 h-4" /> Saved!
                {:else}<Save class="w-4 h-4" /> Save Settings{/if}
              </button>
            </div>
          {/if}

        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .settings-nav {
    display: flex; flex-direction: row; flex-wrap: wrap; gap: 0.25rem;
    padding: 0.5rem;
    border-radius: 0.875rem;
    border: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.02);
  }
  @media (min-width: 1024px) {
    .settings-nav { flex-direction: column; }
  }

  .nav-item {
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.5rem 0.75rem; border-radius: 0.5rem;
    font-size: 0.8125rem; font-weight: 500;
    color: rgba(184,191,214,0.7);
    background: none; border: none; cursor: pointer;
    transition: all 0.15s; text-align: left; white-space: nowrap;
  }
  .nav-item:hover { background: rgba(255,255,255,0.05); color: white; }
  .nav-item-active { background: rgba(0,217,255,0.1); color: #00d9ff; }

  .settings-card {
    padding: 1.5rem; border-radius: 1rem;
    border: 1px solid rgba(255,255,255,0.07);
    background: rgba(8,11,24,0.8); backdrop-filter: blur(20px);
  }

  .settings-section-title {
    font-size: 0.9375rem; font-weight: 600; color: white; margin-bottom: 0.25rem;
  }

  .field-label {
    display: flex; align-items: center; gap: 0.5rem;
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: rgba(184,191,214,0.7); margin-bottom: 0.375rem;
  }

  .field-input {
    width: 100%; padding: 0.625rem 0.875rem; border-radius: 0.625rem;
    border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.04);
    color: #f0f4ff; font-size: 0.875rem; outline: none; font-family: inherit;
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  .field-input::placeholder { color: rgba(107,118,161,0.5); }
  .field-input:focus { border-color: rgba(0,217,255,0.4); box-shadow: 0 0 0 3px rgba(0,217,255,0.07); }

  .pw-eye {
    position: absolute; right: 0.875rem; top: 50%; transform: translateY(-50%);
    color: rgba(184,191,214,0.4); background: none; border: none; cursor: pointer;
    transition: color 0.2s; display: flex; align-items: center;
  }
  .pw-eye:hover { color: rgba(184,191,214,0.8); }

  .save-btn {
    display: inline-flex; align-items: center; gap: 0.5rem;
    padding: 0.625rem 1.25rem; border-radius: 0.625rem;
    font-size: 0.8125rem; font-weight: 600; color: #060914;
    background: linear-gradient(135deg, #00d9ff, #3a86ff);
    border: none; cursor: pointer; transition: opacity 0.2s, transform 0.15s;
  }
  .save-btn:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
  .save-btn:disabled { opacity: 0.5; cursor: not-allowed; }

  /* Toggle switch */
  .toggle-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.75rem 0; border-bottom: 1px solid rgba(255,255,255,0.04);
  }
  .toggle-row:last-child { border-bottom: none; }

  .toggle {
    position: relative; width: 2.5rem; height: 1.375rem;
    border-radius: 9999px; border: 1px solid rgba(255,255,255,0.1);
    background: rgba(255,255,255,0.06); cursor: pointer;
    transition: background 0.2s, border-color 0.2s; flex-shrink: 0;
  }
  .toggle-on { background: rgba(0,217,255,0.2); border-color: rgba(0,217,255,0.4); }

  .toggle-thumb {
    position: absolute; top: 2px; left: 2px;
    width: 1rem; height: 1rem; border-radius: 50%;
    background: rgba(184,191,214,0.5);
    transition: transform 0.2s, background 0.2s;
  }
  .toggle-on .toggle-thumb { transform: translateX(1.125rem); background: #00d9ff; }

  /* Theme options */
  .theme-option {
    display: flex; flex-direction: column; align-items: center; gap: 0.375rem;
    padding: 1rem 0.75rem; border-radius: 0.75rem;
    border: 1px solid rgba(255,255,255,0.07);
    background: rgba(255,255,255,0.02); cursor: pointer;
    transition: all 0.2s; color: white;
  }
  .theme-option:hover { border-color: rgba(255,255,255,0.15); }
  .theme-option-active { border-color: rgba(0,217,255,0.4); background: rgba(0,217,255,0.08); }

  /* Mini preview swatch */
  .theme-preview {
    width: 2.5rem; height: 1.5rem; border-radius: 0.375rem;
    border: 1px solid rgba(255,255,255,0.1);
    flex-shrink: 0;
  }
  .theme-preview-dark   { background: linear-gradient(135deg, #060914 50%, #0d1120 100%); }
  .theme-preview-light  { background: linear-gradient(135deg, #f0f4ff 50%, #e0e8ff 100%); }
  .theme-preview-system {
    background: linear-gradient(135deg, #060914 0%, #060914 50%, #f0f4ff 50%, #f0f4ff 100%);
  }

  .key-set-badge {
    font-size: 0.65rem; font-weight: 600; color: #34d399;
    background: rgba(52,211,153,0.1); padding: 0.1rem 0.4rem;
    border-radius: 9999px; border: 1px solid rgba(52,211,153,0.2);
    text-transform: none; letter-spacing: 0;
  }

  .placeholder-feature {
    display: flex; align-items: center; gap: 0.875rem;
    padding: 1rem; border-radius: 0.75rem;
    border: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.02);
  }

  .coming-soon-badge {
    margin-left: auto; font-size: 0.65rem; font-weight: 600;
    color: #9d4edd; background: rgba(157,78,221,0.1);
    padding: 0.2rem 0.5rem; border-radius: 9999px;
    border: 1px solid rgba(157,78,221,0.2);
  }
</style>
