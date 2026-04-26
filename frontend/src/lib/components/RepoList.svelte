<script lang="ts">
  import { createEventDispatcher, onDestroy } from 'svelte';
  import {
    GitBranch, Plus, Play, ExternalLink, AlertTriangle,
    CheckCircle, Clock, X, Loader, RefreshCw, ShieldAlert
  } from 'lucide-svelte';
  import { PUBLIC_API_URL } from '$env/static/public';
  import CreatePRButton from './CreatePRButton.svelte';

  export let repositories: any[] = [];
  export let userId: string | null;
  export let addRepoTrigger = false;

  const dispatch = createEventDispatcher();
  const apiUrl = PUBLIC_API_URL || 'http://localhost:8000';

  // ── Add form state ────────────────────────────────────────────────────────
  let showAddForm = false;
  let repoUrl = '';
  let repoName = '';
  let adding = false;
  let addError = '';

  // ── Per-repo scan state ───────────────────────────────────────────────────
  // scanState[repoId] = { status, scanId, error, pollTimer }
  let scanState: Record<string, {
    status: 'idle' | 'pending' | 'running' | 'completed' | 'failed';
    scanId: string | null;
    error: string;
    vulns: number;
  }> = {};

  let pollTimers: Record<string, ReturnType<typeof setInterval>> = {};

  // ── Toast ─────────────────────────────────────────────────────────────────
  let toasts: { id: number; type: 'success' | 'error' | 'info'; msg: string }[] = [];
  let toastSeq = 0;

  function toast(type: 'success' | 'error' | 'info', msg: string) {
    const id = ++toastSeq;
    toasts = [...toasts, { id, type, msg }];
    setTimeout(() => { toasts = toasts.filter(t => t.id !== id); }, 5000);
  }

  // ── Trigger from parent ───────────────────────────────────────────────────
  $: if (addRepoTrigger) { showAddForm = true; addRepoTrigger = false; }

  // ── Add repository ────────────────────────────────────────────────────────
  async function handleAdd(e: Event) {
    e.preventDefault();
    adding = true; addError = '';
    try {
      const res = await fetch(`${apiUrl}/api/repositories/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: repoUrl, repo_name: repoName, user_id: userId }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to add repository');
      repoUrl = ''; repoName = ''; showAddForm = false;
      toast('success', 'Repository added');
      dispatch('refresh');
    } catch (err: any) {
      addError = err.message;
    } finally { adding = false; }
  }

  // ── Start scan ────────────────────────────────────────────────────────────
  async function handleScan(repo: any) {
    const rid = repo.id;
    scanState[rid] = { status: 'pending', scanId: null, error: '', vulns: 0 };
    scanState = { ...scanState };

    console.log(`[scan] Triggering scan for repo ${rid} — ${repo.repo_url}`);

    try {
      const res = await fetch(`${apiUrl}/api/scans/trigger`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repo_id:  rid,
          repo_url: repo.repo_url,
        }),
      });

      const data = await res.json();
      console.log(`[scan] Response ${res.status}:`, data);

      if (!res.ok) {
        // Surface the real backend error
        throw new Error(data.detail || `Server error ${res.status}`);
      }

      const scanId: string = data.scan_id;
      scanState[rid] = { status: 'running', scanId, error: '', vulns: 0 };
      scanState = { ...scanState };
      toast('info', `Scan started — polling for results…`);

      // Start polling
      startPolling(rid, scanId);

    } catch (err: any) {
      console.error(`[scan] Failed:`, err);
      scanState[rid] = { status: 'failed', scanId: null, error: err.message, vulns: 0 };
      scanState = { ...scanState };
      toast('error', err.message);
    }
  }

  // ── Poll scan status ──────────────────────────────────────────────────────
  function startPolling(repoId: string, scanId: string) {
    // Clear any existing timer for this repo
    if (pollTimers[repoId]) clearInterval(pollTimers[repoId]);

    pollTimers[repoId] = setInterval(async () => {
      try {
        const res = await fetch(`${apiUrl}/api/scans/${scanId}`);
        if (!res.ok) return;
        const data = await res.json();
        const scan = data.scan;
        const status = scan?.status;

        console.log(`[poll] scan ${scanId} → ${status}`);

        if (status === 'completed') {
          clearInterval(pollTimers[repoId]);
          const vulns = scan.total_vulnerabilities ?? 0;
          scanState[repoId] = { status: 'completed', scanId, error: '', vulns };
          scanState = { ...scanState };
          toast('success', `Scan complete — ${vulns} issue${vulns !== 1 ? 's' : ''} found`);
          dispatch('refresh');
        } else if (status === 'failed') {
          clearInterval(pollTimers[repoId]);
          scanState[repoId] = { status: 'failed', scanId, error: 'Scan failed on server', vulns: 0 };
          scanState = { ...scanState };
          toast('error', 'Scan failed — check backend logs');
        } else {
          // still running/pending — update state to keep spinner
          scanState[repoId] = { ...scanState[repoId], status: status ?? 'running' };
          scanState = { ...scanState };
        }
      } catch (e) {
        console.warn('[poll] fetch error:', e);
      }
    }, 3000);
  }

  // Cleanup timers on component destroy
  onDestroy(() => {
    Object.values(pollTimers).forEach(t => clearInterval(t));
  });

  // ── Helpers ───────────────────────────────────────────────────────────────
  function formatDate(iso: string) {
    return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }

  function repoScanState(repoId: string) {
    return scanState[repoId] ?? { status: 'idle', scanId: null, error: '', vulns: 0 };
  }

  const STATUS_META = {
    idle:      { label: 'Ready',    color: '#34d399', bg: 'rgba(52,211,153,0.1)',  border: 'rgba(52,211,153,0.2)'  },
    pending:   { label: 'Queued',   color: '#00d9ff', bg: 'rgba(0,217,255,0.1)',   border: 'rgba(0,217,255,0.2)'   },
    running:   { label: 'Scanning', color: '#3a86ff', bg: 'rgba(58,134,255,0.1)',  border: 'rgba(58,134,255,0.2)'  },
    completed: { label: 'Done',     color: '#34d399', bg: 'rgba(52,211,153,0.1)',  border: 'rgba(52,211,153,0.2)'  },
    failed:    { label: 'Failed',   color: '#f87171', bg: 'rgba(248,113,113,0.1)', border: 'rgba(248,113,113,0.2)' },
  };
</script>

<!-- ── Toast container ──────────────────────────────────────────────────── -->
<div class="toast-container" aria-live="polite">
  {#each toasts as t (t.id)}
    <div class="toast toast-{t.type}">
      {#if t.type === 'error'}
        <AlertTriangle class="w-3.5 h-3.5 flex-shrink-0" />
      {:else if t.type === 'success'}
        <CheckCircle class="w-3.5 h-3.5 flex-shrink-0" />
      {:else}
        <Loader class="w-3.5 h-3.5 flex-shrink-0 animate-spin" />
      {/if}
      <span>{t.msg}</span>
    </div>
  {/each}
</div>

<div class="space-y-4">

  <!-- Section header -->
  <div class="flex items-center justify-between">
    <div>
      <h2 class="text-base font-semibold text-white">Repositories</h2>
      <p class="text-xs text-on-surface-variant/50 mt-0.5">{repositories.length} connected</p>
    </div>
    <button class="add-btn" on:click={() => showAddForm = !showAddForm}>
      <Plus class="w-3.5 h-3.5" /> Add Repository
    </button>
  </div>

  <!-- Add form -->
  {#if showAddForm}
    <div class="add-form-card">
      <div class="flex items-center justify-between mb-5">
        <h3 class="text-sm font-semibold text-white">Connect a Repository</h3>
        <button class="text-on-surface-variant/40 hover:text-white transition-colors" on:click={() => showAddForm = false}>
          <X class="w-4 h-4" />
        </button>
      </div>
      <form on:submit={handleAdd} class="space-y-4">
        <div>
          <label class="form-label" for="repoUrl">GitHub URL</label>
          <input bind:value={repoUrl} id="repoUrl" type="url"
            placeholder="https://github.com/username/repository" required class="form-input" />
        </div>
        <div>
          <label class="form-label" for="repoName">Display Name</label>
          <input bind:value={repoName} id="repoName" type="text"
            placeholder="my-project" required class="form-input" />
        </div>
        {#if addError}
          <p class="text-xs text-red-400 flex items-center gap-1.5">
            <AlertTriangle class="w-3.5 h-3.5" /> {addError}
          </p>
        {/if}
        <div class="flex gap-2.5 pt-1">
          <button type="submit" disabled={adding} class="submit-btn">
            {#if adding}<Loader class="w-3.5 h-3.5 animate-spin" /> Adding...
            {:else}<Plus class="w-3.5 h-3.5" /> Add Repository{/if}
          </button>
          <button type="button" on:click={() => showAddForm = false} class="cancel-btn">Cancel</button>
        </div>
      </form>
    </div>
  {/if}

  <!-- Empty state -->
  {#if repositories.length === 0}
    <div class="empty-state">
      <div class="empty-icon"><GitBranch class="w-7 h-7 text-neon-cyan/50" /></div>
      <h3 class="text-base font-semibold text-white mt-4 mb-1">No repositories yet</h3>
      <p class="text-sm text-on-surface-variant/50 max-w-xs mx-auto mb-5">
        Connect your first GitHub repository to start scanning for vulnerabilities.
      </p>
      <button class="add-btn" on:click={() => showAddForm = true}>
        <Plus class="w-3.5 h-3.5" /> Add your first repository
      </button>
    </div>

  {:else}
    <div class="repo-table-wrap">
      <div class="repo-table-head">
        <span class="col-name">Repository</span>
        <span class="col-status hidden sm:block">Status</span>
        <span class="col-date hidden md:block">Added</span>
        <span class="col-vulns hidden lg:block">Vulns</span>
        <span class="col-action"></span>
      </div>

      {#each repositories as repo, i}
        {@const rs = repoScanState(repo.id)}
        {@const meta = STATUS_META[rs.status]}
        <div class="repo-row" style="animation-delay:{i*50}ms">

          <!-- Name + URL -->
          <div class="col-name flex items-center gap-3 min-w-0">
            <div class="repo-icon">
              <GitBranch class="w-3.5 h-3.5 text-neon-cyan" />
            </div>
            <div class="min-w-0">
              <p class="text-sm font-medium text-white truncate">{repo.repo_name}</p>
              <a href={repo.repo_url} target="_blank" rel="noopener noreferrer"
                class="text-[11px] text-on-surface-variant/40 hover:text-neon-cyan transition-colors flex items-center gap-1 truncate">
                <span class="truncate">{repo.repo_url.replace('https://github.com/', '')}</span>
                <ExternalLink class="w-2.5 h-2.5 flex-shrink-0" />
              </a>
            </div>
          </div>

          <!-- Status badge — live -->
          <div class="col-status hidden sm:flex items-center">
            <span class="status-badge"
              style="background:{meta.bg}; color:{meta.color}; border-color:{meta.border}">
              {#if rs.status === 'running' || rs.status === 'pending'}
                <Loader class="w-3 h-3 animate-spin" />
              {:else if rs.status === 'failed'}
                <AlertTriangle class="w-3 h-3" />
              {:else}
                <CheckCircle class="w-3 h-3" />
              {/if}
              {meta.label}
            </span>
          </div>

          <!-- Date -->
          <div class="col-date hidden md:flex items-center">
            <span class="text-xs text-on-surface-variant/50 flex items-center gap-1">
              <Clock class="w-3 h-3" /> {formatDate(repo.created_at)}
            </span>
          </div>

          <!-- Vulns count -->
          <div class="col-vulns hidden lg:flex items-center">
            {#if rs.vulns > 0}
              <span class="text-xs font-semibold text-red-400 flex items-center gap-1">
                <ShieldAlert class="w-3 h-3" /> {rs.vulns}
              </span>
            {:else}
              <span class="text-xs text-on-surface-variant/40">—</span>
            {/if}
          </div>

          <!-- Actions -->
          <div class="col-action flex items-center justify-end gap-2">

            <button
              class="scan-btn"
              disabled={rs.status === 'running' || rs.status === 'pending'}
              on:click={() => handleScan(repo)}
              title={rs.status === 'failed' ? `Retry — last error: ${rs.error}` : 'Start security scan'}
            >
              {#if rs.status === 'running' || rs.status === 'pending'}
                <Loader class="w-3.5 h-3.5 animate-spin" />
                <span class="hidden sm:inline">Scanning…</span>
              {:else if rs.status === 'failed'}
                <RefreshCw class="w-3.5 h-3.5" />
                <span class="hidden sm:inline">Retry</span>
              {:else}
                <Play class="w-3.5 h-3.5" />
                <span class="hidden sm:inline">Scan</span>
              {/if}
            </button>

            {#if rs.scanId || repo.last_scan_id}
              <CreatePRButton
                scanId={rs.scanId ?? repo.last_scan_id}
                repoUrl={repo.repo_url}
              />
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  /* Toast */
  .toast-container {
    position: fixed;
    bottom: 1.5rem;
    right: 1.5rem;
    z-index: 9999;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    pointer-events: none;
  }
  .toast {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.625rem 1rem;
    border-radius: 0.75rem;
    font-size: 0.8125rem;
    font-weight: 500;
    backdrop-filter: blur(16px);
    border: 1px solid;
    animation: slideIn 0.2s ease;
    max-width: 340px;
  }
  .toast-success { background: rgba(52,211,153,0.12); border-color: rgba(52,211,153,0.3); color: #34d399; }
  .toast-error   { background: rgba(248,113,113,0.12); border-color: rgba(248,113,113,0.3); color: #f87171; }
  .toast-info    { background: rgba(0,217,255,0.10);   border-color: rgba(0,217,255,0.25);  color: #00d9ff; }

  @keyframes slideIn {
    from { opacity: 0; transform: translateX(12px); }
    to   { opacity: 1; transform: translateX(0); }
  }

  /* Buttons */
  .add-btn {
    display: inline-flex; align-items: center; gap: 0.375rem;
    padding: 0.5rem 0.875rem; border-radius: 0.625rem;
    font-size: 0.8125rem; font-weight: 500;
    color: #00d9ff; background: rgba(0,217,255,0.07);
    border: 1px solid rgba(0,217,255,0.2); cursor: pointer; transition: all 0.2s; white-space: nowrap;
  }
  .add-btn:hover { background: rgba(0,217,255,0.12); border-color: rgba(0,217,255,0.35); }

  .add-form-card {
    padding: 1.25rem; border-radius: 1rem;
    border: 1px solid rgba(0,217,255,0.15); background: rgba(0,217,255,0.04);
    animation: fadeUp 0.2s ease;
  }
  .form-label {
    display: block; font-size: 0.7rem; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: rgba(184,191,214,0.7); margin-bottom: 0.375rem;
  }
  .form-input {
    width: 100%; padding: 0.625rem 0.875rem; border-radius: 0.625rem;
    border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.04);
    color: #f0f4ff; font-size: 0.875rem; outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  .form-input::placeholder { color: rgba(107,118,161,0.5); }
  .form-input:focus { border-color: rgba(0,217,255,0.4); box-shadow: 0 0 0 3px rgba(0,217,255,0.07); }

  .submit-btn {
    display: inline-flex; align-items: center; gap: 0.375rem;
    padding: 0.5rem 1rem; border-radius: 0.625rem;
    font-size: 0.8125rem; font-weight: 600; color: #060914;
    background: linear-gradient(135deg, #00d9ff, #3a86ff);
    border: none; cursor: pointer; transition: opacity 0.2s, transform 0.15s;
  }
  .submit-btn:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
  .submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }

  .cancel-btn {
    padding: 0.5rem 1rem; border-radius: 0.625rem;
    font-size: 0.8125rem; font-weight: 500; color: rgba(184,191,214,0.7);
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);
    cursor: pointer; transition: all 0.2s;
  }
  .cancel-btn:hover { background: rgba(255,255,255,0.07); color: white; }

  /* Empty state */
  .empty-state {
    padding: 3rem 1.5rem; border-radius: 1rem;
    border: 1px dashed rgba(255,255,255,0.08); background: rgba(255,255,255,0.01); text-align: center;
  }
  .empty-icon {
    width: 3.5rem; height: 3.5rem; border-radius: 1rem;
    border: 1px solid rgba(0,217,255,0.15); background: rgba(0,217,255,0.06);
    display: flex; align-items: center; justify-content: center; margin: 0 auto;
  }

  /* Table */
  .repo-table-wrap {
    border-radius: 1rem; border: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.02); overflow: hidden;
  }
  .repo-table-head {
    display: grid; grid-template-columns: 1fr auto auto auto auto;
    gap: 1rem; padding: 0.625rem 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.05); background: rgba(255,255,255,0.02);
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: rgba(184,191,214,0.4);
  }
  .repo-row {
    display: grid; grid-template-columns: 1fr auto auto auto auto;
    gap: 1rem; align-items: center; padding: 0.875rem 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    transition: background 0.15s; animation: fadeUp 0.3s ease both;
  }
  .repo-row:last-child { border-bottom: none; }
  .repo-row:hover { background: rgba(255,255,255,0.03); }

  .col-name   { min-width: 0; }
  .col-status { width: 90px; }
  .col-date   { width: 100px; }
  .col-vulns  { width: 60px; }
  .col-action { width: 200px; }

  .repo-icon {
    width: 2rem; height: 2rem; border-radius: 0.5rem;
    border: 1px solid rgba(0,217,255,0.15); background: rgba(0,217,255,0.07);
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  }

  .status-badge {
    display: inline-flex; align-items: center; gap: 0.3rem;
    padding: 0.25rem 0.625rem; border-radius: 9999px;
    font-size: 0.7rem; font-weight: 500; border: 1px solid;
  }

  .scan-btn {
    display: inline-flex; align-items: center; gap: 0.3rem;
    padding: 0.375rem 0.75rem; border-radius: 0.5rem;
    font-size: 0.75rem; font-weight: 500; color: #9d4edd;
    background: rgba(157,78,221,0.08); border: 1px solid rgba(157,78,221,0.2);
    cursor: pointer; transition: all 0.2s; white-space: nowrap;
  }
  .scan-btn:hover:not(:disabled) { background: rgba(157,78,221,0.15); border-color: rgba(157,78,221,0.35); }
  .scan-btn:disabled { opacity: 0.5; cursor: not-allowed; }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
  }
</style>
