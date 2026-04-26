<script lang="ts">
  import { onMount } from 'svelte';
  import { adminGet } from '$lib/adminApi';
  import { RefreshCw, ScanLine, AlertTriangle, ShieldAlert, CheckCircle2, BarChart2 } from 'lucide-svelte';
  import Dropdown from '$lib/components/admin/Dropdown.svelte';

  const DAYS_OPTIONS = [
    { value: 7,  label: 'Last 7 days'  },
    { value: 30, label: 'Last 30 days' },
    { value: 90, label: 'Last 90 days' },
  ];

  let data: any = null;
  let loading = true;
  let error = '';
  let days = 30;

  async function load() {
    loading = true; error = '';
    try {
      data = await adminGet(`/analytics?days=${days}`);
    } catch (e: any) { error = e.message; }
    finally { loading = false; }
  }

  onMount(load);

  const SEVERITY_COLORS: Record<string, string> = {
    critical: '#f87171',
    high:     '#fb923c',
    medium:   '#fbbf24',
    low:      '#34d399',
  };

  const STATUS_COLORS: Record<string, string> = {
    completed: '#34d399',
    running:   '#3a86ff',
    pending:   '#fbbf24',
    failed:    '#f87171',
  };

  function pct(val: number, total: number) {
    if (!total) return 0;
    return Math.round((val / total) * 100);
  }

  $: stats = data ? [
    { label: 'Total Scans',      value: data.total_scans      ?? 0, icon: ScanLine,      color: '#3a86ff' },
    { label: 'Total Vulns',      value: data.total_vulns      ?? data.total_vulnerabilities ?? 0, icon: AlertTriangle, color: '#fbbf24' },
    { label: 'Critical Vulns',   value: data.critical_vulns   ?? data.critical_vulnerabilities ?? 0, icon: ShieldAlert,   color: '#f87171' },
    { label: 'Completed Scans',  value: data.completed_scans  ?? 0, icon: CheckCircle2,  color: '#34d399' },
  ] : [];

  $: severityBreakdown = data?.severity_breakdown ?? data?.vulnerabilities_by_severity ?? {};
  $: topRepos = data?.top_repos ?? data?.top_repositories ?? [];
  $: statusBreakdown = data?.scan_status_breakdown ?? data?.scans_by_status ?? {};
  $: totalSeverity = Object.values(severityBreakdown).reduce((a: any, b: any) => a + b, 0) as number;
</script>

<svelte:head><title>Analytics — Admin</title></svelte:head>

