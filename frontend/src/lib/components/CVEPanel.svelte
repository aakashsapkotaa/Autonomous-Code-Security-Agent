<script lang="ts">
  import { onMount } from 'svelte';
  import {
    ShieldAlert, ChevronDown, ChevronUp, ExternalLink,
    Loader, RefreshCw, Package, AlertTriangle
  } from 'lucide-svelte';
  import { PUBLIC_API_URL } from '$env/static/public';

  export let scanId: string;

  const api = PUBLIC_API_URL || 'http://localhost:8000';

  type Severity = 'critical' | 'high' | 'medium' | 'low' | 'unknown';

  interface CVEFinding {
    id: string;
    package_name: string;
    package_version: string;
    ecosystem: string;
    source_file: string;
    cve_id: string;
    cvss_score: number | null;
    severity: Severity;
    description: string | null;
    fix_version: string | null;
    reference_url: string | null;
    source: string;
  }

  interface CVESummary {
    scan_id: string;
    total: number;
    critical: number;
    high: number;
    medium: number;
    low: number;
    unknown: number;
    packages_affected: number;
    findings: CVEFinding[];
  }

  let summary: CVESummary | null = null;
  let loading = true;
  let error = '';
  let expandedId: string | null = null;
  let filterSev: Severity | 'all' = 'all';

  const SEV_META: Record<Severity, { label: string; color: string; bg: string; border: string }> = {
    critical: { label: 'Critical', color: '#f87171', bg: 'rgba(248,113,113,0.1)',  border: 'rgba(248,113,113,0.25)' },
    high:     { label: 'High',     color: '#fb923c', bg: 'rgba(251,146,60,0.1)',   border: 'rgba(251,146,60,0.25)'  },
    medium:   { label: 'Medium',   color: '#fbbf24', bg: 'rgba(251,191,36,0.1)',   border: 'rgba(251,191,36,0.25)'  },
    low:      { label: 'Low',      color: '#34d399', bg: 'rgba(52,211,153,0.1)',   border: 'rgba(52,211,153,0.25)'  },
    unknown:  { label: 'Unknown',  color: '#94a3b8', bg: 'rgba(148,163,184,0.08)', border: 'rgba(148,163,184,0.15)' },
  };

  $: filtered = summary?.findings.filter(
    f => filterSev === 'all' || f.severity === filterSev
  ) ?? [];

  onMount(() => fetchFindings());

  async function fetchFindings() {
    loading = true; error = '';
    try {
      const res = await fetch(`${api}/api/cves/${scanId}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      summary = await res.json();
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  function toggle(id: string) {
    expandedId = expandedId === id ? null : id;
  }

  function scoreBar(score: number | null): number {
    return score ? Math.min((score / 10) * 100, 100) : 0;
  }
</script>

<div class="cve-panel">
  <!-- Header -->
  <div class="flex items-center justify-between mb-5">
    <div class="flex items-center gap-2.5">
      <div class="w-8 h-8 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center justify-center">
        <ShieldAlert class="w-4 h-4 text-red-400" />
      </div>
      <div>
        <h3 class="text-sm font-semibold text-white">CVE Findings</h3>
        {#if summary}
          <p class="text-[11px] text-on-surface-variant/50 mt-0.5">
            {summary.total} CVEs across {summary.packages_affected} packages
          </p>
        {/if}
      </div>
    </div>
    <button
      class="nav-icon-btn"
      on:click={fetchFindings}
      title="Refresh"
      disabled={loading}
    >
      <RefreshCw class="w-3.5 h-3.5 {loading ? 'animate-spin' : ''}" />
    </button>
  </div>

  {#if loading}
    <div class="flex items-center justify-center py-10 gap-3 text-sm text-on-surface-variant/50">
      <Loader class="w-4 h-4 animate-spin" /> Loading CVE data...
    </div>

  {:else if error}
    <div class="flex items-start gap-2 p-3 rounded-xl border border-red-500/20 bg-red-500/5 text-sm text-red-400">
      <AlertTriangle class="w-4 h-4 flex-shrink-0 mt-0.5" />
      <span>{error}</span>
    </div>

  {:else if !summary || summary.total === 0}
    <div class="text-center py-8">
      <Package class="w-8 h-8 text-on-surface-variant/20 mx-auto mb-2" />
      <p class="text-sm text-on-surface-variant/40">No CVEs found for this scan.</p>
      <p class="text-xs text-on-surface-variant/30 mt-1">Run a CVE lookup after scanning.</p>
    </div>

  {:else}
    <!-- Severity summary pills -->
    <div class="flex flex-wrap gap-2 mb-4">
      <button
        class="sev-pill {filterSev === 'all' ? 'sev-pill-active' : ''}"
        on:click={() => filterSev = 'all'}
      >
        All <span class="sev-count">{summary.total}</span>
      </button>
      {#each (['critical','high','medium','low'] as const) as sev}
        {#if summary[sev] > 0}
          <button
            class="sev-pill"
            style="
              color:{SEV_META[sev].color};
              background:{filterSev === sev ? SEV_META[sev].bg : 'transparent'};
              border-color:{filterSev === sev ? SEV_META[sev].border : 'rgba(255,255,255,0.07)'};
            "
            on:click={() => filterSev = filterSev === sev ? 'all' : sev}
          >
            {SEV_META[sev].label}
            <span class="sev-count" style="background:{SEV_META[sev].bg}; color:{SEV_META[sev].color}">
              {summary[sev]}
            </span>
          </button>
        {/if}
      {/each}
    </div>

    <!-- Findings list -->
    <div class="space-y-2">
      {#each filtered as f (f.id || f.cve_id + f.package_name)}
        {@const meta = SEV_META[f.severity] ?? SEV_META.unknown}
        <div
          class="finding-card"
          style="border-color:{expandedId === f.id ? meta.border : 'rgba(255,255,255,0.06)'}"
        >
          <!-- Row -->
          <button
            class="finding-row"
            on:click={() => toggle(f.id)}
          >
            <!-- Severity dot -->
            <span class="sev-dot" style="background:{meta.color}; box-shadow:0 0 6px {meta.color}"></span>

            <!-- CVE ID -->
            <span class="text-xs font-mono font-semibold text-white w-36 flex-shrink-0 truncate">
              {f.cve_id}
            </span>

            <!-- Package -->
            <span class="text-xs text-on-surface-variant/70 flex-1 truncate">
              <span class="text-white/80">{f.package_name}</span>
              <span class="text-on-surface-variant/40 ml-1">@{f.package_version}</span>
            </span>

            <!-- CVSS score -->
            {#if f.cvss_score !== null}
              <span
                class="text-xs font-bold w-10 text-right flex-shrink-0"
                style="color:{meta.color}"
              >
                {f.cvss_score.toFixed(1)}
              </span>
            {/if}

            <!-- Chevron -->
            <span class="text-on-surface-variant/30 flex-shrink-0 ml-1">
              {#if expandedId === f.id}
                <ChevronUp class="w-3.5 h-3.5" />
              {:else}
                <ChevronDown class="w-3.5 h-3.5" />
              {/if}
            </span>
          </button>

          <!-- Expanded detail -->
          {#if expandedId === f.id}
            <div class="finding-detail">
              <!-- CVSS bar -->
              {#if f.cvss_score !== null}
                <div class="mb-3">
                  <div class="flex justify-between text-[10px] text-on-surface-variant/50 mb-1">
                    <span>CVSS Score</span>
                    <span style="color:{meta.color}">{f.cvss_score.toFixed(1)} / 10 — {meta.label}</span>
                  </div>
                  <div class="h-1.5 rounded-full bg-white/[0.06] overflow-hidden">
                    <div
                      class="h-full rounded-full transition-all duration-500"
                      style="width:{scoreBar(f.cvss_score)}%; background:{meta.color}"
                    ></div>
                  </div>
                </div>
              {/if}

              <!-- Meta grid -->
              <div class="grid grid-cols-2 gap-x-4 gap-y-1.5 text-[11px] mb-3">
                <div>
                  <span class="text-on-surface-variant/40">Ecosystem</span>
                  <p class="text-white/80 font-medium">{f.ecosystem}</p>
                </div>
                <div>
                  <span class="text-on-surface-variant/40">Source file</span>
                  <p class="text-white/80 font-medium font-mono">{f.source_file}</p>
                </div>
                {#if f.fix_version}
                  <div>
                    <span class="text-on-surface-variant/40">Fix version</span>
                    <p class="text-green-400 font-medium font-mono">≥ {f.fix_version}</p>
                  </div>
                {/if}
                <div>
                  <span class="text-on-surface-variant/40">Data source</span>
                  <p class="text-white/80 font-medium uppercase">{f.source}</p>
                </div>
              </div>

              <!-- Description -->
              {#if f.description}
                <p class="text-[11px] text-on-surface-variant/60 leading-relaxed mb-3">
                  {f.description}
                </p>
              {/if}

              <!-- Reference link -->
              {#if f.reference_url}
                <a
                  href={f.reference_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  class="inline-flex items-center gap-1.5 text-[11px] text-neon-cyan hover:underline"
                >
                  <ExternalLink class="w-3 h-3" /> View advisory
                </a>
              {/if}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .cve-panel {
    padding: 1.25rem;
    border-radius: 1rem;
    border: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.02);
    backdrop-filter: blur(12px);
  }

  .nav-icon-btn {
    width: 2rem; height: 2rem;
    display: flex; align-items: center; justify-content: center;
    border-radius: 0.5rem;
    border: 1px solid rgba(255,255,255,0.07);
    background: rgba(255,255,255,0.03);
    color: rgba(184,191,214,0.5);
    cursor: pointer;
    transition: all 0.2s;
  }
  .nav-icon-btn:hover:not(:disabled) {
    background: rgba(255,255,255,0.07);
    color: white;
  }
  .nav-icon-btn:disabled { opacity: 0.4; cursor: not-allowed; }

  /* Severity pills */
  .sev-pill {
    display: inline-flex; align-items: center; gap: 0.375rem;
    padding: 0.25rem 0.625rem;
    border-radius: 9999px;
    font-size: 0.7rem; font-weight: 500;
    border: 1px solid rgba(255,255,255,0.07);
    color: rgba(184,191,214,0.7);
    background: transparent;
    cursor: pointer;
    transition: all 0.15s;
  }
  .sev-pill:hover { border-color: rgba(255,255,255,0.15); color: white; }
  .sev-pill-active { background: rgba(255,255,255,0.06); color: white; border-color: rgba(255,255,255,0.15); }

  .sev-count {
    display: inline-flex; align-items: center; justify-content: center;
    min-width: 1.25rem; height: 1.25rem;
    border-radius: 9999px;
    font-size: 0.65rem; font-weight: 700;
    background: rgba(255,255,255,0.08);
    padding: 0 0.25rem;
  }

  /* Finding card */
  .finding-card {
    border-radius: 0.625rem;
    border: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.02);
    overflow: hidden;
    transition: border-color 0.2s;
  }

  .finding-row {
    width: 100%;
    display: flex; align-items: center; gap: 0.625rem;
    padding: 0.625rem 0.875rem;
    background: none; border: none; cursor: pointer;
    text-align: left;
    transition: background 0.15s;
  }
  .finding-row:hover { background: rgba(255,255,255,0.03); }

  .sev-dot {
    width: 0.5rem; height: 0.5rem;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .finding-detail {
    padding: 0.875rem;
    border-top: 1px solid rgba(255,255,255,0.05);
    background: rgba(255,255,255,0.02);
    animation: slideDown 0.15s ease;
  }

  @keyframes slideDown {
    from { opacity: 0; transform: translateY(-4px); }
    to   { opacity: 1; transform: translateY(0); }
  }
</style>
