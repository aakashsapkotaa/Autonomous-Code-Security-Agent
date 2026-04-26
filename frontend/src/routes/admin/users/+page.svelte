<script lang="ts">
  import { onMount } from 'svelte';
  import { adminGet, adminPut, adminDelete } from '$lib/adminApi';
  import { Search, RefreshCw, ChevronLeft, ChevronRight, Shield, UserX, UserCheck, Trash2, Edit3, X, Check, ChevronDown } from 'lucide-svelte';

  // ── Custom dropdown ──────────────────────────────────────────────
  let roleOpen = false;
  let statusOpen = false;
  let editRoleOpen = false;
  let editStatusOpen = false;

  const ROLE_OPTIONS   = [
    { value: '',                   label: 'All roles'         },
    { value: 'user',               label: 'User'              },
    { value: 'admin',              label: 'Admin'             },
    { value: 'super_admin',        label: 'Super Admin'       },
    { value: 'enterprise_manager', label: 'Enterprise'        },
  ];
  const STATUS_OPTIONS = [
    { value: '',            label: 'All status' },
    { value: 'active',      label: 'Active'     },
    { value: 'suspended',   label: 'Suspended'  },
  ];
  const EDIT_ROLE_OPTIONS = [
    { value: 'user',               label: 'User'              },
    { value: 'admin',              label: 'Admin'             },
    { value: 'super_admin',        label: 'Super Admin'       },
    { value: 'enterprise_manager', label: 'Enterprise Manager'},
  ];
  const EDIT_STATUS_OPTIONS = [
    { value: 'active',    label: 'Active'    },
    { value: 'suspended', label: 'Suspended' },
  ];

  function labelFor(opts: {value:string;label:string}[], val: string) {
    return opts.find(o => o.value === val)?.label ?? val;
  }

  function closeAll() { roleOpen = statusOpen = editRoleOpen = editStatusOpen = false; }

  let users: any[] = [];
  let total = 0;
  let loading = true;
  let error = '';
  let search = '';
  let roleFilter = '';
  let statusFilter = '';
  let page = 1;
  const limit = 20;

  let editUser: any = null;
  let editRole = '';
  let editStatus = '';
  let saving = false;
  let toast = '';

  async function load() {
    loading = true; error = '';
    try {
      const params = new URLSearchParams({ page: String(page), limit: String(limit) });
      if (search)       params.set('search', search);
      if (roleFilter)   params.set('role', roleFilter);
      if (statusFilter) params.set('status', statusFilter);
      const res: any = await adminGet(`/users?${params}`);
      users = res.users; total = res.total;
    } catch (e: any) { error = e.message; }
    finally { loading = false; }
  }

  onMount(() => {
    load();
    const handler = () => closeAll();
    window.addEventListener('click', handler);
    return () => window.removeEventListener('click', handler);
  });

  async function saveEdit() {
    if (!editUser) return;
    saving = true;
    try {
      await adminPut(`/users/${editUser.id}`, { role: editRole, status: editStatus });
      toast = 'User updated'; editUser = null;
      await load();
      setTimeout(() => toast = '', 2500);
    } catch (e: any) { error = e.message; }
    finally { saving = false; }
  }

  async function deleteUser(id: string) {
    if (!confirm('Delete this user permanently?')) return;
    try {
      await adminDelete(`/users/${id}`);
      toast = 'User deleted'; await load();
      setTimeout(() => toast = '', 2500);
    } catch (e: any) { error = e.message; }
  }

  function openEdit(u: any) { editUser = u; editRole = u.role; editStatus = u.status; }

  const ROLE_COLORS: Record<string, string> = {
    super_admin: '#f87171', admin: '#fbbf24',
    enterprise_manager: '#a78bfa', user: '#94a3b8',
  };
  const STATUS_COLORS: Record<string, string> = { active: '#34d399', suspended: '#f87171' };

  $: totalPages = Math.ceil(total / limit);
</script>

<svelte:head><title>Users — Admin</title></svelte:head>

