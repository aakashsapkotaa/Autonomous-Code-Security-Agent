<script lang="ts">
  import { onMount } from 'svelte';
  import { adminGet, adminPost } from '$lib/adminApi';
  import { RefreshCw, Bell, Info, CheckCircle, XCircle, AlertTriangle, BellOff } from 'lucide-svelte';

  let notifications: any[] = [];
  let loading = true;
  let error = '';
  let marking = false;
  let toast = '';

  async function load() {
    loading = true; error = '';
    try {
      const res: any = await adminGet('/notifications');
      notifications = res.notifications ?? res ?? [];
    } catch (e: any) { error = e.message; }
    finally { loading = false; }
  }

  onMount(load);

  async function markAllRead() {
    marking = true;
    try {
      await adminPost('/notifications/read');
      toast = 'All notifications marked as read';
      await load();
      setTimeout(() => toast = '', 2500);
    } catch (e: any) { error = e.message; }
    finally { marking = false; }
  }

  $: unreadCount = notifications.filter(n => !n.read && !n.is_read).length;

  const TYPE_CONFIG: Record<string, { icon: any; color: string; bg: string }> = {
    info:    { icon: Info,          color: '#3a86ff', bg: 'rgba(58,134,255,0.1)'  },
    success: { icon: CheckCircle,   color: '#34d399', bg: 'rgba(52,211,153,0.1)'  },
    error:   { icon: XCircle,       color: '#f87171', bg: 'rgba(248,113,113,0.1)' },
    warning: { icon: AlertTriangle, color: '#fbbf24', bg: 'rgba(251,191,36,0.1)'  },
  };

  function getConfig(type: string) {
    return TYPE_CONFIG[type] ?? TYPE_CONFIG['info'];
  }

  function timeAgo(dateStr: string) {
    if (!dateStr) return '—';
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return `${Math.floor(hrs / 24)}d ago`;
  }
</script>

<svelte:head><title>Notifications — Admin</title></svelte:head>

