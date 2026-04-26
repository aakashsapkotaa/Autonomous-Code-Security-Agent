<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { GitPullRequest, Loader, CheckCircle, AlertTriangle, ExternalLink, RefreshCw, X } from 'lucide-svelte';
  import { PUBLIC_API_URL } from '$env/static/public';

  export let scanId: string;
  export let repoUrl: string;
  export let baseBranch: string = 'main';

  const apiUrl = PUBLIC_API_URL || 'http://localhost:8000';

  type State = 'idle' | 'loading' | 'success' | 'error';
  let state: State = 'idle';
  let prUrl = '';
  let prNumber = 0;
  let filesChanged: string[] = [];
  let errorMsg = '';
  let popoverOpen = false;
  let btnEl: HTMLButtonElement;

  // Reset error state when a new scan is available
  let prevScanId = scanId;
  $: if (scanId !== prevScanId) {
    prevScanId = scanId;
    if (state === 'error') { state = 'idle'; errorMsg = ''; }
  }

  async function createPR() {
    state = 'loading';
    errorMsg = '';
    popoverOpen = false;
    try {
      const res = await fetch(`${apiUrl}/api/github/create-pr`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scan_id: scanId, repo_url: repoUrl, base_branch: baseBranch }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to create PR');
      prUrl = data.pr_url;
      prNumber = data.pr_number;
      filesChanged = data.files_changed ?? [];
      state = 'success';
    } catch (err: any) {
      errorMsg = err.message;
      state = 'error';
      popoverOpen = true;
    }
  }

  function retry() { state = 'idle'; errorMsg = ''; popoverOpen = false; createPR(); }
  function dismiss() { state = 'idle'; errorMsg = ''; popoverOpen = false; }

  function handleOutside(e: MouseEvent) {
    if (popoverOpen && btnEl && !btnEl.closest('.pr-root')?.contains(e.target as Node)) {
      popoverOpen = false;
    }
  }

  onMount(() => window.addEventListener('click', handleOutside));
  onDestroy(() => window.removeEventListener('click', handleOutside));
</script>

