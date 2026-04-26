<script lang="ts">
  import { onMount } from 'svelte';
  import { adminGet, adminDelete } from '$lib/adminApi';
  import { Search, RefreshCw, ChevronLeft, ChevronRight, Trash2, ExternalLink, GitBranch } from 'lucide-svelte';

  let repos: any[] = [];
  let total = 0;
  let loading = true;
  let error = '';
  let search = '';
  let page = 1;
  const limit = 20;
  let toast = '';

  async function load() {
    loading = true; error = '';
    try {
      const params = new URLSearchParams({ page: String(page), limit: String(limit) });
      if (search) params.set('search', search);
      const res: any = await adminGet(`/repositories?${params}`);
      repos = res.repositories ?? res.items ?? res ?? [];
      total = res.total ?? repos.length;
    } catch (e: any) { error = e.message; }
    finally { loading = false; }
  }

  onMount(load);

  async function deleteRepo(id: string) {
    if (!confirm('Delete this repository permanently?')) return;
    try {
      await adminDelete(`/repositories/${id}`);
      toast = 'Repository deleted';
      await load();
      setTimeout(() => toast = '', 2500);
    } catch (e: any) { error = e.message; }
  }

  function truncate(url: string, max = 40) {
    if (!url) return '—';
    return url.length > max ? url.slice(0, max) + '…' : url;
  }

  $: totalPages = Math.ceil(total / limit);
</script>

<svelte:head><title>Repositories — Admin</title></svelte:head>

<div class="space-y-5">
  <div class="flex flex-wrap items-center justify-between gap-3">
    <div>
      <h1 class="text-xl font-bold text-white">Repositories</h1>
      <p class="text-xs text-muted mt-0.5">{total} total repositories</p>
    </div>
    <button class="admin-btn-ghost" on:click={load}><RefreshCw class="w-3.5 h-3.5" /> Refresh</button>
  </div>

  <div class="search-wrap">
    <Search class="w-3.5 h-3.5 text-muted" />
    <input bind:value={search} on:input={() => { page = 1; load(); }}
      placeholder="Search repositories…" class="search-input" />
  </div>

  {#if error}<div class="admin-error">{error}</div>{/if}
  {#if toast}<div class="admin-toast">{toast}</div>{/if}

  <div class="admin-table-wrap">
    <table class="admin-table">
      <thead>
        <tr>
          <th>Repository</th>
          <th>Owner</th>
          <th>URL</th>
          <th>Created</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {#if loading}
          {#each Array(8) as _}
            <tr><td colspan="5"><div class="skeleton-row"></div></td></tr>
          {/each}
        {:else if repos.length === 0}
          <tr>
            <td colspan="5" class="empty-state">
              <GitBranch class="w-8 h-8 mx-auto mb-2 opacity-20" />
              <p>No repositories found</p>
            </td>
          </tr>
        {:else}
          {#each repos as repo}
            <tr class="table-row">
              <td>
                <div class="flex items-center gap-2">
                  <div class="repo-icon"><GitBranch class="w-3.5 h-3.5" /></div>
                  <span class="text-xs font-medium text-white">{repo.repo_name ?? repo.name ?? '—'}</span>
                </div>
              </td>
              <td class="text-xs text-muted">{repo.owner_email ?? repo.owner ?? '—'}</td>
              <td>
                {#if repo.repo_url ?? repo.url}
                  <a href={repo.repo_url ?? repo.url} target="_blank" rel="noopener"
                    class="url-link">
                    {truncate(repo.repo_url ?? repo.url)}
                    <ExternalLink class="w-3 h-3 inline ml-1 opacity-60" />
                  </a>
                {:else}
                  <span class="text-xs text-muted">—</span>
                {/if}
              </td>
              <td class="text-xs text-muted">
                {repo.created_at ? new Date(repo.created_at).toLocaleDateString() : '—'}
              </td>
              <td>
                <button class="action-btn action-danger" title="Delete" on:click={() => deleteRepo(repo.id)}>
                  <Trash2 class="w-3.5 h-3.5" />
                </button>
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

  .search-wrap {
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.375rem 0.75rem; border-radius: 0.625rem;
    border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.04);
    max-width: 360px;
  }
  .search-input {
    background: none; border: none; outline: none;
    color: #f0f4ff; font-size: 0.8125rem; width: 100%;
  }
  .search-input::placeholder { color: rgba(107,118,161,0.5); }

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

  .repo-icon {
    width: 1.75rem; height: 1.75rem; border-radius: 0.375rem;
    background: rgba(0,217,255,0.08); border: 1px solid rgba(0,217,255,0.15);
    display: flex; align-items: center; justify-content: center;
    color: #00d9ff; flex-shrink: 0;
  }

  .url-link {
    font-size: 0.75rem; color: #3a86ff; text-decoration: none;
    transition: color 0.15s;
  }
  .url-link:hover { color: #00d9ff; }

  .action-btn {
    width: 1.75rem; height: 1.75rem; border-radius: 0.375rem;
    display: flex; align-items: center; justify-content: center;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);
    color: rgba(184,191,214,0.6); cursor: pointer; transition: all 0.15s;
  }
  .action-danger:hover { background: rgba(248,113,113,0.1); color: #f87171; border-color: rgba(248,113,113,0.2); }

  .empty-state { text-align: center; padding: 3rem 1rem; color: rgba(184,191,214,0.4); font-size: 0.8125rem; }

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
  .admin-toast { padding: 0.75rem 1rem; border-radius: 0.75rem; background: rgba(52,211,153,0.08); border: 1px solid rgba(52,211,153,0.2); color: #34d399; font-size: 0.875rem; }

  @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
</style>
