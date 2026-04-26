<script lang="ts">
  import { onMount } from 'svelte';
  import { adminGet } from '$lib/adminApi';
  import { ScrollText, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-svelte';

  let logs: any[] = [];
  let total = 0;
  let loading = true;
  let error = '';
  let page = 1;
  const limit = 50;

  async function load() {
    loading = true; error = '';
    try {
      const res: any = await adminGet(`/audit-logs?page=${page}&limit=${limit}`);
      logs = res.logs; total = res.total;
    } catch (e: any) { error = e.message; }
    finally { loading = false; }
  }

  onMount(load);

  const ACTION_COLORS: Record<string, string> = {
    'user.update': '#fbbf24', 'user.delete': '#f87171',
    'repository.delete': '#fb923c', 'system.settings.update': '#a78bfa',
  };

  $: totalPages = Math.ceil(total / limit);
</script>

<svelte:head><title>Audit Logs — Admin</title></svelte:head>

<div class="space-y-5">
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-xl font-headline font-bold text-white">Audit Logs</h1>
      <p class="text-xs text-on-surface-variant/50 mt-0.5">{total} total entries</p>
    </div>
    <button class="admin-btn-ghost" on:click={load}><RefreshCw class="w-3.5 h-3.5" /> Refresh</button>
  </div>

  {#if error}<div class="admin-error">{error}</div>{/if}

  <div class="admin-table-wrap">
    <table class="admin-table">
      <thead><tr>
        <th>Actor</th><th>Action</th><th>Target</th><th>IP</th><th>Timestamp</th>
      </tr></thead>
      <tbody>
        {#if loading}
          {#each Array(15) as _}<tr><td colspan="5"><div class="skeleton-row"></div></td></tr>{/each}
        {:else}
          {#each logs as l}
            {@const color = ACTION_COLORS[l.action] ?? '#94a3b8'}
            <tr class="table-row">
              <td class="text-xs text-on-surface-variant/70">{l.actor_email ?? '—'}</td>
              <td>
                <span class="action-badge" style="color:{color}; background:{color}18; border-color:{color}33">{l.action}</span>
              </td>
              <td class="text-xs text-on-surface-variant/60">
                {#if l.target_type}{l.target_type}{#if l.target_id} · <span class="font-mono text-[10px]">{l.target_id.slice(0,8)}…</span>{/if}{:else}—{/if}
              </td>
              <td class="text-xs font-mono text-on-surface-variant/40">{l.ip_address ?? '—'}</td>
              <td class="text-xs text-on-surface-variant/50">{new Date(l.created_at).toLocaleString()}</td>
            </tr>
          {:else}
            <tr><td colspan="5" class="text-center text-xs text-on-surface-variant/40 py-8">No audit logs yet</td></tr>
          {/each}
        {/if}
      </tbody>
    </table>
  </div>

  {#if totalPages > 1}
    <div class="flex items-center justify-between text-xs text-on-surface-variant/50">
      <span>Page {page} of {totalPages}</span>
      <div class="flex gap-2">
        <button class="admin-btn-ghost" disabled={page<=1} on:click={() => { page--; load(); }}><ChevronLeft class="w-3.5 h-3.5" /></button>
        <button class="admin-btn-ghost" disabled={page>=totalPages} on:click={() => { page++; load(); }}><ChevronRight class="w-3.5 h-3.5" /></button>
      </div>
    </div>
  {/if}
</div>

<style>
  .admin-table-wrap { border-radius: 0.875rem; border: 1px solid rgba(255,255,255,0.06); overflow: hidden; overflow-x: auto; }
  .admin-table { width: 100%; border-collapse: collapse; min-width: 600px; }
  .admin-table thead tr { background: rgba(255,255,255,0.02); }
  .admin-table th { padding: 0.625rem 0.875rem; text-align: left; font-size: 0.65rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(184,191,214,0.4); border-bottom: 1px solid rgba(255,255,255,0.05); white-space: nowrap; }
  .table-row { border-bottom: 1px solid rgba(255,255,255,0.04); transition: background 0.15s; }
  .table-row:last-child { border-bottom: none; }
  .table-row:hover { background: rgba(255,255,255,0.02); }
  .admin-table td { padding: 0.625rem 0.875rem; }
  .action-badge { display: inline-flex; padding: 0.15rem 0.5rem; border-radius: 0.25rem; font-size: 0.65rem; font-weight: 600; border: 1px solid; font-family: monospace; }
  .skeleton-row { height: 2.5rem; border-radius: 0.375rem; background: rgba(255,255,255,0.04); animation: shimmer 1.5s infinite; background-size: 200% 100%; }
  .admin-btn-ghost { display: inline-flex; align-items: center; gap: 0.375rem; padding: 0.375rem 0.75rem; border-radius: 0.5rem; font-size: 0.75rem; font-weight: 500; color: rgba(184,191,214,0.6); background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07); cursor: pointer; transition: all 0.15s; }
  .admin-btn-ghost:hover:not(:disabled) { background: rgba(255,255,255,0.08); color: white; }
  .admin-btn-ghost:disabled { opacity: 0.3; cursor: not-allowed; }
  .admin-error { padding: 0.75rem 1rem; border-radius: 0.75rem; background: rgba(248,113,113,0.08); border: 1px solid rgba(248,113,113,0.2); color: #f87171; font-size: 0.875rem; }
  @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
</style>
