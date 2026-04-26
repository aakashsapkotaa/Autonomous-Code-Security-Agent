<script lang="ts">
  import { adminGet } from '$lib/adminApi';
  import { Download, Users, ScanLine, AlertTriangle, Clock } from 'lucide-svelte';

  type ReportKey = 'users' | 'scans' | 'vulnerabilities';

  const REPORTS: { key: ReportKey; label: string; desc: string; icon: any; color: string }[] = [
    {
      key: 'users',
      label: 'Users Report',
      desc: 'All registered users with roles, status, and activity metrics.',
      icon: Users,
      color: '#3a86ff',
    },
    {
      key: 'scans',
      label: 'Scans Report',
      desc: 'Complete scan history with status, duration, and repository details.',
      icon: ScanLine,
      color: '#9d4edd',
    },
    {
      key: 'vulnerabilities',
      label: 'Vulnerabilities Report',
      desc: 'All detected vulnerabilities with severity, CVE IDs, and remediation status.',
      icon: AlertTriangle,
      color: '#ff006e',
    },
  ];

  let downloading: Record<ReportKey, boolean> = { users: false, scans: false, vulnerabilities: false };
  let lastGenerated: Record<ReportKey, string | null> = { users: null, scans: null, vulnerabilities: null };
  let errors: Record<ReportKey, string> = { users: '', scans: '', vulnerabilities: '' };

  async function download(key: ReportKey) {
    downloading[key] = true;
    errors[key] = '';
    try {
      const data = await adminGet(`/reports/${key}`);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${key}-report-${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
      lastGenerated[key] = new Date().toLocaleString();
      lastGenerated = { ...lastGenerated };
    } catch (e: any) {
      errors[key] = e.message;
    } finally {
      downloading[key] = false;
      downloading = { ...downloading };
    }
  }
</script>

<svelte:head><title>Reports — Admin</title></svelte:head>

<div class="space-y-5">
  <div>
    <h1 class="text-xl font-bold text-white">Reports</h1>
    <p class="text-xs text-muted mt-0.5">Download platform data as JSON</p>
  </div>

  <div class="reports-grid">
    {#each REPORTS as report}
      <div class="report-card">
        <div class="report-header">
          <div class="report-icon" style="background:{report.color}12; color:{report.color}; border-color:{report.color}25">
            <svelte:component this={report.icon} class="w-5 h-5" />
          </div>
          <div>
            <h2 class="text-sm font-semibold text-white">{report.label}</h2>
            <p class="text-xs text-muted mt-0.5 leading-relaxed">{report.desc}</p>
          </div>
        </div>

        {#if errors[report.key]}
          <div class="admin-error text-xs mt-3">{errors[report.key]}</div>
        {/if}

        {#if lastGenerated[report.key]}
          <div class="last-gen">
            <Clock class="w-3 h-3" />
            Last generated: {lastGenerated[report.key]}
          </div>
        {/if}

        <button
          class="download-btn"
          style="--accent:{report.color}"
          disabled={downloading[report.key]}
          on:click={() => download(report.key)}
        >
          {#if downloading[report.key]}
            <div class="spin"></div>
            Generating…
          {:else}
            <Download class="w-3.5 h-3.5" />
            Download JSON
          {/if}
        </button>
      </div>
    {/each}
  </div>

  <div class="info-note">
    <span class="note-dot"></span>
    Reports are generated in real-time from the live database. Large datasets may take a moment to download.
  </div>
</div>

<style>
  .text-muted { color: rgba(184,191,214,0.5); }

  .reports-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }

  .report-card {
    padding: 1.25rem; border-radius: 0.875rem;
    border: 1px solid rgba(255,255,255,0.06); background: rgba(255,255,255,0.02);
    display: flex; flex-direction: column; gap: 0.875rem;
    transition: border-color 0.2s;
  }
  .report-card:hover { border-color: rgba(255,255,255,0.1); }

  .report-header { display: flex; align-items: flex-start; gap: 0.875rem; }

  .report-icon {
    width: 2.75rem; height: 2.75rem; border-radius: 0.625rem;
    display: flex; align-items: center; justify-content: center;
    border: 1px solid; flex-shrink: 0;
  }

  .last-gen {
    display: flex; align-items: center; gap: 0.375rem;
    font-size: 0.7rem; color: rgba(184,191,214,0.4);
  }

  .download-btn {
    display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem;
    padding: 0.5rem 1rem; border-radius: 0.625rem;
    font-size: 0.8125rem; font-weight: 600;
    color: var(--accent); background: color-mix(in srgb, var(--accent) 10%, transparent);
    border: 1px solid color-mix(in srgb, var(--accent) 25%, transparent);
    cursor: pointer; transition: all 0.15s; width: 100%;
  }
  .download-btn:hover:not(:disabled) {
    background: color-mix(in srgb, var(--accent) 18%, transparent);
  }
  .download-btn:disabled { opacity: 0.5; cursor: not-allowed; }

  .spin {
    width: 0.875rem; height: 0.875rem; border-radius: 50%;
    border: 2px solid currentColor; border-top-color: transparent;
    animation: spin 0.7s linear infinite;
  }

  .info-note {
    display: flex; align-items: center; gap: 0.625rem;
    padding: 0.75rem 1rem; border-radius: 0.75rem;
    background: rgba(58,134,255,0.05); border: 1px solid rgba(58,134,255,0.12);
    font-size: 0.75rem; color: rgba(184,191,214,0.6);
  }
  .note-dot {
    width: 0.4rem; height: 0.4rem; border-radius: 50%;
    background: #3a86ff; flex-shrink: 0;
  }

  .admin-error { padding: 0.5rem 0.75rem; border-radius: 0.5rem; background: rgba(248,113,113,0.08); border: 1px solid rgba(248,113,113,0.2); color: #f87171; }

  @keyframes spin { to { transform: rotate(360deg); } }
</style>