<div class="space-y-5">
  <div class="flex flex-wrap items-center justify-between gap-3">
    <div class="flex items-center gap-3">
      <div>
        <h1 class="text-xl font-bold text-white">Notifications</h1>
        <p class="text-xs text-muted mt-0.5">{notifications.length} total</p>
      </div>
      {#if unreadCount > 0}
        <span class="unread-badge">{unreadCount} unread</span>
      {/if}
    </div>
    <div class="flex gap-2">
      <button class="admin-btn-ghost" on:click={load}><RefreshCw class="w-3.5 h-3.5" /> Refresh</button>
      {#if unreadCount > 0}
        <button class="mark-read-btn" disabled={marking} on:click={markAllRead}>
          <BellOff class="w-3.5 h-3.5" />
          {marking ? 'Marking…' : 'Mark all read'}
        </button>
      {/if}
    </div>
  </div>

  {#if error}<div class="admin-error">{error}</div>{/if}
  {#if toast}<div class="admin-toast">{toast}</div>{/if}

  <div class="notif-list">
    {#if loading}
      {#each Array(6) as _}
        <div class="skeleton-notif"></div>
      {/each}
    {:else if notifications.length === 0}
      <div class="empty-state">
        <Bell class="w-10 h-10 mx-auto mb-3 opacity-20" />
        <p class="font-medium">No notifications</p>
        <p class="text-xs mt-1 opacity-60">System notifications will appear here.</p>
      </div>
    {:else}
      {#each notifications as notif}
        {@const cfg = getConfig(notif.type ?? 'info')}
        {@const isUnread = !notif.read && !notif.is_read}
        <div class="notif-item {isUnread ? 'notif-unread' : ''}">
          <div class="notif-icon" style="background:{cfg.bg}; color:{cfg.color}; border-color:{cfg.color}33">
            <svelte:component this={cfg.icon} class="w-4 h-4" />
          </div>
          <div class="notif-body">
            <div class="flex items-start justify-between gap-2">
              <p class="text-xs font-medium text-white leading-snug">{notif.title ?? notif.message ?? 'Notification'}</p>
              <span class="notif-time">{timeAgo(notif.created_at)}</span>
            </div>
            {#if notif.message && notif.title}
              <p class="text-xs text-muted mt-0.5 leading-relaxed">{notif.message}</p>
            {/if}
            <div class="flex items-center gap-2 mt-1.5">
              <span class="type-pill" style="color:{cfg.color}; background:{cfg.bg}; border-color:{cfg.color}33">
                {notif.type ?? 'info'}
              </span>
              {#if isUnread}
                <span class="unread-dot"></span>
              {/if}
            </div>
          </div>
        </div>
      {/each}
    {/if}
  </div>
</div>

<style>
  .text-muted { color: rgba(184,191,214,0.5); }

  .unread-badge {
    display: inline-flex; align-items: center;
    padding: 0.2rem 0.6rem; border-radius: 9999px;
    font-size: 0.65rem; font-weight: 700;
    background: rgba(0,217,255,0.12); color: #00d9ff;
    border: 1px solid rgba(0,217,255,0.25);
  }

  .mark-read-btn {
    display: inline-flex; align-items: center; gap: 0.375rem;
    padding: 0.375rem 0.75rem; border-radius: 0.5rem;
    font-size: 0.75rem; font-weight: 500; color: #00d9ff;
    background: rgba(0,217,255,0.08); border: 1px solid rgba(0,217,255,0.2);
    cursor: pointer; transition: all 0.15s;
  }
  .mark-read-btn:hover:not(:disabled) { background: rgba(0,217,255,0.15); }
  .mark-read-btn:disabled { opacity: 0.4; cursor: not-allowed; }

  .notif-list { display: flex; flex-direction: column; gap: 0.5rem; }

  .notif-item {
    display: flex; align-items: flex-start; gap: 0.875rem;
    padding: 0.875rem 1rem; border-radius: 0.75rem;
    border: 1px solid rgba(255,255,255,0.05);
    background: rgba(255,255,255,0.02);
    transition: background 0.15s;
  }
  .notif-item:hover { background: rgba(255,255,255,0.04); }
  .notif-unread { border-color: rgba(0,217,255,0.1); background: rgba(0,217,255,0.03); }

  .notif-icon {
    width: 2.25rem; height: 2.25rem; border-radius: 0.5rem;
    display: flex; align-items: center; justify-content: center;
    border: 1px solid; flex-shrink: 0;
  }

  .notif-body { flex: 1; min-width: 0; }

  .notif-time { font-size: 0.65rem; color: rgba(184,191,214,0.35); white-space: nowrap; flex-shrink: 0; }

  .type-pill {
    display: inline-flex; padding: 0.1rem 0.4rem; border-radius: 0.25rem;
    font-size: 0.6rem; font-weight: 600; letter-spacing: 0.05em;
    text-transform: uppercase; border: 1px solid;
  }

  .unread-dot {
    width: 0.4rem; height: 0.4rem; border-radius: 50%;
    background: #00d9ff; box-shadow: 0 0 4px #00d9ff;
  }

  .skeleton-notif {
    height: 4.5rem; border-radius: 0.75rem;
    background: linear-gradient(90deg, rgba(255,255,255,0.04) 25%, rgba(255,255,255,0.07) 50%, rgba(255,255,255,0.04) 75%);
    animation: shimmer 1.5s infinite; background-size: 200% 100%;
  }

  .empty-state {
    text-align: center; padding: 4rem 1rem;
    color: rgba(184,191,214,0.5); font-size: 0.875rem;
  }

  .admin-btn-ghost {
    display: inline-flex; align-items: center; gap: 0.375rem;
    padding: 0.375rem 0.75rem; border-radius: 0.5rem;
    font-size: 0.75rem; font-weight: 500; color: rgba(184,191,214,0.6);
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);
    cursor: pointer; transition: all 0.15s;
  }
  .admin-btn-ghost:hover { background: rgba(255,255,255,0.08); color: white; }

  .admin-error { padding: 0.75rem 1rem; border-radius: 0.75rem; background: rgba(248,113,113,0.08); border: 1px solid rgba(248,113,113,0.2); color: #f87171; font-size: 0.875rem; }
  .admin-toast { padding: 0.75rem 1rem; border-radius: 0.75rem; background: rgba(52,211,153,0.08); border: 1px solid rgba(52,211,153,0.2); color: #34d399; font-size: 0.875rem; }

  @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
</style>
