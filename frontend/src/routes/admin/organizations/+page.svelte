<script lang="ts">
  import { onMount } from 'svelte';
  import { adminGet } from '$lib/adminApi';
  import { RefreshCw, Building2 } from 'lucide-svelte';

  let orgs: any[] = [];
  let loading = true;
  let error = '';

  async function load() {
    loading = true; error = '';
    try {
      const res: any = await adminGet('/organizations');
      orgs = res.organizations ?? res.items ?? res ?? [];
    } catch (e: any) { error = e.message; }
    finally { loading = false; }
  }

  onMount(load);

  const PLAN_STYLES: Record<string, { color: string; bg: string; border: string }> = {
    free:       { color: '#94a3b8', bg: 'rgba(148,163,184,0.1)',  border: 'rgba(148,163,184,0.2)'  },
    pro:        { color: '#00d9ff', bg: 'rgba(0,217,255,0.1)',    border: 'rgba(0,217,255,0.25)'   },
    enterprise: { color: '#9d4edd', bg: 'rgba(157,78,221,0.1)',   border: 'rgba(157,78,221,0.25)'  },
  };

  function planStyle(plan: string) {
    return PLAN_STYLES[plan?.toLowerCase()] ?? PLAN_STYLES['free'];
  }
</script>

<svelte:head><title>Organizations — Admin</title></svelte:head>

<div class="space-y-5">
  <div class="flex flex-wrap items-center justify-between gap-3">
    <div>
      <h1 class="text-xl font-bold text-white">Organizations</h1>
      <p class="text-xs text-muted mt-0.5">{orgs.length} total organizations</p>
    </div>
    <button class="admin-btn-ghost" on:click={load}><RefreshCw class="w-3.5 h-3.5" /> Refresh</button>
  </div>

  {#if error}<div class="admin-error">{error}</div>{/if}

  <div class="admin-table-wrap">
    <table class="admin-table">
      <thead>
        <tr>
          <th>Organization</th>
          <th>Plan</th>
          <th>Owner</th>
          <th>Created</th>
        </tr>
      </thead>
      <tbody>
        {#if loading}
          {#each Array(6) as _}
            <tr><td colspan="4"><div class="skeleton-row"></div></td></tr>
          {/each}
        {:else if orgs.length === 0}
          <tr>
            <td colspan="4" class="empty-state">
              <Building2 class="w-10 h-10 mx-auto mb-3 opacity-20" />
              <p class="font-medium">No organizations yet</p>
              <p class="text-xs mt-1 opacity-60">Organizations will appear here once created.</p>
            </td>
          </tr>
        {:else}
          {#each orgs as org}
            {@const ps = planStyle(org.plan)}
            <tr class="table-row">
              <td>
                <div class="flex items-center gap-2.5">
                  <div class="org-avatar">
                    {(org.name || 'O').slice(0, 2).toUpperCase()}
                  </div>
                  <span class="text-xs font-medium text-white">{org.name ?? '—'}</span>
                </div>
              </td>
              <td>
                <span class="plan-badge" style="color:{ps.color}; background:{ps.bg}; border-color:{ps.border}">
                  {org.plan ?? 'free'}
                </span>
              </td>
              <td class="text-xs text-muted">{org.owner_email ?? org.owner ?? '—'}</td>
              <td class="text-xs text-muted">
                {org.created_at ? new Date(org.created_at).toLocaleDateString() : '—'}
              </td>
            </tr>
          {/each}
        {/if}
      </tbody>
    </table>
  </div>
</div>

<style>
  .text-muted { color: rgba(184,191,214,0.5); }

  .admin-table-wrap { border-radius: 0.875rem; border: 1px solid rgba(255,255,255,0.06); overflow: hidden; }
  .admin-table { width: 100%; border-collapse: collapse; }
  .admin-table thead tr { background: rgba(255,255,255,0.02); }
  .admin-table th {
    padding: 0.625rem 0.875rem; text-align: left;
    font-size: 0.65rem; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: rgba(184,191,214,0.4);
    border-bottom: 1px solid rgba(255,255,255,0.05);
  }
  .table-row { border-bottom: 1px solid rgba(255,255,255,0.04); transition: background 0.15s; }
  .table-row:last-child { border-bottom: none; }
  .table-row:hover { background: rgba(255,255,255,0.02); }
  .admin-table td { padding: 0.75rem 0.875rem; }

  .org-avatar {
    width: 2rem; height: 2rem; border-radius: 0.5rem;
    background: linear-gradient(135deg, #9d4edd, #3a86ff);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.65rem; font-weight: 700; color: white; flex-shrink: 0;
  }

  .plan-badge {
    display: inline-flex; padding: 0.15rem 0.5rem; border-radius: 0.25rem;
    font-size: 0.65rem; font-weight: 600; text-transform: capitalize;
    border: 1px solid;
  }

  .empty-state {
    text-align: center; padding: 4rem 1rem;
    color: rgba(184,191,214,0.5); font-size: 0.875rem;
  }

  .skeleton-row {
    height: 2.5rem; border-radius: 0.375rem;
    background: linear-gradient(90deg, rgba(255,255,255,0.04) 25%, rgba(255,255,255,0.07) 50%, rgba(255,255,255,0.04) 75%);
    animation: shimmer 1.5s infinite; background-size: 200% 100%;
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

  @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
</style>
