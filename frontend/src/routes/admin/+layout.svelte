<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { supabase } from '$lib/supabaseClient';
  import { adminGet } from '$lib/adminApi';
  import {
    Shield, LayoutDashboard, Users, Building2, GitBranch,
    ScanLine, AlertTriangle, GitPullRequest, Bell, BarChart2,
    FileText, ScrollText, CreditCard, Settings2, LogOut,
    ChevronRight, Menu, X
  } from 'lucide-svelte';

  let user: any = null;
  let loading = true;
  let sidebarOpen = false;

  const NAV = [
    { href: '/admin',                    icon: LayoutDashboard, label: 'Overview'       },
    { href: '/admin/users',              icon: Users,           label: 'Users'          },
    { href: '/admin/organizations',      icon: Building2,       label: 'Organizations'  },
    { href: '/admin/repositories',       icon: GitBranch,       label: 'Repositories'   },
    { href: '/admin/scans',              icon: ScanLine,        label: 'Scans'          },
    { href: '/admin/vulnerabilities',    icon: AlertTriangle,   label: 'Vulnerabilities'},
    { href: '/admin/pull-requests',      icon: GitPullRequest,  label: 'Pull Requests'  },
    { href: '/admin/notifications',      icon: Bell,            label: 'Notifications'  },
    { href: '/admin/analytics',          icon: BarChart2,       label: 'Analytics'      },
    { href: '/admin/reports',            icon: FileText,        label: 'Reports'        },
    { href: '/admin/audit-logs',         icon: ScrollText,      label: 'Audit Logs'     },
    { href: '/admin/billing',            icon: CreditCard,      label: 'Billing'        },
    { href: '/admin/system-settings',    icon: Settings2,       label: 'System'         },
  ];

  onMount(async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      console.log('[admin layout] session:', session?.user?.id);
      
      if (!session) {
        console.log('[admin layout] no session, redirecting to /');
        goto('/');
        return;
      }

      // Try hitting an admin endpoint — 403 means not an admin
      try {
        console.log('[admin layout] checking admin access...');
        await adminGet('/overview');
        console.log('[admin layout] admin access confirmed');
      } catch (e: any) {
        console.error('[admin layout] admin check failed:', e.message);
        if (e.message?.includes('403') || e.message?.includes('Admin') || e.message?.includes('required')) {
          console.log('[admin layout] not an admin, redirecting to /dashboard');
          goto('/dashboard');
          return;
        }
        // Other errors (network etc.) — still let them in, page will show its own error
        console.warn('[admin layout] non-403 error, allowing access:', e.message);
      }

      user = session.user;
      loading = false;
    } catch (e: any) {
      console.error('[admin layout] unexpected error:', e);
      goto('/');
    }
  });

  async function signOut() {
    await supabase.auth.signOut();
    goto('/');
  }

  $: currentPath = $page?.url?.pathname ?? '';
</script>

