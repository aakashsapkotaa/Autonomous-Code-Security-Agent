<script lang="ts">
  import { onMount } from 'svelte';
  import { adminGet } from '$lib/adminApi';
  import Dropdown from '$lib/components/admin/Dropdown.svelte';
  import { ShieldAlert, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-svelte';

  let vulns: any[] = [];
  let total = 0;
  let loading = true;
  let error = '';
  let severityFilter = '';
  let page = 1;
  const limit = 25;

  const SEVERITY_OPTIONS = [
    { value: '',         label: 'All severities' },
    { value: 'critical', label: 'Critical'       },
    { value: 'high',     label: 'High'           },
    { value: 'medium',   label: 'Medium'         },
    { value: 'low',      label: 'Low'            },
  ];

  async function load() {
    loading = true; error = '';
    try {
      const params = new URLSearchParams({ page: String(page), limit: String(limit) });
      if (severityFilter) params.set('severity', severityFilter);
      const res: any = await adminGet(`/vulnerabilities?${params}`);
      vulns = res.vulnerabilities; total = res.total;
    } catch (e: any) { error = e.message; }
    finally { loading = false; }
  }

  onMount(load);

  const SEV_COLORS: Record<string, string> = {
    critical: '#f87171', high: '#fb923c', medium: '#fbbf24', low: '#34d399',
  };
  $: totalPages = Math.ceil(total / limit);
</script>

<svelte:head><title>Vulnerabilities — Admin</title></svelte:head>

<div class="space-y-5">
  <div class="flex flex-wrap items-center justify-between gap-3">
    <div>
      <h1 class="text-xl font-headline font-bold text-white">Global Vulnerability Center</h1>
      <p class="text-xs text-on-surface-variant/50 mt-0.5">{total} total vulnerabilities</p>
    </div>
    <div class="flex gap-2 items-center">
      <Dropdown
        bind:value={severityFilter}
        options={SEVERITY_OPTIONS}
        onChange={() => { page = 1; load(); }}
      />
      <button class="admin-btn-ghost" on:click={load}><RefreshCw class="w-3.5 h-3.5" /></button>
    </div>
  </div>

  {#if error}<div class="admin-error">{error}</div>{/if}

  <div class="admin-table-wrap">
    <table class="admin-table">
      <thead><tr>
        <th>Severity</th><th>Repository</th><th>File</th><th>Type</th><th>Tool</th><th>CVSS</th><th>Fixed</th><th>Detected</th>
      </tr></thead>
      <tbody>
        {#if loading}
          {#each Array(10) as _}<tr><td colspan="8"><div class="skeleton-row"></div></td></tr>{/each}
        {:else}
          {#each vulns as v}
            {@const color = SEV_COLORS[v.severity] ?? '#94a3b8'}
            <tr class="table-row">
              <td>
                <span class="sev-badge" style="color:{color}; background:{color}18; border-color:{color}33">
                  {v.severity?.toUpperCase()}
                </span>
              </td>
              <td class="text-xs text-white">{v.scans?.repositories?.repo_name ?? '—'}</td>
              <td class="text-[11px] text-on-surface-variant/60 font-mono max-w-[140px] truncate">{v.file_path}</td>
              <td class="text-xs text-on-surface-variant/70">{v.vulnerability_type}</td>
              <td class="text-xs text-on-surface-variant/50">{v.tool ?? '—'}</td>
              <td class="text-xs" style="color:{color}">{v.cvss_score ?? '—'}</td>
              <td>
                <span class="text-xs" style="color:{v.is_fixed ? '#34d399' : '#f87171'}">{v.is_fixed ? 'Yes' : 'No'}</span>
              </td>
              <td class="text-xs text-on-surface-variant/50">{v.detected_at ? new Date(v.detected_at).toLocaleDateString() : '—'}</td>
            </tr>
          {:else}
            <tr><td colspan="8" class="text-center text-xs text-on-surface-variant/40 py-8">No vulnerabilities found</td></tr>
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
  .admin-table { width: 100%; border-collapse: collapse; min-width: 700px; }
  .admin-table thead tr { background: rgba(255,255,255,0.02); }
  .admin-table th { padding: 0.625rem 0.875rem; text-align: left; font-size: 0.65rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(184,191,214,0.4); border-bottom: 1px solid rgba(255,255,255,0.05); white-space: nowrap; }
  .table-row { border-bottom: 1px solid rgba(255,255,255,0.04); transition: background 0.15s; }
  .table-row:last-child { border-bottom: none; }
  .table-row:hover { background: rgba(255,255,255,0.02); }
  .admin-table td { padding: 0.625rem 0.875rem; }
  .sev-badge { display: inline-flex; padding: 0.15rem 0.5rem; border-radius: 0.25rem; font-size: 0.65rem; font-weight: 700; border: 1px solid; }
  .skeleton-row { height: 2.5rem; border-radius: 0.375rem; background: rgba(255,255,255,0.04); animation: shimmer 1.5s infinite; background-size: 200% 100%; }
  .admin-btn-ghost { display: inline-flex; align-items: center; gap: 0.375rem; padding: 0.375rem 0.75rem; border-radius: 0.5rem; font-size: 0.75rem; font-weight: 500; color: rgba(184,191,214,0.6); background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07); cursor: pointer; transition: all 0.15s; }
  .admin-btn-ghost:hover:not(:disabled) { background: rgba(255,255,255,0.08); color: white; }
  .admin-btn-ghost:disabled { opacity: 0.3; cursor: not-allowed; }
  .admin-error { padding: 0.75rem 1rem; border-radius: 0.75rem; background: rgba(248,113,113,0.08); border: 1px solid rgba(248,113,113,0.2); color: #f87171; font-size: 0.875rem; }
  @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
</style>
