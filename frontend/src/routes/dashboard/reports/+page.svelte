<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { supabase } from '$lib/supabaseClient';
  import { ShieldAlert, GitBranch, CheckCircle, XCircle, Clock, Activity, ArrowLeft, ExternalLink } from 'lucide-svelte';

  let scans: any[] = [];
  let repos: any[] = [];
  let loading = true;
  let userId = '';

  onMount(async () => {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) { goto('/'); return; }
    userId = session.user.id;

    const [repoRes, scanRes] = await Promise.all([
      supabase.from('repositories').select('id, repo_name, repo_url').eq('user_id', userId),
      supabase.from('scans')
        .select('*, repositories(repo_name, repo_url)')
        .order('created_at', { ascending: false })
        .limit(50),
    ]);

    repos  = repoRes.data  || [];
    scans  = scanRes.data  || [];
    loading = false;
  });

  const SEV_COLORS: Record<string, string> = {
    critical: '#f87171', high: '#fb923c', medium: '#fbbf24', low: '#34d399',
  };

  function statusMeta(status: string) {
    if (status === 'completed') return { icon: CheckCircle, color: '#34d399', label: 'Completed' };
    if (status === 'running')   return { icon: Activity,    color: '#00d9ff', label: 'Running'   };
    if (status === 'failed')    return { icon: XCircle,     color: '#f87171', label: 'Failed'    };
    return                             { icon: Clock,       color: '#fbbf24', label: 'Pending'   };
  }

  function fmt(iso: string) {
    return new Date(iso).toLocaleString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  }

  $: totalVulns    = scans.reduce((a, s) => a + (s.total_vulnerabilities || 0), 0);
  $: criticalVulns = scans.reduce((a, s) => a + (s.critical_count || 0), 0);
  $: completedScans = scans.filter(s => s.status === 'completed').length;
  $: prsCreated    = scans.filter(s => s.pr_url).length;
</script>

<svelte:head><title>Reports — SecureShift</title></svelte:head>