{#if loading}
  <div class="min-h-screen bg-[#060914] flex items-center justify-center">
    <div class="w-8 h-8 border-2 border-neon-cyan/20 border-t-neon-cyan rounded-full animate-spin"></div>
  </div>
{:else}
  <div class="admin-shell">

    <!-- Mobile overlay -->
    {#if sidebarOpen}
      <!-- svelte-ignore a11y-click-events-have-key-events -->
      <!-- svelte-ignore a11y-no-static-element-interactions -->
      <div class="fixed inset-0 z-40 bg-black/60 lg:hidden" on:click={() => sidebarOpen = false}></div>
    {/if}

    <!-- Sidebar -->
    <aside class="admin-sidebar {sidebarOpen ? 'sidebar-open' : ''}">
      <!-- Brand -->
      <div class="sidebar-brand">
        <div class="brand-icon">
          <Shield class="w-4 h-4 text-neon-cyan" />
        </div>
        <div>
          <span class="brand-name">SecureShift</span>
          <span class="brand-tag">Admin</span>
        </div>
        <button class="ml-auto lg:hidden text-on-surface-variant/40 hover:text-white"
          on:click={() => sidebarOpen = false}>
          <X class="w-4 h-4" />
        </button>
      </div>

      <!-- Nav -->
      <nav class="sidebar-nav">
        {#each NAV as item}
          <a
            href={item.href}
            class="nav-link {currentPath === item.href ? 'nav-link-active' : ''}"
            on:click={() => sidebarOpen = false}
          >
            <svelte:component this={item.icon} class="w-4 h-4 flex-shrink-0" />
            <span>{item.label}</span>
            {#if currentPath === item.href}
              <ChevronRight class="w-3 h-3 ml-auto opacity-60" />
            {/if}
          </a>
        {/each}
      </nav>

      <!-- User footer -->
      <div class="sidebar-footer">
        <div class="flex items-center gap-2.5 min-w-0">
          <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-neon-cyan to-neon-blue flex items-center justify-center text-[10px] font-bold text-dark-bg flex-shrink-0">
            {(user?.email || 'A').slice(0, 2).toUpperCase()}
          </div>
          <div class="min-w-0">
            <p class="text-xs font-medium text-white truncate">{user?.email}</p>
            <p class="text-[10px] text-neon-cyan/70">Admin</p>
          </div>
        </div>
        <button class="text-on-surface-variant/40 hover:text-red-400 transition-colors" on:click={signOut}>
          <LogOut class="w-4 h-4" />
        </button>
      </div>
    </aside>

    <!-- Main area -->
    <div class="admin-main">
      <!-- Top bar -->
      <header class="admin-topbar">
        <button class="lg:hidden nav-icon-btn" on:click={() => sidebarOpen = true}>
          <Menu class="w-4 h-4" />
        </button>
        <div class="flex items-center gap-2 text-xs text-on-surface-variant/50">
          <a href="/dashboard" class="hover:text-neon-cyan transition-colors">Dashboard</a>
          <span>/</span>
          <span class="text-white capitalize">{currentPath.split('/').pop() || 'Overview'}</span>
        </div>
        <div class="ml-auto flex items-center gap-2">
          <span class="status-dot"></span>
          <span class="text-[11px] text-on-surface-variant/50">Live</span>
        </div>
      </header>

      <!-- Page content -->
      <div class="admin-content">
        <slot />
      </div>
    </div>
  </div>
{/if}

<style>
  .admin-shell {
    display: flex; min-height: 100vh;
    background: #060914;
    color: #f0f4ff;
  }

  /* Sidebar */
  .admin-sidebar {
    width: 220px; flex-shrink: 0;
    display: flex; flex-direction: column;
    border-right: 1px solid rgba(255,255,255,0.05);
    background: rgba(6,9,20,0.95);
    backdrop-filter: blur(20px);
    position: fixed; top: 0; left: 0; bottom: 0; z-index: 50;
    transform: translateX(-100%);
    transition: transform 0.25s ease;
  }
  @media (min-width: 1024px) {
    .admin-sidebar { transform: translateX(0); position: sticky; height: 100vh; }
  }
  .sidebar-open { transform: translateX(0) !important; }

  .sidebar-brand {
    display: flex; align-items: center; gap: 0.625rem;
    padding: 1.125rem 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    flex-shrink: 0;
  }
  .brand-icon {
    width: 2rem; height: 2rem; border-radius: 0.5rem;
    background: rgba(0,217,255,0.1); border: 1px solid rgba(0,217,255,0.2);
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  }
  .brand-name { display: block; font-size: 0.875rem; font-weight: 700; color: white; line-height: 1; }
  .brand-tag  { display: block; font-size: 0.6rem; font-weight: 600; color: #00d9ff; letter-spacing: 0.1em; text-transform: uppercase; margin-top: 1px; }

  .sidebar-nav {
    flex: 1; overflow-y: auto; padding: 0.75rem 0.5rem;
    display: flex; flex-direction: column; gap: 1px;
    scrollbar-width: none;
  }
  .sidebar-nav::-webkit-scrollbar { display: none; }

  .nav-link {
    display: flex; align-items: center; gap: 0.625rem;
    padding: 0.5rem 0.625rem; border-radius: 0.5rem;
    font-size: 0.8125rem; font-weight: 500;
    color: rgba(184,191,214,0.65);
    text-decoration: none; transition: all 0.15s;
  }
  .nav-link:hover { background: rgba(255,255,255,0.05); color: white; }
  .nav-link-active { background: rgba(0,217,255,0.1); color: #00d9ff; }

  .sidebar-footer {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.875rem 1rem;
    border-top: 1px solid rgba(255,255,255,0.05);
    flex-shrink: 0;
  }

  /* Main */
  .admin-main {
    flex: 1; display: flex; flex-direction: column;
    min-width: 0;
    margin-left: 0;
  }
  @media (min-width: 1024px) {
    .admin-main { margin-left: 220px; }
  }

  .admin-topbar {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.75rem 1.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    background: rgba(6,9,20,0.7);
    backdrop-filter: blur(20px);
    position: sticky; top: 0; z-index: 30;
    flex-shrink: 0;
  }

  .nav-icon-btn {
    width: 2rem; height: 2rem;
    display: flex; align-items: center; justify-content: center;
    border-radius: 0.5rem; border: 1px solid rgba(255,255,255,0.07);
    background: rgba(255,255,255,0.03); color: rgba(184,191,214,0.6);
    cursor: pointer; transition: all 0.15s;
  }
  .nav-icon-btn:hover { background: rgba(255,255,255,0.07); color: white; }

  .status-dot {
    width: 0.5rem; height: 0.5rem; border-radius: 50%;
    background: #34d399;
    box-shadow: 0 0 6px #34d399;
    animation: pulse 2s infinite;
  }

  .admin-content {
    flex: 1; padding: 1.5rem;
    overflow-y: auto;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.5; }
  }
</style>
