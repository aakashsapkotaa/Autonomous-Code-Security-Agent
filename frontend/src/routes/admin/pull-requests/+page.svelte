<script lang="ts">
  import { onMount } from 'svelte';
  import { adminGet } from '$lib/adminApi';
  import { RefreshCw, ChevronLeft, ChevronRight, GitPullRequest, ExternalLink } from 'lucide-svelte';

  let prs: any[] = [];
  let total = 0;
  let loading = true;
  let error = '';
  let page = 1;
  const limit = 20;

  async function load() {
    loading = true; error = '';
    try {
      const res: any = await adminGet(`/pull-requests?page=${page}&limit=${limit}`);
      prs = res.pull_requests ?? res.items ?? res ?? [];
      total = res.total ?? prs.length;
    } catch (e: any) { error = e.message; }
    finally { loading = false; }
  }

  onMount(load);

  $: totalPages = Math.ceil(total / limit);
</script>

<svelte:head><title>Pull Requests — Admin</title></svelte:head>

<div class="space-y-5">
  <div class="flex flex-wrap items-center justify-between gap-3">
    <div>
      <h1 class="text-xl font-bold text-white">Pull Requests</h1>
      <p class="text-xs text-muted mt-0.5">{total} total pull requests</p>
    </div>
    <button class="admin-btn-ghost" on:click={load}><RefreshCw class="w-3.5 h-3.5" /> Refresh</button>
  </div>

  {#if error}<div class="admin-error">{error}</div>{/if}

  <div class="admin-table-wrap">
    <table class="admin-table">
      <thead>
        <tr>
          <th>Repository</th>
          <th>PR URL</th>
          <th>Owner</th>
          <th>Created</th>
        </tr>
      </thead>
      <tbody>
        {#if loading}
          {#each Array(8) as _}
            <tr><td colspan="4"><div class="skeleton-row"></div></td></tr>
          {/each}
        {:else if prs.length === 0}
          <tr>
            <td colspan="4" class="empty-state">
              <GitPullRequest class="w-10 h-10 mx-auto mb-3 opacity-20" />
              <p class="font-medium">No PRs yet</p>
              <p class="text-xs mt-1 opacity-60">Pull requests created by the AI agent will appear here.</p>
            </td>
          </tr>
        {:else}
          {#each prs as pr}
            <tr class="table-row">
              <td>
                <div class="flex items-center gap-2">
                  <div class="pr-icon"><GitPullRequest class="w-3.5 h-3.5" /></div>
                  <span class="text-xs font-medium text-white">{pr.repo_name ?? pr.repository ?? '—'}</span>
                </div>
              </td>
              <td>
                {#if pr.pr_url ?? pr.url}
                  <a href={pr.pr_url ?? pr.url} target="_blank" rel="noopener" class="url-link">
                    {(pr.pr_url ?? pr.url).replace('https://github.com/', '')}
                    <ExternalLink class="w-3 h-3 inline ml-1 opacity-60" />
                  </a>
                {:else}
                  <span class="text-xs text-muted">—</span>
                {/if}
              </td>
              <td class="text-xs text-muted">{pr.owner_email ?? pr.owner ?? '—'}</td>
              <td class="text-xs text-muted">
                {pr.created_at ? new Date(pr.created_at).toLocaleDateString() : '—'}
              </td>
            </tr>
          {/each}
        {/if}
      </tbody>
    </table>
  </div>

  {#if totalPages > 1}
    <div class="flex items-center justify-between text-xs text-muted">
      <span>Page {page} of {totalPages}</span>
      <div class="flex gap-2">
        <button class="admin-btn-ghost" disabled={page <= 1} on:click={() => { page--; load(); }}>
          <ChevronLeft class="w-3.5 h-3.5" />
        </button>
        <button class="admin-btn-ghost" disabled={page >= totalPages} on:click={() => { page++; load(); }}>
          <ChevronRight class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  {/if}
</div>

<style>
  .text-muted { color: rgba(184,191,214,0.5); }

  .admin-table-wrap { border-radius: 0.875rem; border: 1px solid rgba(255,255,255,0.06); overflow: hidden; }
  .admin-table { width: 100%; border-collapse: collapse; }
  .admin-table thead tr { background: rgba(255,255,255,0.02); }
  .admin-table th {
    padding: 0.625rem 0.875rem; text-align: left;
    font-size: 0.65rem; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: rgba(184,191,214,0.4);
    border-bottom: 1px solid rgba(255,255,255,0.05);
  }
  .table-row { border-bottom: 1px solid rgba(255,255,255,0.04); transition: background 0.15s; }
  .table-row:last-child { border-bottom: none; }
  .table-row:hover { background: rgba(255,255,255,0.02); }
  .admin-table td { padding: 0.75rem 0.875rem; }

  .pr-icon {
    width: 1.75rem; height: 1.75rem; border-radius: 0.375rem;
    background: rgba(157,78,221,0.1); border: 1px solid rgba(157,78,221,0.2);
    display: flex; align-items: center; justify-content: center;
    color: #9d4edd; flex-shrink: 0;
  }

  .url-link {
    font-size: 0.75rem; color: #3a86ff; text-decoration: none; transition: color 0.15s;
  }
  .url-link:hover { color: #00d9ff; }

  .empty-state {
    text-align: center; padding: 4rem 1rem;
    color: rgba(184,191,214,0.5); font-size: 0.875rem;
  }

  .skeleton-row {
    height: 2.5rem; border-radius: 0.375rem;
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
  .admin-btn-ghost:hover:not(:disabled) { background: rgba(255,255,255,0.08); color: white; }
  .admin-btn-ghost:disabled { opacity: 0.3; cursor: not-allowed; }

  .admin-error { padding: 0.75rem 1rem; border-radius: 0.75rem; background: rgba(248,113,113,0.08); border: 1px solid rgba(248,113,113,0.2); color: #f87171; font-size: 0.875rem; }

  @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
</style>
