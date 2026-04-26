<script lang="ts">
  import { onMount } from 'svelte';
  import { adminGet, adminPut } from '$lib/adminApi';
  import { Save, RefreshCw, Eye, EyeOff, ShieldAlert, Key, Cpu } from 'lucide-svelte';

  let settings: any = {};
  let loading = true;
  let saving = false;
  let error = '';
  let toast = '';

  // Form fields
  let githubToken = '';
  let openrouterKey = '';
  let nvdKey = '';
  let openrouterModel = '';

  // Show/hide toggles
  let showGithub = false;
  let showOpenrouter = false;
  let showNvd = false;

  async function load() {
    loading = true; error = '';
    try {
      settings = await adminGet('/system-settings');
      openrouterModel = settings.openrouter_model ?? '';
      // Keys are never returned as plaintext — only their "set" status
    } catch (e: any) { error = e.message; }
    finally { loading = false; }
  }

  onMount(load);

  async function save() {
    saving = true; error = '';
    try {
      const body: Record<string, string> = { openrouter_model: openrouterModel };
      if (githubToken)    body.github_token = githubToken;
      if (openrouterKey)  body.openrouter_api_key = openrouterKey;
      if (nvdKey)         body.nvd_api_key = nvdKey;
      await adminPut('/system-settings', body);
      toast = 'Settings saved successfully';
      // Clear sensitive inputs after save
      githubToken = ''; openrouterKey = ''; nvdKey = '';
      await load();
      setTimeout(() => toast = '', 3000);
    } catch (e: any) { error = e.message; }
    finally { saving = false; }
  }

  $: githubSet     = settings?.github_token_set     ?? settings?.has_github_token     ?? false;
  $: openrouterSet = settings?.openrouter_key_set    ?? settings?.has_openrouter_key   ?? false;
  $: nvdSet        = settings?.nvd_key_set           ?? settings?.has_nvd_key          ?? false;
</script>

<svelte:head><title>System Settings — Admin</title></svelte:head>