<div class="space-y-5">
  <div class="flex flex-wrap items-center justify-between gap-3">
    <div>
      <h1 class="text-xl font-headline font-bold text-white">Users</h1>
      <p class="text-xs text-on-surface-variant/50 mt-0.5">{total} total users</p>
    </div>
    <button class="admin-btn-ghost" on:click={load}><RefreshCw class="w-3.5 h-3.5" /> Refresh</button>
  </div>

  <!-- Filters -->
  <div class="flex flex-wrap gap-3">
    <div class="search-wrap">
      <Search class="w-3.5 h-3.5 text-on-surface-variant/40" />
      <input bind:value={search} on:input={() => { page=1; load(); }}
        placeholder="Search email or name…" class="search-input" />
    </div>

    <!-- Role filter -->
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div class="dropdown-wrap" on:click|stopPropagation={() => { roleOpen = !roleOpen; statusOpen = false; }}>
      <span class="dropdown-label">{labelFor(ROLE_OPTIONS, roleFilter)}</span>
      <ChevronDown class="w-3 h-3 opacity-50 transition-transform {roleOpen ? 'rotate-180' : ''}" />
      {#if roleOpen}
        <div class="dropdown-menu">
          {#each ROLE_OPTIONS as opt}
            <button class="dropdown-item {roleFilter === opt.value ? 'dropdown-item-active' : ''}"
              on:click|stopPropagation={() => { roleFilter = opt.value; roleOpen = false; page=1; load(); }}>
              {opt.label}
            </button>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Status filter -->
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div class="dropdown-wrap" on:click|stopPropagation={() => { statusOpen = !statusOpen; roleOpen = false; }}>
      <span class="dropdown-label">{labelFor(STATUS_OPTIONS, statusFilter)}</span>
      <ChevronDown class="w-3 h-3 opacity-50 transition-transform {statusOpen ? 'rotate-180' : ''}" />
      {#if statusOpen}
        <div class="dropdown-menu">
          {#each STATUS_OPTIONS as opt}
            <button class="dropdown-item {statusFilter === opt.value ? 'dropdown-item-active' : ''}"
              on:click|stopPropagation={() => { statusFilter = opt.value; statusOpen = false; page=1; load(); }}>
              {opt.label}
            </button>
          {/each}
        </div>
      {/if}
    </div>
  </div>

  {#if error}<div class="admin-error">{error}</div>{/if}
  {#if toast}<div class="admin-toast">{toast}</div>{/if}

  <!-- Table -->
  <div class="admin-table-wrap">
    <table class="admin-table">
      <thead>
        <tr>
          <th>User</th>
          <th>Role</th>
          <th>Status</th>
          <th>Repos</th>
          <th>Scans</th>
          <th>Joined</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {#if loading}
          {#each Array(8) as _}
            <tr><td colspan="7"><div class="skeleton-row"></div></td></tr>
          {/each}
        {:else}
          {#each users as u}
            <tr class="table-row">
              <td>
                <div class="flex items-center gap-2.5">
                  <div class="avatar">{(u.email||'?').slice(0,2).toUpperCase()}</div>
                  <div>
                    <p class="text-xs font-medium text-white">{u.name || '—'}</p>
                    <p class="text-[11px] text-on-surface-variant/50">{u.email}</p>
                  </div>
                </div>
              </td>
              <td>
                <span class="role-badge" style="color:{ROLE_COLORS[u.role]||'#94a3b8'}; background:{ROLE_COLORS[u.role]||'#94a3b8'}18; border-color:{ROLE_COLORS[u.role]||'#94a3b8'}33">
                  {u.role}
                </span>
              </td>
              <td>
                <span class="status-dot-inline" style="background:{STATUS_COLORS[u.status]||'#94a3b8'}"></span>
                <span class="text-xs capitalize" style="color:{STATUS_COLORS[u.status]||'#94a3b8'}">{u.status}</span>
              </td>
              <td class="text-xs text-on-surface-variant/60">{u.repo_count ?? 0}</td>
              <td class="text-xs text-on-surface-variant/60">{u.scan_count ?? 0}</td>
              <td class="text-xs text-on-surface-variant/50">{u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}</td>
              <td>
                <div class="flex items-center gap-1.5">
                  <button class="action-btn" title="Edit" on:click={() => openEdit(u)}><Edit3 class="w-3.5 h-3.5" /></button>
                  <button class="action-btn action-danger" title="Delete" on:click={() => deleteUser(u.id)}><Trash2 class="w-3.5 h-3.5" /></button>
                </div>
              </td>
            </tr>
          {:else}
            <tr><td colspan="7" class="text-center text-xs text-on-surface-variant/40 py-8">No users found</td></tr>
          {/each}
        {/if}
      </tbody>
    </table>
  </div>

  <!-- Pagination -->
  {#if totalPages > 1}
    <div class="flex items-center justify-between text-xs text-on-surface-variant/50">
      <span>Page {page} of {totalPages}</span>
      <div class="flex gap-2">
        <button class="admin-btn-ghost" disabled={page <= 1} on:click={() => { page--; load(); }}>
          <ChevronLeft class="w-3.5 h-3.5" />
        </button>
        <button class="admin-btn-ghost" disabled={page >= totalPages} on:click={() => { page++; load(); }}>
          <ChevronRight class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  {/if}
</div>

<!-- Edit modal -->
{#if editUser}
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div class="modal-backdrop" on:click={() => editUser = null}></div>
  <div class="modal-box">
    <div class="flex items-center justify-between mb-5">
      <h3 class="text-sm font-semibold text-white">Edit User</h3>
      <button on:click={() => editUser = null}><X class="w-4 h-4 text-on-surface-variant/40" /></button>
    </div>
    <p class="text-xs text-on-surface-variant/60 mb-4">{editUser.email}</p>
    <div class="space-y-3">
      <div>
        <label class="modal-label">Role</label>
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <!-- svelte-ignore a11y-no-static-element-interactions -->
        <div class="dropdown-wrap w-full" on:click|stopPropagation={() => { editRoleOpen = !editRoleOpen; editStatusOpen = false; }}>
          <span class="dropdown-label">{labelFor(EDIT_ROLE_OPTIONS, editRole)}</span>
          <ChevronDown class="w-3 h-3 opacity-50 transition-transform {editRoleOpen ? 'rotate-180' : ''}" />
          {#if editRoleOpen}
            <div class="dropdown-menu">
              {#each EDIT_ROLE_OPTIONS as opt}
                <button class="dropdown-item {editRole === opt.value ? 'dropdown-item-active' : ''}"
                  on:click|stopPropagation={() => { editRole = opt.value; editRoleOpen = false; }}>
                  {opt.label}
                </button>
              {/each}
            </div>
          {/if}
        </div>
      </div>
      <div>
        <label class="modal-label">Status</label>
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <!-- svelte-ignore a11y-no-static-element-interactions -->
        <div class="dropdown-wrap w-full" on:click|stopPropagation={() => { editStatusOpen = !editStatusOpen; editRoleOpen = false; }}>
          <span class="dropdown-label">{labelFor(EDIT_STATUS_OPTIONS, editStatus)}</span>
          <ChevronDown class="w-3 h-3 opacity-50 transition-transform {editStatusOpen ? 'rotate-180' : ''}" />
          {#if editStatusOpen}
            <div class="dropdown-menu">
              {#each EDIT_STATUS_OPTIONS as opt}
                <button class="dropdown-item {editStatus === opt.value ? 'dropdown-item-active' : ''}"
                  on:click|stopPropagation={() => { editStatus = opt.value; editStatusOpen = false; }}>
                  {opt.label}
                </button>
              {/each}
            </div>
          {/if}
        </div>
      </div>
    </div>
    <div class="flex gap-2 mt-5">
      <button class="save-btn" disabled={saving} on:click={saveEdit}>
        {#if saving}Saving…{:else}<Check class="w-3.5 h-3.5" /> Save{/if}
      </button>
      <button class="admin-btn-ghost" on:click={() => editUser = null}>Cancel</button>
    </div>
  </div>
{/if}

<style>
  .search-wrap {
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.375rem 0.75rem; border-radius: 0.625rem;
    border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.04);
    flex: 1; min-width: 200px;
  }
  .search-input {
    background: none; border: none; outline: none; color: #f0f4ff;
    font-size: 0.8125rem; width: 100%;
  }
  .search-input::placeholder { color: rgba(107,118,161,0.5); }

  /* Custom dropdown */
  .dropdown-wrap {
    position: relative; display: inline-flex; align-items: center; gap: 0.5rem;
    padding: 0.375rem 0.75rem; border-radius: 0.625rem;
    border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.04);
    color: #f0f4ff; font-size: 0.8125rem; cursor: pointer;
    user-select: none; min-width: 120px;
  }
  .dropdown-wrap:hover { border-color: rgba(255,255,255,0.15); background: rgba(255,255,255,0.07); }

  .dropdown-label { flex: 1; white-space: nowrap; }

  .dropdown-menu {
    position: absolute; top: calc(100% + 6px); left: 0; z-index: 200;
    min-width: 100%; background: #0d1117;
    border: 1px solid rgba(255,255,255,0.1); border-radius: 0.625rem;
    box-shadow: 0 16px 40px rgba(0,0,0,0.7);
    overflow: hidden; padding: 0.25rem;
  }

  .dropdown-item {
    display: block; width: 100%; text-align: left;
    padding: 0.5rem 0.75rem; border-radius: 0.375rem;
    font-size: 0.8125rem; color: rgba(184,191,214,0.8);
    background: none; border: none; cursor: pointer;
    transition: background 0.12s, color 0.12s;
  }
  .dropdown-item:hover { background: rgba(255,255,255,0.07); color: #fff; }
  .dropdown-item-active { color: #00d9ff; background: rgba(0,217,255,0.08); }

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

  .avatar {
    width: 2rem; height: 2rem; border-radius: 0.5rem;
    background: linear-gradient(135deg, #00d9ff, #3a86ff);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.65rem; font-weight: 700; color: #060914; flex-shrink: 0;
  }

  .role-badge {
    display: inline-flex; padding: 0.15rem 0.5rem; border-radius: 0.25rem;
    font-size: 0.65rem; font-weight: 600; border: 1px solid;
  }

  .status-dot-inline {
    display: inline-block; width: 0.5rem; height: 0.5rem;
    border-radius: 50%; margin-right: 0.375rem;
  }

  .action-btn {
    width: 1.75rem; height: 1.75rem; border-radius: 0.375rem;
    display: flex; align-items: center; justify-content: center;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);
    color: rgba(184,191,214,0.6); cursor: pointer; transition: all 0.15s;
  }
  .action-btn:hover { background: rgba(255,255,255,0.08); color: white; }
  .action-danger:hover { background: rgba(248,113,113,0.1); color: #f87171; border-color: rgba(248,113,113,0.2); }

  .skeleton-row { height: 2.5rem; border-radius: 0.375rem; background: rgba(255,255,255,0.04); animation: shimmer 1.5s infinite; background-size: 200% 100%; }

  .modal-backdrop { position: fixed; inset: 0; z-index: 900; background: rgba(0,0,0,0.7); backdrop-filter: blur(4px); }
  .modal-box {
    position: fixed; z-index: 901; top: 50%; left: 50%; transform: translate(-50%,-50%);
    width: min(90vw, 380px); padding: 1.5rem; border-radius: 1rem;
    border: 1px solid rgba(255,255,255,0.08); background: rgba(8,11,24,0.97);
    backdrop-filter: blur(20px); box-shadow: 0 30px 80px rgba(0,0,0,0.6);
  }
  .modal-label { display: block; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: rgba(184,191,214,0.6); margin-bottom: 0.375rem; }

  .save-btn {
    display: inline-flex; align-items: center; gap: 0.375rem;
    padding: 0.5rem 1rem; border-radius: 0.625rem;
    font-size: 0.8125rem; font-weight: 600; color: #060914;
    background: linear-gradient(135deg, #00d9ff, #3a86ff);
    border: none; cursor: pointer; transition: opacity 0.2s;
  }
  .save-btn:disabled { opacity: 0.5; cursor: not-allowed; }

  .admin-btn-ghost {
    display: inline-flex; align-items: center; gap: 0.375rem;
    padding: 0.375rem 0.75rem; border-radius: 0.5rem;
    font-size: 0.75rem; font-weight: 500; color: rgba(184,191,214,0.6);
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);
    cursor: pointer; transition: all 0.15s;
  }
  .admin-btn-ghost:hover:not(:disabled) { background: rgba(255,255,255,0.08); color: white; }
  .admin-btn-ghost:disabled { opacity: 0.3; cursor: not-allowed; }

  .admin-error { padding: 0.75rem 1rem; border-radius: 0.75rem; background: rgba(248,113,113,0.08); border: 1px solid rgba(248,113,113,0.2); color: #f87171; font-size: 0.875rem; }
  .admin-toast { padding: 0.75rem 1rem; border-radius: 0.75rem; background: rgba(52,211,153,0.08); border: 1px solid rgba(52,211,153,0.2); color: #34d399; font-size: 0.875rem; }

  @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
</style>
