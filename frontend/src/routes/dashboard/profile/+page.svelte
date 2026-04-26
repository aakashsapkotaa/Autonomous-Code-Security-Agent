<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { supabase } from '$lib/supabaseClient';
  import { apiGet, apiPut } from '$lib/api';
  import AuroraBackground from '$lib/components/AuroraBackground.svelte';
  import {
    Shield, ArrowLeft, User, Mail, Calendar, GitBranch,
    ShieldAlert, CheckCircle, Camera, Loader, Save
  } from 'lucide-svelte';
  import type { User as SupaUser } from '@supabase/supabase-js';

  let user: SupaUser | null = null;
  let profile: any = null;
  let loading = true;
  let saving = false;
  let saved = false;
  let error = '';

  let editName = '';
  let editBio = '';
  let avatarPreview = '';

  onMount(async () => {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) { goto('/'); return; }
    user = session.user;
    await loadProfile();
  });

  async function loadProfile() {
    loading = true;
    try {
      profile = await apiGet('/api/profile');
      editName = profile.name || '';
      editBio = profile.bio || '';
      avatarPreview = profile.avatar_url || '';
    } catch (e: any) { error = e.message; }
    finally { loading = false; }
  }

  async function saveProfile() {
    saving = true; error = '';
    try {
      profile = await apiPut('/api/profile', {
        name: editName || null,
        bio: editBio || null,
        avatar_url: avatarPreview || null,
      });
      saved = true;
      setTimeout(() => saved = false, 2500);
    } catch (e: any) { error = e.message; }
    finally { saving = false; }
  }

  function handleAvatarInput(e: Event) {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = ev => { avatarPreview = ev.target?.result as string; };
    reader.readAsDataURL(file);
  }

  const STAT_META = [
    { key: 'repo_count',  label: 'Repositories',  color: '#00d9ff', icon: GitBranch    },
    { key: 'scan_count',  label: 'Total Scans',    color: '#9d4edd', icon: Shield       },
    { key: 'vuln_count',  label: 'Vulnerabilities',color: '#f87171', icon: ShieldAlert  },
    { key: 'fixes_count', label: 'Fixes Applied',  color: '#34d399', icon: CheckCircle  },
  ];

  function fmtDate(iso: string) {
    return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  }
</script>

<svelte:head><title>Profile — SecureShift</title></svelte:head>

