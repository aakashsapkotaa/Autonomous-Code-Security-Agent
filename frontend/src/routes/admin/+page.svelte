<script lang="ts">
  import { onMount } from 'svelte';
  import { adminGet } from '$lib/adminApi';
  import {
    Users, GitBranch, ScanLine, AlertTriangle, Bot,
    GitPullRequest, TrendingUp, Activity, Zap, ShieldAlert,
    RefreshCw, CheckCircle, XCircle, Clock
  } from 'lucide-svelte';

  let overview: any = null;
  let analytics: any = null;
  let loading = true;
  let error = '';

  onMount(async () => {
    try {
      console.log('[admin overview] fetching data...');
      [overview, analytics] = await Promise.all([
        adminGet('/overview'),
        adminGet('/analytics?days=14'),
      ]);
      console.log('[admin overview] data loaded:', { overview, analytics });
    } catch (e: any) {
      console.error('[admin overview] fetch error:', e);
      error = e.message;
    } finally {
      loading = false;
    }
  });

  const STAT_CARDS = [
    { key: 'total_users',           label: 'Total Users',        icon: Users,         color: '#00d9ff', gradient: 'from-neon-cyan to-neon-blue'   },
    { key: 'total_repositories',    label: 'Repositories',       icon: GitBranch,     color: '#9d4edd', gradient: 'from-neon-purple to-accent-1'  },
    { key: 'total_scans',           label: 'Total Scans',        icon: ScanLine,      color: '#3a86ff', gradient: 'from-neon-blue to-neon-cyan'   },
    { key: 'running_scans',         label: 'Running Scans',      icon: Activity,      color: '#fbbf24', gradient: 'from-yellow-400 to-orange-400' },
    { key: 'total_vulnerabilities', label: 'Vulnerabilities',    icon: AlertTriangle, color: '#f87171', gradient: 'from-red-400 to-neon-pink'     },
    { key: 'critical_vulnerabilities', label: 'Critical',        icon: ShieldAlert,   color: '#ff006e', gradient: 'from-neon-pink to-accent-2'   },
    { key: 'ai_fixes_generated',    label: 'AI Fixes',           icon: Bot,           color: '#34d399', gradient: 'from-emerald-400 to-neon-cyan' },
    { key: 'pull_requests_created', label: 'PRs Created',        icon: GitPullRequest,color: '#a78bfa', gradient: 'from-violet-400 to-neon-purple'},
  ];

  function barHeight(count: number, max: number): number {
    if (!max) return 4;
    return Math.max(4, Math.round((count / max) * 80));
  }

  $: scanDays   = analytics?.scans_per_day ?? [];
  $: vulnDays   = analytics?.vulns_per_day ?? [];
  $: maxScans   = Math.max(...scanDays.map((d: any) => d.count), 1);
  $: maxVulns   = Math.max(...vulnDays.map((d: any) => d.count), 1);
  $: topRepos   = analytics?.top_repos?.slice(0, 5) ?? [];
  $: sevBreak   = analytics?.severity_breakdown ?? {};
  $: statusBreak = analytics?.scan_status_breakdown ?? {};
</script>

<svelte:head><title>Admin Overview — SecureShift</title></svelte:head>

