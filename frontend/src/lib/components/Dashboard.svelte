<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { supabase } from '$lib/supabaseClient';
  import { apiGet } from '$lib/api';
  import {
    Shield, AlertTriangle, CheckCircle, LogOut, GitBranch,
    Plus, Zap, FileText, Bell, ChevronDown, User,
    Activity, TrendingUp, Clock, Settings, LayoutDashboard
  } from 'lucide-svelte';
  import RepoList from './RepoList.svelte';
  import NotificationsPanel from './NotificationsPanel.svelte';
  import type { User as SupaUser } from '@supabase/supabase-js';

  export let user: SupaUser;

  let repositories: any[] = [];
  let scans: any[] = [];
  let loading = true;
  let error: string | null = null;
  let profileOpen = false;
  let notifOpen = false;
  let unreadCount = 0;
  let isAdmin = false;
  let animatedCounts = { repos: 0, scans: 0, vulns: 0, fixed: 0 };

  // Derived stats
  $: totalVulns = scans.reduce((a, s) => a + (s.total_vulnerabilities || 0), 0);
  $: fixedVulns = scans.reduce((a, s) => a + (s.fixed_count || 0), 0);
  $: activeScans = scans.filter(s => s.status === 'running' || s.status === 'pending').length;

  $: displayName = user.user_metadata?.full_name || user.email?.split('@')[0] || 'User';
  $: initials = displayName.slice(0, 2).toUpperCase();

  onMount(async () => {
    await loadData();
    animateCounters();
    fetchUnreadCount();
    checkAdminRole();
  });

  async function checkAdminRole() {
    try {
      const profile: any = await apiGet('/api/profile');
      // role is on the DB user row
      const dbUser = await supabase.from('users').select('role').eq('id', user.id).single();
      isAdmin = ['admin', 'super_admin', 'enterprise_manager'].includes(dbUser.data?.role ?? '');
    } catch { /* silent */ }
  }

  async function fetchUnreadCount() {
    try {
      const res: any = await apiGet('/api/notifications?limit=1');
      unreadCount = res.unread_count ?? 0;
    } catch { /* silent */ }
  }

  async function loadData() {
    loading = true; error = null;
    const [repoRes, scanRes] = await Promise.all([
      supabase.from('repositories').select('*, scans(id, status, created_at)').eq('user_id', user.id).order('created_at', { ascending: false }),
      supabase.from('scans').select('*').order('created_at', { ascending: false }).limit(10),
    ]);
    if (repoRes.error) { error = repoRes.error.message; }
    else {
      // Attach last_scan_id to each repo for the PR button
      repositories = (repoRes.data || []).map((r: any) => ({
        ...r,
        last_scan_id: r.scans?.sort((a: any, b: any) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        )[0]?.id ?? null,
      }));
    }
    scans = scanRes.data || [];
    loading = false;
    animateCounters();
  }

  function animateCounters() {
    const targets = {
      repos: repositories.length,
      scans: activeScans,
      vulns: totalVulns,
      fixed: fixedVulns,
    };
    const duration = 800;
    const steps = 30;
    let step = 0;
    const interval = setInterval(() => {
      step++;
      const progress = step / steps;
      const ease = 1 - Math.pow(1 - progress, 3);
      animatedCounts = {
        repos: Math.round(targets.repos * ease),
        scans: Math.round(targets.scans * ease),
        vulns: Math.round(targets.vulns * ease),
        fixed: Math.round(targets.fixed * ease),
      };
      if (step >= steps) clearInterval(interval);
    }, duration / steps);
  }

  async function handleSignOut() {
    await supabase.auth.signOut();
    window.location.href = '/';
  }

  const stats = [
    {
      key: 'repos',
      label: 'Repositories',
      icon: GitBranch,
      color: 'cyan',
      gradient: 'from-neon-cyan to-neon-blue',
      bg: 'rgba(0,217,255,0.08)',
      border: 'rgba(0,217,255,0.15)',
      glow: 'rgba(0,217,255,0.2)',
    },
    {
      key: 'scans',
      label: 'Active Scans',
      icon: Activity,
      color: 'purple',
      gradient: 'from-neon-purple to-accent-1',
      bg: 'rgba(157,78,221,0.08)',
      border: 'rgba(157,78,221,0.15)',
      glow: 'rgba(157,78,221,0.2)',
    },
    {
      key: 'vulns',
      label: 'Vulnerabilities',
      icon: AlertTriangle,
      color: 'pink',
      gradient: 'from-neon-pink to-accent-2',
      bg: 'rgba(247,37,133,0.08)',
      border: 'rgba(247,37,133,0.15)',
      glow: 'rgba(247,37,133,0.2)',
    },
    {
      key: 'fixed',
      label: 'Issues Fixed',
      icon: CheckCircle,
      color: 'green',
      gradient: 'from-green-400 to-emerald-500',
      bg: 'rgba(52,211,153,0.08)',
      border: 'rgba(52,211,153,0.15)',
      glow: 'rgba(52,211,153,0.2)',
    },
  ];

  const quickActions = [
    { label: 'Add Repository', icon: Plus,    color: 'cyan',   action: () => { addRepoTrigger = true; } },
    { label: 'Start Scan',     icon: Zap,     color: 'purple', action: () => { addRepoTrigger = true; } },
    { label: 'View Reports',   icon: FileText, color: 'pink',  action: () => goto('/dashboard/reports') },
  ];

  let addRepoTrigger = false;

  // Recent activity from scans
  $: recentActivity = scans.slice(0, 5).map(s => ({
    id: s.id,
    repo: repositories.find(r => r.id === s.repo_id)?.repo_name || 'Unknown repo',
    status: s.status,
    vulns: s.total_vulnerabilities || 0,
    time: s.created_at,
  }));

  function statusColor(status: string) {
    if (status === 'completed') return { dot: '#34d399', text: 'text-emerald-400', label: 'Completed' };
    if (status === 'running')   return { dot: '#00d9ff', text: 'text-neon-cyan',   label: 'Running'   };
    if (status === 'failed')    return { dot: '#f87171', text: 'text-red-400',     label: 'Failed'    };
    return                             { dot: '#9d4edd', text: 'text-neon-purple', label: 'Pending'   };
  }

  function timeAgo(iso: string) {
    const diff = Date.now() - new Date(iso).getTime();
    const m = Math.floor(diff / 60000);
    if (m < 1)  return 'just now';
    if (m < 60) return `${m}m ago`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}h ago`;
    return `${Math.floor(h / 24)}d ago`;
  }
</script>

<!-- ── Top nav ─────────────────────────────────────────────── -->
<nav class="dash-nav">
  <!-- Brand — always stays in dashboard when logged in -->
  <a href="/dashboard" class="flex items-center gap-2.5 group">
    <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-neon-cyan/20 to-neon-blue/10 border border-neon-cyan/20 flex items-center justify-center group-hover:border-neon-cyan/40 transition-all">
      <Shield class="w-4 h-4 text-neon-cyan" />
    </div>
    <span class="text-lg font-headline font-bold tracking-tight">
      <span class="text-white">Secure</span><span class="bg-gradient-to-r from-neon-cyan to-neon-blue bg-clip-text text-transparent">Shift</span>
    </span>
  </a>

  <!-- Right side -->
  <div class="flex items-center gap-3">
    <!-- Notification bell with unread badge -->
    <div class="relative">
      <button
        class="nav-icon-btn"
        aria-label="Notifications"
        on:click={() => { notifOpen = !notifOpen; profileOpen = false; }}
      >
        <Bell class="w-4 h-4" />
        {#if unreadCount > 0}
          <span class="notif-badge">{unreadCount > 9 ? '9+' : unreadCount}</span>
        {/if}
      </button>
      <NotificationsPanel
        open={notifOpen}
        on:close={() => notifOpen = false}
        on:unread={(e) => unreadCount = e.detail}
      />
    </div>

    <!-- Admin link — only shown to admin/super_admin -->
    {#if isAdmin}
      <button
        class="nav-icon-btn admin-glow"
        aria-label="Admin Panel"
        title="Admin Panel"
        on:click={() => goto('/admin')}
      >
        <LayoutDashboard class="w-4 h-4" />
      </button>
    {/if}

    <!-- Settings -->
    <button
      class="nav-icon-btn"
      aria-label="Settings"
      on:click={() => goto('/dashboard/settings')}
    >
      <Settings class="w-4 h-4" />
    </button>

    <div class="w-px h-5 bg-white/10"></div>

    <!-- Profile dropdown -->
    <div class="relative">
      <button
        class="flex items-center gap-2.5 px-3 py-1.5 rounded-xl border border-white/10 bg-white/[0.04] hover:bg-white/[0.07] hover:border-white/20 transition-all duration-200"
        on:click={() => { profileOpen = !profileOpen; notifOpen = false; }}
      >
        <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-neon-cyan to-neon-blue flex items-center justify-center text-[11px] font-bold text-dark-bg">
          {initials}
        </div>
        <span class="text-sm font-medium text-on-surface hidden sm:block max-w-[120px] truncate">{displayName}</span>
        <ChevronDown class="w-3.5 h-3.5 text-on-surface-variant transition-transform duration-200 {profileOpen ? 'rotate-180' : ''}" />
      </button>

      {#if profileOpen}
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <!-- svelte-ignore a11y-no-static-element-interactions -->
        <div class="profile-dropdown" on:click|stopPropagation>
          <div class="px-4 py-3 border-b border-white/[0.06]">
            <p class="text-sm font-semibold text-white truncate">{displayName}</p>
            <p class="text-xs text-on-surface-variant/60 truncate mt-0.5">{user.email}</p>
          </div>
          <div class="py-1.5">
            <button class="dropdown-item" on:click={() => { profileOpen = false; goto('/dashboard/profile'); }}>
              <User class="w-3.5 h-3.5" /> Profile
            </button>
            <button class="dropdown-item" on:click={() => { profileOpen = false; goto('/dashboard/settings'); }}>
              <Settings class="w-3.5 h-3.5" /> Settings
            </button>
          </div>
          <div class="py-1.5 border-t border-white/[0.06]">
            <button class="dropdown-item text-red-400 hover:bg-red-500/10" on:click={handleSignOut}>
              <LogOut class="w-3.5 h-3.5" /> Sign out
            </button>
          </div>
        </div>

        <!-- Backdrop -->
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <!-- svelte-ignore a11y-no-static-element-interactions -->
        <div class="fixed inset-0 z-[-1]" on:click={() => profileOpen = false}></div>
      {/if}
    </div>
  </div>
</nav>

<!-- ── Main content ───────────────────────────────────────── -->
<main class="flex-1 px-5 sm:px-8 lg:px-12 py-8 max-w-7xl mx-auto w-full">

  {#if loading}
    <div class="flex items-center justify-center min-h-[60vh]">
      <div class="flex flex-col items-center gap-4">
        <div class="w-10 h-10 border-2 border-neon-cyan/20 border-t-neon-cyan rounded-full animate-spin"></div>
        <p class="text-sm text-on-surface-variant/60">Loading your dashboard...</p>
      </div>
    </div>

  {:else if error}
    <div class="mt-8 p-5 rounded-xl border border-red-500/20 bg-red-500/5 flex items-start gap-3">
      <AlertTriangle class="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
      <div>
        <p class="text-sm font-semibold text-red-400">Failed to load data</p>
        <p class="text-xs text-on-surface-variant mt-1">{error}</p>
        <button on:click={loadData} class="mt-3 text-xs text-neon-cyan hover:underline">Retry</button>
      </div>
    </div>

  {:else}
    <!-- Page header -->
    <div class="mb-8">
      <div class="flex items-center gap-2 mb-1">
        <span class="text-xs font-semibold uppercase tracking-[0.18em] text-on-surface-variant/50">Dashboard</span>
      </div>
      <h1 class="text-2xl sm:text-3xl font-headline font-bold text-white">
        Good {new Date().getHours() < 12 ? 'morning' : new Date().getHours() < 18 ? 'afternoon' : 'evening'},
        <span class="bg-gradient-to-r from-neon-cyan to-neon-blue bg-clip-text text-transparent">{displayName}</span>
      </h1>
      <p class="text-sm text-on-surface-variant/60 mt-1">Here's your security overview for today.</p>
    </div>

    <!-- ── Stats row ── -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {#each stats as s, i}
        <div class="stat-card" style="animation-delay:{i*80}ms; --bg:{s.bg}; --border:{s.border}; --glow:{s.glow}">
          <div class="flex items-start justify-between mb-3">
            <span class="text-xs font-semibold uppercase tracking-wider text-on-surface-variant/60">{s.label}</span>
            <div class="stat-icon-wrap" style="background:{s.bg}; border-color:{s.border}">
              <svelte:component this={s.icon} class="w-3.5 h-3.5" style="color:{s.border.replace('0.15','1')}" />
            </div>
          </div>
          <div class="text-3xl font-headline font-bold bg-gradient-to-r {s.gradient} bg-clip-text text-transparent">
            {animatedCounts[s.key]}
          </div>
          <div class="mt-2 flex items-center gap-1 text-[11px] text-on-surface-variant/40">
            <TrendingUp class="w-3 h-3" />
            <span>All time</span>
          </div>
        </div>
      {/each}
    </div>

    <!-- ── Two-column layout ── -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">

      <!-- Left: repos (2/3 width) -->
      <div class="xl:col-span-2 space-y-6">
        <RepoList {repositories} userId={user.id} bind:addRepoTrigger on:refresh={loadData} />
      </div>

      <!-- Right: sidebar (1/3 width) -->
      <div class="space-y-5">

        <!-- Quick actions -->
        <div class="dash-card">
          <h3 class="section-title mb-4">Quick Actions</h3>
          <div class="space-y-2">
            {#each quickActions as qa}
              <button
                class="quick-action-btn quick-action-{qa.color}"
                on:click={qa.action}
              >
                <svelte:component this={qa.icon} class="w-4 h-4" />
                {qa.label}
              </button>
            {/each}
          </div>
        </div>

        <!-- Recent activity -->
        <div class="dash-card">
          <h3 class="section-title mb-4">Recent Activity</h3>
          {#if recentActivity.length === 0}
            <div class="text-center py-6">
              <Clock class="w-8 h-8 text-on-surface-variant/20 mx-auto mb-2" />
              <p class="text-xs text-on-surface-variant/40">No scans yet</p>
            </div>
          {:else}
            <div class="space-y-3">
              {#each recentActivity as a}
                {@const sc = statusColor(a.status)}
                <div class="activity-item">
                  <div class="activity-dot" style="background:{sc.dot}; box-shadow: 0 0 6px {sc.dot}"></div>
                  <div class="flex-1 min-w-0">
                    <p class="text-xs font-medium text-on-surface truncate">{a.repo}</p>
                    <div class="flex items-center gap-2 mt-0.5">
                      <span class="text-[10px] {sc.text}">{sc.label}</span>
                      {#if a.vulns > 0}
                        <span class="text-[10px] text-on-surface-variant/40">· {a.vulns} vulns</span>
                      {/if}
                    </div>
                  </div>
                  <span class="text-[10px] text-on-surface-variant/30 flex-shrink-0">{timeAgo(a.time)}</span>
                </div>
              {/each}
            </div>
          {/if}
        </div>

      </div>
    </div>
  {/if}
</main>

<!-- ── Footer ─────────────────────────────────────────────── -->
<footer class="px-5 sm:px-8 lg:px-12 py-5 border-t border-white/[0.04] mt-auto">
  <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] text-on-surface-variant/40">
    <div class="flex items-center gap-2">
      <span class="relative flex h-1.5 w-1.5">
        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
        <span class="relative inline-flex rounded-full h-1.5 w-1.5 bg-green-400"></span>
      </span>
      All systems operational
    </div>
    <div class="flex items-center gap-4">
      <a href="/dashboard/privacy" class="hover:text-white/60 transition-colors">Privacy</a>
      <a href="/dashboard/terms"   class="hover:text-white/60 transition-colors">Terms</a>
      <span>SecureShift v1.0</span>
    </div>
  </div>
</footer>

<style>
  /* Nav */
  .dash-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.25rem 1rem 1.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    background: rgba(6,9,20,0.6);
    backdrop-filter: blur(20px);
    position: sticky;
    top: 0;
    z-index: 50;
  }

  .nav-icon-btn {
    position: relative;
    width: 2.25rem; height: 2.25rem;
    display: flex; align-items: center; justify-content: center;
    border-radius: 0.625rem;
    border: 1px solid rgba(255,255,255,0.07);
    background: rgba(255,255,255,0.03);
    color: rgba(184,191,214,0.6);
    transition: all 0.2s;
    cursor: pointer;
  }
  .nav-icon-btn:hover {
    background: rgba(255,255,255,0.07);
    border-color: rgba(255,255,255,0.12);
    color: white;
  }

  .admin-glow {
    border-color: rgba(157,78,221,0.3) !important;
    color: #9d4edd !important;
  }
  .admin-glow:hover {
    background: rgba(157,78,221,0.12) !important;
    border-color: rgba(157,78,221,0.5) !important;
    box-shadow: 0 0 12px rgba(157,78,221,0.25);
  }

  .notif-badge {
    position: absolute; top: -4px; right: -4px;
    min-width: 1.1rem; height: 1.1rem; padding: 0 0.2rem;
    border-radius: 9999px; font-size: 0.6rem; font-weight: 700;
    background: #00d9ff; color: #060914;
    display: flex; align-items: center; justify-content: center;
    border: 1.5px solid #060914;
  }

  /* Profile dropdown */
  .profile-dropdown {
    position: absolute;
    top: calc(100% + 0.5rem);
    right: 0;
    width: 200px;
    border-radius: 0.875rem;
    border: 1px solid rgba(255,255,255,0.08);
    background: rgba(10,13,28,0.95);
    backdrop-filter: blur(20px);
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    z-index: 100;
    overflow: hidden;
    animation: dropIn 0.15s ease;
  }

  .dropdown-item {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 0.625rem;
    padding: 0.5rem 1rem;
    font-size: 0.8125rem;
    color: rgba(184,191,214,0.8);
    background: none;
    border: none;
    cursor: pointer;
    transition: background 0.15s, color 0.15s;
    text-align: left;
  }
  .dropdown-item:hover {
    background: rgba(255,255,255,0.05);
    color: white;
  }

  /* Stat cards */
  .stat-card {
    padding: 1.125rem;
    border-radius: 1rem;
    border: 1px solid var(--border);
    background: var(--bg);
    backdrop-filter: blur(12px);
    animation: fadeUp 0.4s ease both;
    transition: box-shadow 0.3s, border-color 0.3s;
  }
  .stat-card:hover {
    box-shadow: 0 0 30px var(--glow);
    border-color: var(--border);
  }

  .stat-icon-wrap {
    width: 1.875rem; height: 1.875rem;
    border-radius: 0.5rem;
    border: 1px solid;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }

  /* Generic dash card */
  .dash-card {
    padding: 1.25rem;
    border-radius: 1rem;
    border: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.02);
    backdrop-filter: blur(12px);
  }

  .section-title {
    font-size: 0.8125rem;
    font-weight: 600;
    color: rgba(184,191,214,0.7);
    letter-spacing: 0.04em;
  }

  /* Quick actions */
  .quick-action-btn {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 0.625rem;
    padding: 0.625rem 0.875rem;
    border-radius: 0.625rem;
    font-size: 0.8125rem;
    font-weight: 500;
    border: 1px solid transparent;
    cursor: pointer;
    transition: all 0.2s;
    text-align: left;
  }
  .quick-action-cyan {
    background: rgba(0,217,255,0.07);
    border-color: rgba(0,217,255,0.15);
    color: #00d9ff;
  }
  .quick-action-cyan:hover {
    background: rgba(0,217,255,0.12);
    border-color: rgba(0,217,255,0.3);
  }
  .quick-action-purple {
    background: rgba(157,78,221,0.07);
    border-color: rgba(157,78,221,0.15);
    color: #9d4edd;
  }
  .quick-action-purple:hover {
    background: rgba(157,78,221,0.12);
    border-color: rgba(157,78,221,0.3);
  }
  .quick-action-pink {
    background: rgba(247,37,133,0.07);
    border-color: rgba(247,37,133,0.15);
    color: #ff006e;
  }
  .quick-action-pink:hover {
    background: rgba(247,37,133,0.12);
    border-color: rgba(247,37,133,0.3);
  }

  /* Activity timeline */
  .activity-item {
    display: flex;
    align-items: flex-start;
    gap: 0.625rem;
  }
  .activity-dot {
    width: 0.5rem; height: 0.5rem;
    border-radius: 50%;
    flex-shrink: 0;
    margin-top: 0.25rem;
  }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes dropIn {
    from { opacity: 0; transform: translateY(-6px); }
    to   { opacity: 1; transform: translateY(0); }
  }
</style>