<div class="min-h-screen bg-[#060914]">
  <AuroraBackground />
  <div class="relative z-10 max-w-3xl mx-auto px-5 sm:px-8 py-10">

    <a href="/dashboard" class="inline-flex items-center gap-2 text-sm text-on-surface-variant/60 hover:text-neon-cyan transition-colors mb-8">
      <ArrowLeft class="w-4 h-4" /> Back to Dashboard
    </a>

    {#if loading}
      <div class="flex items-center justify-center py-20">
        <Loader class="w-6 h-6 text-neon-cyan animate-spin" />
      </div>
    {:else if profile}

      <!-- Header card -->
      <div class="glass-card mb-6">
        <div class="flex flex-col sm:flex-row items-start sm:items-center gap-5">
          <!-- Avatar -->
          <div class="relative group">
            <div class="w-20 h-20 rounded-2xl overflow-hidden border-2 border-neon-cyan/20 bg-gradient-to-br from-neon-cyan/20 to-neon-blue/10 flex items-center justify-center">
              {#if avatarPreview}
                <img src={avatarPreview} alt="avatar" class="w-full h-full object-cover" />
              {:else}
                <span class="text-2xl font-headline font-bold text-neon-cyan">
                  {(editName || profile.email || 'U').slice(0, 2).toUpperCase()}
                </span>
              {/if}
            </div>
            <label class="absolute inset-0 flex items-center justify-center bg-black/50 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
              <Camera class="w-5 h-5 text-white" />
              <input type="file" accept="image/*" class="hidden" on:change={handleAvatarInput} />
            </label>
          </div>

          <div class="flex-1 min-w-0">
            <h1 class="text-xl font-headline font-bold text-white">{profile.name || 'Unnamed User'}</h1>
            <p class="text-sm text-on-surface-variant/60 mt-0.5 flex items-center gap-1.5">
              <Mail class="w-3.5 h-3.5" /> {profile.email}
            </p>
            {#if profile.created_at}
              <p class="text-xs text-on-surface-variant/40 mt-1 flex items-center gap-1.5">
                <Calendar class="w-3 h-3" /> Member since {fmtDate(profile.created_at)}
              </p>
            {/if}
          </div>
        </div>

        <!-- Stats row -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6 pt-5 border-t border-white/[0.06]">
          {#each STAT_META as s}
            <div class="stat-mini" style="--c:{s.color}">
              <svelte:component this={s.icon} class="w-4 h-4 mb-1" style="color:{s.color}" />
              <div class="text-xl font-headline font-bold" style="color:{s.color}">{profile[s.key] ?? 0}</div>
              <div class="text-[10px] text-on-surface-variant/50 uppercase tracking-wider">{s.label}</div>
            </div>
          {/each}
        </div>
      </div>

      <!-- Edit form -->
      <div class="glass-card">
        <h2 class="text-sm font-semibold text-white mb-5">Edit Profile</h2>

        {#if error}
          <p class="text-xs text-red-400 mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20">{error}</p>
        {/if}

        <div class="space-y-4">
          <div>
            <label class="field-label">Full Name</label>
            <input bind:value={editName} type="text" placeholder="Your name" class="field-input" />
          </div>
          <div>
            <label class="field-label">Bio</label>
            <textarea bind:value={editBio} placeholder="A short bio…" rows="3" class="field-input resize-none"></textarea>
          </div>
          <div>
            <label class="field-label">Avatar URL</label>
            <input bind:value={avatarPreview} type="url" placeholder="https://…" class="field-input" />
            <p class="text-[11px] text-on-surface-variant/40 mt-1">Or upload via the avatar above</p>
          </div>
        </div>

        <div class="flex items-center gap-3 mt-6">
          <button class="save-btn" disabled={saving} on:click={saveProfile}>
            {#if saving}
              <Loader class="w-4 h-4 animate-spin" /> Saving…
            {:else if saved}
              <CheckCircle class="w-4 h-4" /> Saved!
            {:else}
              <Save class="w-4 h-4" /> Save Changes
            {/if}
          </button>
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .glass-card {
    padding: 1.5rem;
    border-radius: 1rem;
    border: 1px solid rgba(255,255,255,0.07);
    background: rgba(8,11,24,0.8);
    backdrop-filter: blur(20px);
    margin-bottom: 1rem;
  }

  .stat-mini {
    display: flex; flex-direction: column; align-items: center;
    padding: 0.875rem; border-radius: 0.75rem;
    border: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.02);
    text-align: center;
    transition: border-color 0.2s;
  }
  .stat-mini:hover { border-color: color-mix(in srgb, var(--c) 30%, transparent); }

  .field-label {
    display: block; font-size: 0.7rem; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: rgba(184,191,214,0.7); margin-bottom: 0.375rem;
  }

  .field-input {
    width: 100%; padding: 0.625rem 0.875rem; border-radius: 0.625rem;
    border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.04);
    color: #f0f4ff; font-size: 0.875rem; outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
    font-family: inherit;
  }
  .field-input::placeholder { color: rgba(107,118,161,0.5); }
  .field-input:focus {
    border-color: rgba(0,217,255,0.4);
    box-shadow: 0 0 0 3px rgba(0,217,255,0.07);
  }

  .save-btn {
    display: inline-flex; align-items: center; gap: 0.5rem;
    padding: 0.625rem 1.25rem; border-radius: 0.625rem;
    font-size: 0.8125rem; font-weight: 600; color: #060914;
    background: linear-gradient(135deg, #00d9ff, #3a86ff);
    border: none; cursor: pointer;
    transition: opacity 0.2s, transform 0.15s;
  }
  .save-btn:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
  .save-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