<div class="min-h-screen bg-[#060914] text-white px-5 sm:px-8 lg:px-12 py-8 max-w-6xl mx-auto">

  <!-- Header -->
  <div class="flex items-center gap-4 mb-8">
    <button class="back-btn" on:click={() => goto('/dashboard')}>
      <ArrowLeft class="w-4 h-4" /> Dashboard
    </button>
    <div>
      <h1 class="text-2xl font-bold text-white">Security Reports</h1>
      <p class="text-xs text-white/40 mt-0.5">Full scan history and vulnerability summary</p>
    </div>
  </div>

  {#if loading}
    <div class="flex items-center justify-center py-24">
      <div class="w-8 h-8 border-2 border-neon-cyan/20 border-t-neon-cyan rounded-full animate-spin"></div>
    </div>
  {:else}

    <!-- Summary cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {#each [
        { label: 'Total Scans',       value: scans.length,    color: '#3a86ff' },
        { label: 'Completed',         value: completedScans,  color: '#34d399' },
        { label: 'Vulnerabilities',   value: totalVulns,      color: '#f87171' },
        { label: 'PRs Created',       value: prsCreated,      color: '#a78bfa' },
      ] as card}
        <div class="summary-card" style="--c:{card.color}">
          <p class="text-[10px] font-semibold uppercase tracking-wider text-white/40">{card.label}</p>
          <p class="text-3xl font-bold mt-2" style="color:{card.color}">{card.value}</p>
        </div>
      {/each}
    </div>

    <!-- Scan history table -->
    <div class="report-card">
      <h2 class="text-sm font-semibold text-white/70 mb-4">Scan History</h2>

      {#if scans.length === 0}
        <div class="text-center py-12">
          <ShieldAlert class="w-10 h-10 text-white/10 mx-auto mb-3" />
          <p class="text-sm text-white/30">No scans yet. Go to the dashboard and click Scan on a repository.</p>
          <button class="back-btn mt-4" on:click={() => goto('/dashboard')}>Go to Dashboard</button>
        </div>
      {:else}
        <div class="overflow-x-auto">
          <table class="w-full text-sm border-collapse">
            <thead>
              <tr class="border-b border-white/[0.05]">
                <th class="th">Repository</th>
                <th class="th">Status</th>
                <th class="th hidden md:table-cell">Vulns</th>
                <th class="th hidden lg:table-cell">Critical</th>
                <th class="th hidden lg:table-cell">PR</th>
                <th class="th hidden md:table-cell">Date</th>
              </tr>
            </thead>
            <tbody>
              {#each scans as scan}
                {@const sm = statusMeta(scan.status)}
                <tr class="scan-row">
                  <td class="td">
                    <div class="flex items-center gap-2">
                      <div class="repo-dot"><GitBranch class="w-3 h-3 text-neon-cyan" /></div>
                      <div>
                        <p class="font-medium text-white text-xs">{scan.repositories?.repo_name ?? '—'}</p>
                        <p class="text-[10px] text-white/30 truncate max-w-[160px]">
                          {scan.repositories?.repo_url?.replace('https://github.com/', '') ?? ''}
                        </p>
                      </div>
                    </div>
                  </td>
                  <td class="td">
                    <span class="status-pill" style="color:{sm.color}; background:{sm.color}18; border-color:{sm.color}33">
                      <svelte:component this={sm.icon} class="w-3 h-3" />
                      {sm.label}
                    </span>
                  </td>
                  <td class="td hidden md:table-cell">
                    <span class="text-xs font-semibold" style="color:{(scan.total_vulnerabilities||0) > 0 ? '#f87171' : '#34d399'}">
                      {scan.total_vulnerabilities ?? 0}
                    </span>
                  </td>
                  <td class="td hidden lg:table-cell">
                    <span class="text-xs font-semibold text-red-400">{scan.critical_count ?? 0}</span>
                  </td>
                  <td class="td hidden lg:table-cell">
                    {#if scan.pr_url}
                      <a href={scan.pr_url} target="_blank" rel="noopener noreferrer"
                        class="text-[11px] text-neon-cyan hover:underline flex items-center gap-1">
                        View PR <ExternalLink class="w-2.5 h-2.5" />
                      </a>
                    {:else}
                      <span class="text-[11px] text-white/20">—</span>
                    {/if}
                  </td>
                  <td class="td hidden md:table-cell text-[11px] text-white/30">
                    {fmt(scan.created_at)}
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </div>

  {/if}
</div>

<style>
  .back-btn {
    display: inline-flex; align-items: center; gap: 0.375rem;
    padding: 0.375rem 0.75rem; border-radius: 0.5rem;
    font-size: 0.75rem; font-weight: 500;
    color: rgba(184,191,214,0.6);
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    cursor: pointer; transition: all 0.15s;
  }
  .back-btn:hover { background: rgba(255,255,255,0.08); color: white; }

  .summary-card {
    padding: 1.125rem; border-radius: 0.875rem;
    border: 1px solid color-mix(in srgb, var(--c) 20%, transparent);
    background: color-mix(in srgb, var(--c) 6%, transparent);
  }

  .report-card {
    padding: 1.25rem; border-radius: 0.875rem;
    border: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.02);
  }

  .th {
    padding: 0.5rem 0.75rem; text-align: left;
    font-size: 0.65rem; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: rgba(184,191,214,0.35);
  }

  .scan-row { border-bottom: 1px solid rgba(255,255,255,0.04); transition: background 0.15s; }
  .scan-row:last-child { border-bottom: none; }
  .scan-row:hover { background: rgba(255,255,255,0.02); }

  .td { padding: 0.75rem 0.75rem; vertical-align: middle; }

  .repo-dot {
    width: 1.75rem; height: 1.75rem; border-radius: 0.375rem;
    border: 1px solid rgba(0,217,255,0.15); background: rgba(0,217,255,0.07);
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  }

  .status-pill {
    display: inline-flex; align-items: center; gap: 0.3rem;
    padding: 0.2rem 0.5rem; border-radius: 9999px;
    font-size: 0.7rem; font-weight: 500; border: 1px solid;
  }
</style>