<div class="pr-root">

  <!-- ── IDLE ── -->
  {#if state === 'idle'}
    <button class="pr-btn" on:click={createPR}>
      <GitPullRequest class="w-3.5 h-3.5" />
      <span>Create PR</span>
    </button>

  <!-- ── LOADING ── -->
  {:else if state === 'loading'}
    <button class="pr-btn pr-btn-loading" disabled>
      <Loader class="w-3.5 h-3.5 animate-spin" />
      <span>Creating…</span>
    </button>

  <!-- ── SUCCESS ── -->
  {:else if state === 'success'}
    <a href={prUrl} target="_blank" rel="noopener noreferrer" class="pr-btn pr-btn-success">
      <CheckCircle class="w-3.5 h-3.5" />
      <span>PR #{prNumber}</span>
      <ExternalLink class="w-3 h-3 opacity-60" />
    </a>

  <!-- ── ERROR — compact pill + popover ── -->
  {:else if state === 'error'}
    <div class="pr-error-wrap">
      <!-- Compact error pill button -->
      <button
        bind:this={btnEl}
        class="pr-btn pr-btn-error"
        on:click|stopPropagation={() => popoverOpen = !popoverOpen}
        title={errorMsg}
      >
        <AlertTriangle class="w-3.5 h-3.5 flex-shrink-0" />
        <span>PR Failed</span>
      </button>

      <!-- Popover -->
      {#if popoverOpen}
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <!-- svelte-ignore a11y-no-static-element-interactions -->
        <div class="pr-popover" on:click|stopPropagation>
          <!-- Header -->
          <div class="pop-header">
            <div class="flex items-center gap-1.5">
              <AlertTriangle class="w-3.5 h-3.5 text-red-400 flex-shrink-0" />
              <span class="pop-title">PR Creation Failed</span>
            </div>
            <button class="pop-close" on:click={dismiss}><X class="w-3 h-3" /></button>
          </div>

          <!-- Error message -->
          <p class="pop-msg">{errorMsg}</p>

          <!-- Actions -->
          <div class="pop-actions">
            <button class="pop-retry" on:click={retry}>
              <RefreshCw class="w-3 h-3" /> Retry
            </button>
            <button class="pop-dismiss" on:click={dismiss}>Dismiss</button>
          </div>
        </div>
      {/if}
    </div>
  {/if}

</div>

<style>
  .pr-root {
    position: relative;
    display: inline-flex;
    flex-shrink: 0;
  }

  /* ── Base button ── */
  .pr-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.375rem 0.625rem;
    border-radius: 0.5rem;
    font-size: 0.75rem;
    font-weight: 500;
    white-space: nowrap;
    cursor: pointer;
    transition: all 0.15s;
    border: 1px solid;
    text-decoration: none;
    /* prevent any overflow */
    max-width: 130px;
    overflow: hidden;
  }

  /* idle / default — purple */
  .pr-btn {
    color: #9d4edd;
    background: rgba(157,78,221,0.08);
    border-color: rgba(157,78,221,0.22);
  }
  .pr-btn:hover:not(:disabled) {
    background: rgba(157,78,221,0.15);
    border-color: rgba(157,78,221,0.4);
  }

  /* loading */
  .pr-btn-loading {
    opacity: 0.6;
    cursor: not-allowed;
  }

  /* success — green */
  .pr-btn-success {
    color: #34d399;
    background: rgba(52,211,153,0.08);
    border-color: rgba(52,211,153,0.22);
  }
  .pr-btn-success:hover {
    background: rgba(52,211,153,0.14);
    border-color: rgba(52,211,153,0.4);
  }

  /* error — red compact pill */
  .pr-btn-error {
    color: #f87171;
    background: rgba(248,113,113,0.08);
    border-color: rgba(248,113,113,0.22);
  }
  .pr-btn-error:hover {
    background: rgba(248,113,113,0.14);
    border-color: rgba(248,113,113,0.4);
  }

  /* ── Error wrap (relative anchor for popover) ── */
  .pr-error-wrap {
    position: relative;
    display: inline-flex;
  }

  /* ── Popover ── */
  .pr-popover {
    position: absolute;
    bottom: calc(100% + 8px);
    right: 0;
    z-index: 999;
    width: 260px;
    background: #0d1117;
    border: 1px solid rgba(248,113,113,0.25);
    border-radius: 0.75rem;
    box-shadow: 0 16px 40px rgba(0,0,0,0.7), 0 0 0 1px rgba(248,113,113,0.08);
    padding: 0.875rem;
    animation: popIn 0.15s ease;
  }

  .pop-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.5rem;
  }

  .pop-title {
    font-size: 0.8125rem;
    font-weight: 600;
    color: #f87171;
  }

  .pop-close {
    width: 1.25rem; height: 1.25rem;
    display: flex; align-items: center; justify-content: center;
    border-radius: 0.25rem;
    color: rgba(184,191,214,0.4);
    background: none; border: none; cursor: pointer;
    transition: color 0.15s, background 0.15s;
  }
  .pop-close:hover { color: white; background: rgba(255,255,255,0.07); }

  .pop-msg {
    font-size: 0.75rem;
    color: rgba(184,191,214,0.7);
    line-height: 1.5;
    margin-bottom: 0.75rem;
    word-break: break-word;
  }

  .pop-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .pop-retry {
    display: inline-flex; align-items: center; gap: 0.3rem;
    padding: 0.375rem 0.75rem; border-radius: 0.5rem;
    font-size: 0.75rem; font-weight: 600;
    color: #060914;
    background: linear-gradient(135deg, #f87171, #ef4444);
    border: none; cursor: pointer;
    transition: opacity 0.15s, transform 0.15s;
  }
  .pop-retry:hover { opacity: 0.9; transform: translateY(-1px); }

  .pop-dismiss {
    font-size: 0.75rem;
    color: rgba(184,191,214,0.5);
    background: none; border: none; cursor: pointer;
    transition: color 0.15s;
    padding: 0.375rem 0.5rem;
  }
  .pop-dismiss:hover { color: white; }

  @keyframes popIn {
    from { opacity: 0; transform: translateY(4px) scale(0.97); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
  }
</style>
