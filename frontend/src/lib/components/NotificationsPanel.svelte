<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { Bell, CheckCheck, X, ShieldAlert, Zap, GitPullRequest, Search, Info } from 'lucide-svelte';
  import { apiGet, apiPost } from '$lib/api';

  export let open = false;

  const dispatch = createEventDispatcher();

  interface Notification {
    id: string; user_id: string; title: string;
    message: string; type: string; is_read: boolean; created_at: string;
  }

  let notifications: Notification[] = [];
  let unreadCount = 0;
  let loading = false;

  $: if (open) fetchNotifications();

  async function fetchNotifications() {
    loading = true;
    try {
      const res: any = await apiGet('/api/notifications');
      notifications = res.notifications;
      unreadCount = res.unread_count;
    } catch (e) { /* silent */ }
    finally { loading = false; }
  }

  async function markAllRead() {
    await apiPost('/api/notifications/read', {});
    notifications = notifications.map(n => ({ ...n, is_read: true }));
    unreadCount = 0;
    dispatch('unread', 0);
  }

  async function markRead(id: string) {
    await apiPost('/api/notifications/read', { notification_ids: [id] });
    notifications = notifications.map(n => n.id === id ? { ...n, is_read: true } : n);
    unreadCount = Math.max(0, unreadCount - 1);
    dispatch('unread', unreadCount);
  }

  function timeAgo(iso: string) {
    const diff = Date.now() - new Date(iso).getTime();
    const m = Math.floor(diff / 60000);
    if (m < 1) return 'just now';
    if (m < 60) return `${m}m ago`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}h ago`;
    return `${Math.floor(h / 24)}d ago`;
  }

  const TYPE_META: Record<string, { icon: any; color: string; bg: string }> = {
    success: { icon: CheckCheck,     color: '#34d399', bg: 'rgba(52,211,153,0.1)'  },
    error:   { icon: ShieldAlert,    color: '#f87171', bg: 'rgba(248,113,113,0.1)' },
    warning: { icon: ShieldAlert,    color: '#fbbf24', bg: 'rgba(251,191,36,0.1)'  },
    scan:    { icon: Search,         color: '#00d9ff', bg: 'rgba(0,217,255,0.1)'   },
    pr:      { icon: GitPullRequest, color: '#9d4edd', bg: 'rgba(157,78,221,0.1)'  },
    cve:     { icon: ShieldAlert,    color: '#fb923c', bg: 'rgba(251,146,60,0.1)'  },
    info:    { icon: Info,           color: '#3a86ff', bg: 'rgba(58,134,255,0.1)'  },
  };

  function meta(type: string) {
    return TYPE_META[type] ?? TYPE_META.info;
  }
</script>

{#if open}
  <!-- Backdrop -->
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div class="fixed inset-0 z-40" on:click={() => dispatch('close')}></div>

  <div class="notif-panel">
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-white/[0.06]">
      <div class="flex items-center gap-2">
        <Bell class="w-4 h-4 text-neon-cyan" />
        <span class="text-sm font-semibold text-white">Notifications</span>
        {#if unreadCount > 0}
          <span class="unread-badge">{unreadCount}</span>
        {/if}
      </div>
      <div class="flex items-center gap-2">
        {#if unreadCount > 0}
          <button class="text-[11px] text-neon-cyan hover:underline" on:click={markAllRead}>
            Mark all read
          </button>
        {/if}
        <button class="text-on-surface-variant/40 hover:text-white transition-colors" on:click={() => dispatch('close')}>
          <X class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- List -->
    <div class="overflow-y-auto max-h-[420px]">
      {#if loading}
        <div class="flex items-center justify-center py-10 text-xs text-on-surface-variant/40">
          Loading…
        </div>
      {:else if notifications.length === 0}
        <div class="flex flex-col items-center justify-center py-10 gap-2">
          <Bell class="w-8 h-8 text-on-surface-variant/20" />
          <p class="text-xs text-on-surface-variant/40">No notifications yet</p>
        </div>
      {:else}
        {#each notifications as n (n.id)}
          {@const m = meta(n.type)}
          <!-- svelte-ignore a11y-click-events-have-key-events -->
          <!-- svelte-ignore a11y-no-static-element-interactions -->
          <div
            class="notif-item {n.is_read ? 'opacity-60' : ''}"
            on:click={() => !n.is_read && markRead(n.id)}
          >
            <div class="notif-icon" style="background:{m.bg}; color:{m.color}">
              <svelte:component this={m.icon} class="w-3.5 h-3.5" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs font-semibold text-white truncate">{n.title}</p>
              <p class="text-[11px] text-on-surface-variant/60 mt-0.5 line-clamp-2">{n.message}</p>
              <p class="text-[10px] text-on-surface-variant/30 mt-1">{timeAgo(n.created_at)}</p>
            </div>
            {#if !n.is_read}
              <div class="w-1.5 h-1.5 rounded-full bg-neon-cyan flex-shrink-0 mt-1"></div>
            {/if}
          </div>
        {/each}
      {/if}
    </div>
  </div>
{/if}

<style>
  .notif-panel {
    position: absolute;
    top: calc(100% + 0.5rem);
    right: 0;
    width: 340px;
    border-radius: 1rem;
    border: 1px solid rgba(255,255,255,0.08);
    background: rgba(8,11,24,0.96);
    backdrop-filter: blur(24px);
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    z-index: 50;
    animation: dropIn 0.15s ease;
  }

  .unread-badge {
    display: inline-flex; align-items: center; justify-content: center;
    min-width: 1.25rem; height: 1.25rem; padding: 0 0.25rem;
    border-radius: 9999px; font-size: 0.65rem; font-weight: 700;
    background: rgba(0,217,255,0.15); color: #00d9ff;
  }

  .notif-item {
    display: flex; align-items: flex-start; gap: 0.75rem;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    cursor: pointer; transition: background 0.15s;
  }
  .notif-item:last-child { border-bottom: none; }
  .notif-item:hover { background: rgba(255,255,255,0.03); }

  .notif-icon {
    width: 2rem; height: 2rem; border-radius: 0.5rem;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  }

  @keyframes dropIn {
    from { opacity: 0; transform: translateY(-6px); }
    to   { opacity: 1; transform: translateY(0); }
  }
</style>