<div class="space-y-6">
  <!-- Page header -->
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-xl font-headline font-bold text-white">Admin Overview</h1>
      <p class="text-xs text-on-surface-variant/50 mt-0.5">Platform-wide metrics and health</p>
    </div>
    <button class="admin-btn-ghost" on:click={() => location.reload()}>
      <RefreshCw class="w-3.5 h-3.5" /> Refresh
    </button>
  </div>

  {#if error}
    <div class="admin-error">
      <div class="mb-2">{error}</div>
      <a href="/admin/debug" class="text-xs underline hover:text-white transition-colors">
        → Open Debug Page for troubleshooting
      </a>
    </div>
  {:else if loading}
    <!-- Skeleton -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {#each Array(8) as _}
        <div class="stat-card skeleton"></div>
      {/each}
    </div>
  {:else if overview}

    <!-- Stat cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {#each STAT_CARDS as s}
        <div class="stat-card" style="--c:{s.color}">
          <div class="flex items-start justify-between mb-3">
            <span class="text-[10px] font-semibold uppercase tracking-wider text-on-surface-variant/50">{s.label}</span>
            <div class="stat-icon" style="background:{s.color}18; border-color:{s.color}33">
              <svelte:component this={s.icon} class="w-3.5 h-3.5" style="color:{s.color}" />
            </div>
          </div>
          <div class="text-3xl font-headline font-bold bg-gradient-to-r {s.gradient} bg-clip-text text-transparent">
            {overview[s.key] ?? 0}
          </div>
        </div>
      {/each}
    </div>

    <!-- Charts row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">

      <!-- Scans per day -->
      <div class="admin-card">
        <div class="admin-card-header">
          <ScanLine class="w-4 h-4 text-neon-cyan" />
          <span>Scans — Last 14 Days</span>
        </div>
        <div class="chart-bars">
          {#each scanDays.slice(-14) as d}
            <div class="chart-col">
              <div class="chart-bar bg-gradient-to-t from-neon-cyan/60 to-neon-cyan"
                style="height:{barHeight(d.count, maxScans)}px"
                title="{d.date}: {d.count}">
              </div>
              <span class="chart-label">{d.date.slice(5)}</span>
            </div>
          {/each}
          {#if scanDays.length === 0}
            <p class="text-xs text-on-surface-variant/40 m-auto">No data yet</p>
          {/if}
        </div>
      </div>

      <!-- Vulns per day -->
      <div class="admin-card">
        <div class="admin-card-header">
          <AlertTriangle class="w-4 h-4 text-red-400" />
          <span>Vulnerabilities — Last 14 Days</span>
        </div>
        <div class="chart-bars">
          {#each vulnDays.slice(-14) as d}
            <div class="chart-col">
              <div class="chart-bar bg-gradient-to-t from-red-500/60 to-red-400"
                style="height:{barHeight(d.count, maxVulns)}px"
                title="{d.date}: {d.count}">
              </div>
              <span class="chart-label">{d.date.slice(5)}</span>
            </div>
          {/each}
          {#if vulnDays.length === 0}
            <p class="text-xs text-on-surface-variant/40 m-auto">No data yet</p>
          {/if}
        </div>
      </div>
    </div>

    <!-- Bottom row -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">

      <!-- Severity breakdown -->
      <div class="admin-card">
        <div class="admin-card-header">
          <ShieldAlert class="w-4 h-4 text-neon-pink" />
          <span>Severity Breakdown</span>
        </div>
        <div class="space-y-2.5 mt-2">
          {#each [
            { key: 'critical', color: '#f87171', label: 'Critical' },
            { key: 'high',     color: '#fb923c', label: 'High'     },
            { key: 'medium',   color: '#fbbf24', label: 'Medium'   },
            { key: 'low',      color: '#34d399', label: 'Low'      },
          ] as s}
            {@const total = (sevBreak.critical||0)+(sevBreak.high||0)+(sevBreak.medium||0)+(sevBreak.low||0)}
            {@const pct = total ? Math.round(((sevBreak[s.key]||0)/total)*100) : 0}
            <div>
              <div class="flex justify-between text-[11px] mb-1">
                <span style="color:{s.color}">{s.label}</span>
                <span class="text-on-surface-variant/50">{sevBreak[s.key]||0} ({pct}%)</span>
              </div>
              <div class="h-1.5 rounded-full bg-white/[0.06] overflow-hidden">
                <div class="h-full rounded-full transition-all duration-700"
                  style="width:{pct}%; background:{s.color}"></div>
              </div>
            </div>
          {/each}
        </div>
      </div>

      <!-- Scan status -->
      <div class="admin-card">
        <div class="admin-card-header">
          <Activity class="w-4 h-4 text-neon-blue" />
          <span>Scan Status</span>
        </div>
        <div class="space-y-2 mt-2">
          {#each [
            { key: 'completed', icon: CheckCircle, color: '#34d399' },
            { key: 'running',   icon: Activity,    color: '#00d9ff' },
            { key: 'failed',    icon: XCircle,     color: '#f87171' },
            { key: 'pending',   icon: Clock,       color: '#fbbf24' },
          ] as s}
            <div class="flex items-center justify-between py-1.5 border-b border-white/[0.04] last:border-0">
              <div class="flex items-center gap-2">
                <svelte:component this={s.icon} class="w-3.5 h-3.5" style="color:{s.color}" />
                <span class="text-xs capitalize text-on-surface-variant/70">{s.key}</span>
              </div>
              <span class="text-sm font-semibold" style="color:{s.color}">{statusBreak[s.key]||0}</span>
            </div>
          {/each}
        </div>
      </div>

      <!-- Top repos -->
      <div class="admin-card">
        <div class="admin-card-header">
          <TrendingUp class="w-4 h-4 text-neon-purple" />
          <span>Most Vulnerable Repos</span>
        </div>
        <div class="space-y-2 mt-2">
          {#each topRepos as r, i}
            <div class="flex items-center gap-2 py-1">
              <span class="text-[10px] font-bold text-on-surface-variant/30 w-4">{i+1}</span>
              <span class="text-xs text-white truncate flex-1">{r.repo_name}</span>
              <span class="text-xs font-semibold text-red-400">{r.vuln_count}</span>
            </div>
          {:else}
            <p class="text-xs text-on-surface-variant/40">No data yet</p>
          {/each}
        </div>
      </div>
    </div>

  {/if}
</div>

<style>
  .stat-card {
    padding: 1.125rem; border-radius: 0.875rem;
    border: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.02);
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  .stat-card:hover { border-color: color-mix(in srgb, var(--c) 25%, transparent); box-shadow: 0 0 20px color-mix(in srgb, var(--c) 10%, transparent); }
  .stat-card.skeleton { height: 100px; animation: shimmer 1.5s infinite; background: linear-gradient(90deg, rgba(255,255,255,0.03) 25%, rgba(255,255,255,0.06) 50%, rgba(255,255,255,0.03) 75%); background-size: 200% 100%; }

  .stat-icon {
    width: 1.875rem; height: 1.875rem; border-radius: 0.5rem;
    border: 1px solid; display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  }

  .admin-card {
    padding: 1.125rem; border-radius: 0.875rem;
    border: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.02);
  }
  .admin-card-header {
    display: flex; align-items: center; gap: 0.5rem;
    font-size: 0.8125rem; font-weight: 600; color: rgba(184,191,214,0.8);
    margin-bottom: 0.75rem;
  }

  .chart-bars {
    display: flex; align-items: flex-end; gap: 0.25rem;
    height: 90px; overflow: hidden;
  }
  .chart-col { display: flex; flex-direction: column; align-items: center; gap: 0.25rem; flex: 1; min-width: 0; }
  .chart-bar { width: 100%; border-radius: 2px 2px 0 0; min-height: 4px; transition: height 0.5s ease; }
  .chart-label { font-size: 0.55rem; color: rgba(184,191,214,0.3); white-space: nowrap; overflow: hidden; }

  .admin-btn-ghost {
    display: inline-flex; align-items: center; gap: 0.375rem;
    padding: 0.375rem 0.75rem; border-radius: 0.5rem;
    font-size: 0.75rem; font-weight: 500; color: rgba(184,191,214,0.6);
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);
    cursor: pointer; transition: all 0.15s;
  }
  .admin-btn-ghost:hover { background: rgba(255,255,255,0.08); color: white; }

  .admin-error {
    padding: 0.75rem 1rem; border-radius: 0.75rem;
    background: rgba(248,113,113,0.08); border: 1px solid rgba(248,113,113,0.2);
    color: #f87171; font-size: 0.875rem;
  }

  @keyframes shimmer {
    0%   { background-position: -200% 0; }
    100% { background-position:  200% 0; }
  }
</style>
