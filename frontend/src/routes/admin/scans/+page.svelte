<script lang="ts">
  import { onMount } from 'svelte';
  import { adminGet } from '$lib/adminApi';
  import Dropdown from '$lib/components/admin/Dropdown.svelte';
  import { ScanLine, RefreshCw, ChevronLeft, ChevronRight, CheckCircle, XCircle, Clock, Activity } from 'lucide-svelte';

  let scans: any[] = [];
  let total = 0;
  let loading = true;
  let error = '';
  let statusFilter = '';
  let page = 1;
  const limit = 25;

  const STATUS_OPTIONS = [
    { value: '',          label: 'All statuses' },
    { value: 'running',   label: 'Running'      },
    { value: 'pending',   label: 'Pending'      },
    { value: 'completed', label: 'Completed'    },
    { value: 'failed',    label: 'Failed'       },
  ];

  async function load() {
    loading = true; error = '';
    try {
      const params = new URLSearchParams({ page: String(page), limit: String(limit) });
      if (statusFilter) params.set('status', statusFilter);
      const res: any = await adminGet(`/scans?${params}`);
      scans = res.scans; total = res.total;
    } catch (e: any) { error = e.message; }
    finally { loading = false; }
  }

  onMount(load);

  const STATUS_META: Record<string, { color: string; icon: any }> = {
    completed: { color: '#34d399', icon: CheckCircle },
    running:   { color: '#00d9ff', icon: Activity    },
    failed:    { color: '#f87171', icon: XCircle     },
    pending:   { color: '#fbbf24', icon: Clock       },
  };

  $: totalPages = Math.ceil(total / limit);
</script>

<svelte:head><title>Scans — Admin</title></svelte:head>

<div class="space-y-5">
  <div class="flex flex-wrap items-center justify-between gap-3">
    <div>
      <h1 class="text-xl font-headline font-bold text-white">Scan Monitor</h1>
      <p class="text-xs text-on-surface-variant/50 mt-0.5">{total} total scans</p>
    </div>
    <div class="flex gap-2 items-center">
      <Dropdown
        bind:value={statusFilter}
        options={STATUS_OPTIONS}
        onChange={() => { page = 1; load(); }}
      />
      <button class="admin-btn-ghost" on:click={load}><RefreshCw class="w-3.5 h-3.5" /></button>
    </div>
  </div>

  {#if error}<div class="admin-error">{error}</div>{/if}

  <div class="admin-table-wrap">
    <table class="admin-table">
      <thead><tr>
        <th>Repository</th><th>Owner</th><th>Status</th>
        <th>Vulns</th><th>Critical</th><th>High</th><th>Started</th>
      </tr></thead>
      <tbody>
        {#if loading}
          {#each Array(10) as _}<tr><td colspan="7"><div class="skeleton-row"></div></td></tr>{/each}
        {:else}
          {#each scans as s}
            {@const meta = STATUS_META[s.status] ?? STATUS_META.pending}
            <tr class="table-row">
              <td>
                <p class="text-xs font-medium text-white">{s.repositories?.repo_name ?? '—'}</p>
                <p class="text-[10px] text-on-surface-variant/40 font-mono truncate max-w-[180px]">{s.repositories?.repo_url ?? ''}</p>
              </td>
              <td class="text-xs text-on-surface-variant/60">{s.repositories?.users?.email ?? '—'}</td>
              <td>
                <div class="flex items-center gap-1.5">
                  <svelte:component this={meta.icon} class="w-3.5 h-3.5" style="color:{meta.color}" />
                  <span class="text-xs capitalize" style="color:{meta.color}">{s.status}</span>
                </div>
              </td>
              <td class="text-xs text-on-surface-variant/70">{s.total_vulnerabilities ?? 0}</td>
              <td class="text-xs text-red-400">{s.critical_count ?? 0}</td>
              <td class="text-xs text-orange-400">{s.high_count ?? 0}</td>
              <td class="text-xs text-on-surface-variant/50">{s.scan_started_at ? new Date(s.scan_started_at).toLocaleString() : '—'}</td>
            </tr>
          {:else}
            <tr><td colspan="7" class="text-center text-xs text-on-surface-variant/40 py-8">No scans found</td></tr>
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
  .admin-table-wrap { border-radius: 0.875rem; border: 1px solid rgba(255,255,255,0.06); overflow: hidden; }
  .admin-table { width: 100%; border-collapse: collapse; }
  .admin-table thead tr { background: rgba(255,255,255,0.02); }
  .admin-table th { padding: 0.625rem 0.875rem; text-align: left; font-size: 0.65rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(184,191,214,0.4); border-bottom: 1px solid rgba(255,255,255,0.05); }
  .table-row { border-bottom: 1px solid rgba(255,255,255,0.04); transition: background 0.15s; }
  .table-row:last-child { border-bottom: none; }
  .table-row:hover { background: rgba(255,255,255,0.02); }
  .admin-table td { padding: 0.75rem 0.875rem; }
  .skeleton-row { height: 2.5rem; border-radius: 0.375rem; background: rgba(255,255,255,0.04); animation: shimmer 1.5s infinite; background-size: 200% 100%; }
  .admin-btn-ghost { display: inline-flex; align-items: center; gap: 0.375rem; padding: 0.375rem 0.75rem; border-radius: 0.5rem; font-size: 0.75rem; font-weight: 500; color: rgba(184,191,214,0.6); background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07); cursor: pointer; transition: all 0.15s; }
  .admin-btn-ghost:hover:not(:disabled) { background: rgba(255,255,255,0.08); color: white; }
  .admin-btn-ghost:disabled { opacity: 0.3; cursor: not-allowed; }
  .admin-error { padding: 0.75rem 1rem; border-radius: 0.75rem; background: rgba(248,113,113,0.08); border: 1px solid rgba(248,113,113,0.2); color: #f87171; font-size: 0.875rem; }
  @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
</style>