<div class="space-y-6">
  <div class="flex flex-wrap items-center justify-between gap-3">
    <div>
      <h1 class="text-xl font-bold text-white">Analytics</h1>
      <p class="text-xs text-muted mt-0.5">Platform-wide statistics</p>
    </div>
    <div class="flex items-center gap-2">
      <Dropdown
        bind:value={days}
        options={DAYS_OPTIONS}
        onChange={load}
      />
      <button class="admin-btn-ghost" on:click={load}><RefreshCw class="w-3.5 h-3.5" /> Refresh</button>
    </div>
  </div>

  {#if error}<div class="admin-error">{error}</div>{/if}

  <!-- Stat cards -->
  <div class="stats-grid">
    {#if loading}
      {#each Array(4) as _}
        <div class="skeleton-card"></div>
      {/each}
    {:else}
      {#each stats as s}
        <div class="stat-card">
          <div class="stat-icon" style="background:{s.color}15; color:{s.color}; border-color:{s.color}30">
            <svelte:component this={s.icon} class="w-4 h-4" />
          </div>
          <div>
            <p class="stat-value">{s.value.toLocaleString()}</p>
            <p class="stat-label">{s.label}</p>
          </div>
        </div>
      {/each}
    {/if}
  </div>

  <div class="two-col">
    <!-- Severity breakdown -->
    <div class="admin-card">
      <h2 class="section-title"><BarChart2 class="w-4 h-4" /> Severity Breakdown</h2>
      {#if loading}
        <div class="space-y-3 mt-4">
          {#each Array(4) as _}<div class="skeleton-bar"></div>{/each}
        </div>
      {:else if totalSeverity === 0}
        <p class="text-xs text-muted mt-4">No vulnerability data available.</p>
      {:else}
        <div class="space-y-3 mt-4">
          {#each ['critical','high','medium','low'] as sev}
            {@const count = severityBreakdown[sev] ?? 0}
            {@const width = pct(count, totalSeverity)}
            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="capitalize font-medium" style="color:{SEVERITY_COLORS[sev]}">{sev}</span>
                <span class="text-muted">{count}</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill" style="width:{width}%; background:{SEVERITY_COLORS[sev]}"></div>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Scan status breakdown -->
    <div class="admin-card">
      <h2 class="section-title"><ScanLine class="w-4 h-4" /> Scan Status</h2>
      {#if loading}
        <div class="flex flex-wrap gap-2 mt-4">
          {#each Array(4) as _}<div class="skeleton-pill"></div>{/each}
        </div>
      {:else}
        <div class="flex flex-wrap gap-2 mt-4">
          {#each Object.entries(statusBreakdown) as [status, count]}
            <div class="status-pill" style="color:{STATUS_COLORS[status]??'#94a3b8'}; background:{STATUS_COLORS[status]??'#94a3b8'}15; border-color:{STATUS_COLORS[status]??'#94a3b8'}30">
              <span class="status-dot" style="background:{STATUS_COLORS[status]??'#94a3b8'}"></span>
              <span class="capitalize">{status}</span>
              <span class="font-bold">{count}</span>
            </div>
          {:else}
            <p class="text-xs text-muted">No scan data available.</p>
          {/each}
        </div>
      {/if}
    </div>
  </div>

  <!-- Top repos -->
  <div class="admin-card">
    <h2 class="section-title"><AlertTriangle class="w-4 h-4" /> Top 10 Repos by Vulnerability Count</h2>
    {#if loading}
      <div class="space-y-2 mt-4">
        {#each Array(5) as _}<div class="skeleton-row"></div>{/each}
      </div>
    {:else if topRepos.length === 0}
      <p class="text-xs text-muted mt-4">No repository data available.</p>
    {:else}
      <div class="repo-rank-list">
        {#each topRepos.slice(0, 10) as repo, i}
          <div class="repo-rank-item">
            <span class="rank-num">{i + 1}</span>
            <span class="text-xs font-medium text-white flex-1 truncate">{repo.repo_name ?? repo.name ?? '—'}</span>
            <span class="vuln-count" style="color:{i < 3 ? '#f87171' : '#fbbf24'}">{repo.vuln_count ?? repo.vulnerability_count ?? 0}</span>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>

<style>
  .text-muted { color: rgba(184,191,214,0.5); }

  .filter-select { display: none; } /* replaced by Dropdown component */

  .stats-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }

  .stat-card {
    display: flex; align-items: center; gap: 0.875rem;
    padding: 1.125rem; border-radius: 0.875rem;
    border: 1px solid rgba(255,255,255,0.06); background: rgba(255,255,255,0.02);
  }
  .stat-icon {
    width: 2.5rem; height: 2.5rem; border-radius: 0.625rem;
    display: flex; align-items: center; justify-content: center;
    border: 1px solid; flex-shrink: 0;
  }
  .stat-value { font-size: 1.375rem; font-weight: 700; color: white; line-height: 1; }
  .stat-label { font-size: 0.7rem; color: rgba(184,191,214,0.5); margin-top: 0.25rem; }

  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
  @media (max-width: 768px) { .two-col { grid-template-columns: 1fr; } }

  .admin-card {
    padding: 1.125rem; border-radius: 0.875rem;
    border: 1px solid rgba(255,255,255,0.06); background: rgba(255,255,255,0.02);
  }

  .section-title {
    display: flex; align-items: center; gap: 0.5rem;
    font-size: 0.8125rem; font-weight: 600; color: rgba(184,191,214,0.8);
  }

  .bar-track { height: 0.375rem; border-radius: 9999px; background: rgba(255,255,255,0.06); overflow: hidden; }
  .bar-fill { height: 100%; border-radius: 9999px; transition: width 0.5s ease; }

  .status-pill {
    display: inline-flex; align-items: center; gap: 0.375rem;
    padding: 0.375rem 0.75rem; border-radius: 9999px;
    font-size: 0.75rem; font-weight: 500; border: 1px solid;
  }
  .status-dot { width: 0.4rem; height: 0.4rem; border-radius: 50%; }

  .repo-rank-list { display: flex; flex-direction: column; gap: 0.375rem; margin-top: 1rem; }
  .repo-rank-item {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.5rem 0.75rem; border-radius: 0.5rem;
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04);
  }
  .rank-num {
    width: 1.5rem; height: 1.5rem; border-radius: 0.375rem;
    background: rgba(255,255,255,0.06); display: flex; align-items: center; justify-content: center;
    font-size: 0.65rem; font-weight: 700; color: rgba(184,191,214,0.5); flex-shrink: 0;
  }
  .vuln-count { font-size: 0.8125rem; font-weight: 700; flex-shrink: 0; }

  .skeleton-card { height: 5rem; border-radius: 0.875rem; background: linear-gradient(90deg, rgba(255,255,255,0.04) 25%, rgba(255,255,255,0.07) 50%, rgba(255,255,255,0.04) 75%); animation: shimmer 1.5s infinite; background-size: 200% 100%; }
  .skeleton-bar  { height: 2rem; border-radius: 0.375rem; background: linear-gradient(90deg, rgba(255,255,255,0.04) 25%, rgba(255,255,255,0.07) 50%, rgba(255,255,255,0.04) 75%); animation: shimmer 1.5s infinite; background-size: 200% 100%; }
  .skeleton-pill { height: 2rem; width: 6rem; border-radius: 9999px; background: linear-gradient(90deg, rgba(255,255,255,0.04) 25%, rgba(255,255,255,0.07) 50%, rgba(255,255,255,0.04) 75%); animation: shimmer 1.5s infinite; background-size: 200% 100%; }
  .skeleton-row  { height: 2.5rem; border-radius: 0.375rem; background: linear-gradient(90deg, rgba(255,255,255,0.04) 25%, rgba(255,255,255,0.07) 50%, rgba(255,255,255,0.04) 75%); animation: shimmer 1.5s infinite; background-size: 200% 100%; }

  .admin-btn-ghost {
    display: inline-flex; align-items: center; gap: 0.375rem;
    padding: 0.375rem 0.75rem; border-radius: 0.5rem;
    font-size: 0.75rem; font-weight: 500; color: rgba(184,191,214,0.6);
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);
    cursor: pointer; transition: all 0.15s;
  }
  .admin-btn-ghost:hover { background: rgba(255,255,255,0.08); color: white; }

  .admin-error { padding: 0.75rem 1rem; border-radius: 0.75rem; background: rgba(248,113,113,0.08); border: 1px solid rgba(248,113,113,0.2); color: #f87171; font-size: 0.875rem; }

  @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
</style>