<div class="space-y-5">
  <div class="flex flex-wrap items-center justify-between gap-3">
    <div>
      <h1 class="text-xl font-bold text-white">System Settings</h1>
      <p class="text-xs text-muted mt-0.5">Global API keys and configuration</p>
    </div>
    <button class="admin-btn-ghost" on:click={load}><RefreshCw class="w-3.5 h-3.5" /> Refresh</button>
  </div>

  <div class="super-note">
    <ShieldAlert class="w-4 h-4 text-[#fbbf24] flex-shrink-0" />
    <span>Only <strong class="text-[#fbbf24]">super_admin</strong> can access this page. Changes affect the entire platform.</span>
  </div>

  {#if error}<div class="admin-error">{error}</div>{/if}
  {#if toast}<div class="admin-toast">{toast}</div>{/if}

  {#if loading}
    <div class="space-y-3">
      {#each Array(4) as _}<div class="skeleton-field"></div>{/each}
    </div>
  {:else}
    <div class="settings-form">

      <!-- GitHub Token -->
      <div class="field-group">
        <div class="field-label-row">
          <div class="field-icon" style="background:rgba(52,211,153,0.1); color:#34d399; border-color:rgba(52,211,153,0.2)">
            <Key class="w-3.5 h-3.5" />
          </div>
          <div>
            <label class="field-label">GitHub Token</label>
            <p class="field-desc">Used for repository access and PR creation.</p>
          </div>
          <div class="ml-auto">
            {#if githubSet}
              <span class="set-badge set">Set ✓</span>
            {:else}
              <span class="set-badge unset">Not set</span>
            {/if}
          </div>
        </div>
        <div class="input-wrap">
          {#if showGithub}
            <input bind:value={githubToken} type="text" placeholder="ghp_xxxxxxxxxxxx" class="settings-input" />
          {:else}
            <input bind:value={githubToken} type="password" placeholder={githubSet ? '••••••••••••••••' : 'Enter GitHub token'} class="settings-input" />
          {/if}
          <button class="eye-btn" on:click={() => showGithub = !showGithub}>
            {#if showGithub}<EyeOff class="w-3.5 h-3.5" />{:else}<Eye class="w-3.5 h-3.5" />{/if}
          </button>
        </div>
      </div>

      <div class="divider"></div>

      <!-- OpenRouter API Key -->
      <div class="field-group">
        <div class="field-label-row">
          <div class="field-icon" style="background:rgba(157,78,221,0.1); color:#9d4edd; border-color:rgba(157,78,221,0.2)">
            <Cpu class="w-3.5 h-3.5" />
          </div>
          <div>
            <label class="field-label">OpenRouter API Key</label>
            <p class="field-desc">Powers AI-based vulnerability analysis and fix suggestions.</p>
          </div>
          <div class="ml-auto">
            {#if openrouterSet}
              <span class="set-badge set">Set ✓</span>
            {:else}
              <span class="set-badge unset">Not set</span>
            {/if}
          </div>
        </div>
        <div class="input-wrap">
          {#if showOpenrouter}
            <input bind:value={openrouterKey} type="text" placeholder="sk-or-xxxxxxxxxxxx" class="settings-input" />
          {:else}
            <input bind:value={openrouterKey} type="password" placeholder={openrouterSet ? '••••••••••••••••' : 'Enter OpenRouter key'} class="settings-input" />
          {/if}
          <button class="eye-btn" on:click={() => showOpenrouter = !showOpenrouter}>
            {#if showOpenrouter}<EyeOff class="w-3.5 h-3.5" />{:else}<Eye class="w-3.5 h-3.5" />{/if}
          </button>
        </div>
      </div>

      <div class="divider"></div>

      <!-- OpenRouter Model -->
      <div class="field-group">
        <div class="field-label-row">
          <div class="field-icon" style="background:rgba(0,217,255,0.1); color:#00d9ff; border-color:rgba(0,217,255,0.2)">
            <Cpu class="w-3.5 h-3.5" />
          </div>
          <div>
            <label class="field-label">OpenRouter Model</label>
            <p class="field-desc">Model identifier used for AI analysis (e.g. openai/gpt-4o).</p>
          </div>
        </div>
        <input bind:value={openrouterModel} type="text" placeholder="openai/gpt-4o" class="settings-input mt-2" />
      </div>

      <div class="divider"></div>

      <!-- NVD API Key -->
      <div class="field-group">
        <div class="field-label-row">
          <div class="field-icon" style="background:rgba(251,191,36,0.1); color:#fbbf24; border-color:rgba(251,191,36,0.2)">
            <ShieldAlert class="w-3.5 h-3.5" />
          </div>
          <div>
            <label class="field-label">NVD API Key</label>
            <p class="field-desc">National Vulnerability Database key for CVE enrichment.</p>
          </div>
          <div class="ml-auto">
            {#if nvdSet}
              <span class="set-badge set">Set ✓</span>
            {:else}
              <span class="set-badge unset">Not set</span>
            {/if}
          </div>
        </div>
        <div class="input-wrap">
          {#if showNvd}
            <input bind:value={nvdKey} type="text" placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" class="settings-input" />
          {:else}
            <input bind:value={nvdKey} type="password" placeholder={nvdSet ? '••••••••••••••••' : 'Enter NVD API key'} class="settings-input" />
          {/if}
          <button class="eye-btn" on:click={() => showNvd = !showNvd}>
            {#if showNvd}<EyeOff class="w-3.5 h-3.5" />{:else}<Eye class="w-3.5 h-3.5" />{/if}
          </button>
        </div>
      </div>

      <div class="save-row">
        <button class="save-btn" disabled={saving} on:click={save}>
          {#if saving}
            <div class="spin"></div> Saving…
          {:else}
            <Save class="w-3.5 h-3.5" /> Save Settings
          {/if}
        </button>
        <p class="text-xs text-muted">Only filled fields will be updated. Leave blank to keep existing values.</p>
      </div>
    </div>
  {/if}
</div>

<style>
  .text-muted { color: rgba(184,191,214,0.5); }

  .super-note {
    display: flex; align-items: center; gap: 0.625rem;
    padding: 0.75rem 1rem; border-radius: 0.75rem;
    background: rgba(251,191,36,0.05); border: 1px solid rgba(251,191,36,0.15);
    font-size: 0.8125rem; color: rgba(184,191,214,0.7);
  }

  .settings-form {
    padding: 1.25rem; border-radius: 0.875rem;
    border: 1px solid rgba(255,255,255,0.06); background: rgba(255,255,255,0.02);
    display: flex; flex-direction: column; gap: 1.25rem;
  }

  .field-group { display: flex; flex-direction: column; gap: 0.625rem; }

  .field-label-row { display: flex; align-items: center; gap: 0.75rem; }

  .field-icon {
    width: 2.25rem; height: 2.25rem; border-radius: 0.5rem;
    display: flex; align-items: center; justify-content: center;
    border: 1px solid; flex-shrink: 0;
  }

  .field-label { font-size: 0.8125rem; font-weight: 600; color: white; display: block; }
  .field-desc  { font-size: 0.7rem; color: rgba(184,191,214,0.5); margin-top: 0.125rem; }

  .set-badge {
    display: inline-flex; padding: 0.2rem 0.5rem; border-radius: 0.375rem;
    font-size: 0.65rem; font-weight: 700; border: 1px solid;
  }
  .set-badge.set   { color: #34d399; background: rgba(52,211,153,0.1);  border-color: rgba(52,211,153,0.25);  }
  .set-badge.unset { color: #94a3b8; background: rgba(148,163,184,0.08); border-color: rgba(148,163,184,0.2); }

  .input-wrap { position: relative; }
  .settings-input {
    width: 100%; padding: 0.5rem 2.5rem 0.5rem 0.75rem;
    border-radius: 0.625rem; border: 1px solid rgba(255,255,255,0.08);
    background: rgba(255,255,255,0.04); color: #f0f4ff;
    font-size: 0.8125rem; outline: none; transition: border-color 0.15s;
    box-sizing: border-box;
  }
  .settings-input:focus { border-color: rgba(0,217,255,0.3); }
  .settings-input::placeholder { color: rgba(107,118,161,0.5); }

  .eye-btn {
    position: absolute; right: 0.625rem; top: 50%; transform: translateY(-50%);
    color: rgba(184,191,214,0.4); background: none; border: none; cursor: pointer;
    display: flex; align-items: center; transition: color 0.15s;
  }
  .eye-btn:hover { color: rgba(184,191,214,0.8); }

  .divider { height: 1px; background: rgba(255,255,255,0.05); }

  .save-row { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; padding-top: 0.25rem; }

  .save-btn {
    display: inline-flex; align-items: center; gap: 0.5rem;
    padding: 0.5rem 1.25rem; border-radius: 0.625rem;
    font-size: 0.8125rem; font-weight: 600; color: #060914;
    background: linear-gradient(135deg, #00d9ff, #3a86ff);
    border: none; cursor: pointer; transition: opacity 0.2s;
  }
  .save-btn:disabled { opacity: 0.5; cursor: not-allowed; }

  .spin {
    width: 0.875rem; height: 0.875rem; border-radius: 50%;
    border: 2px solid rgba(6,9,20,0.4); border-top-color: #060914;
    animation: spin 0.7s linear infinite;
  }

  .skeleton-field {
    height: 5rem; border-radius: 0.75rem;
    background: linear-gradient(90deg, rgba(255,255,255,0.04) 25%, rgba(255,255,255,0.07) 50%, rgba(255,255,255,0.04) 75%);
    animation: shimmer 1.5s infinite; background-size: 200% 100%;
  }

  .admin-btn-ghost {
    display: inline-flex; align-items: center; gap: 0.375rem;
    padding: 0.375rem 0.75rem; border-radius: 0.5rem;
    font-size: 0.75rem; font-weight: 500; color: rgba(184,191,214,0.6);
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);
    cursor: pointer; transition: all 0.15s;
  }
  .admin-btn-ghost:hover { background: rgba(255,255,255,0.08); color: white; }

  .admin-error { padding: 0.75rem 1rem; border-radius: 0.75rem; background: rgba(248,113,113,0.08); border: 1px solid rgba(248,113,113,0.2); color: #f87171; font-size: 0.875rem; }
  .admin-toast { padding: 0.75rem 1rem; border-radius: 0.75rem; background: rgba(52,211,153,0.08); border: 1px solid rgba(52,211,153,0.2); color: #34d399; font-size: 0.875rem; }

  @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
  @keyframes spin    { to { transform: rotate(360deg); } }
</style>
