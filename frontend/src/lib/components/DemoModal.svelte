<script lang="ts">
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';
  import { X, ChevronLeft, ChevronRight, GitBranch, Shield, Zap, Bot, GitPullRequest, BarChart2, Play, Pause } from 'lucide-svelte';

  export let open = false;
  const dispatch = createEventDispatcher();

  let current = 0;
  let autoplay = true;
  let autoTimer: ReturnType<typeof setInterval> | null = null;
  let logIndex = 0;
  let logTimer: ReturnType<typeof setInterval> | null = null;

  const TOTAL = 6;
  const AUTO_MS = 6000;

  // ── Step data ──────────────────────────────────────────────────────────────
  const steps = [
    { id: 1, icon: GitBranch, color: '#00d9ff', label: 'Add Repository',       title: 'Connect any GitHub repository in seconds' },
    { id: 2, icon: Shield,    color: '#9d4edd', label: 'Scan Pipeline',         title: 'Multi-tool security analysis runs automatically' },
    { id: 3, icon: Zap,       color: '#f87171', label: 'Vulnerabilities Found', title: 'Issues ranked by severity with full context' },
    { id: 4, icon: Bot,       color: '#fbbf24', label: 'AI Fix Agent',          title: 'OpenRouter AI generates precise code patches' },
    { id: 5, icon: GitPullRequest, color: '#34d399', label: 'PR Agent',         title: 'Patches committed and a Draft PR opened automatically' },
    { id: 6, icon: BarChart2, color: '#3a86ff', label: 'Dashboard',             title: 'Track vulnerabilities and fixes over time' },
  ];

  const scanLogs = [
    { type: 'info',  text: 'Cloning djangogoat repository...' },
    { type: 'ok',    text: 'Repository cloned successfully' },
    { type: 'info',  text: 'Running Bandit static analysis...' },
    { type: 'warn',  text: 'HIGH  SQL injection — db/queries.py:42' },
    { type: 'error', text: 'CRIT  Hardcoded secret — config.py:17' },
    { type: 'info',  text: 'Running TruffleHog secret scan...' },
    { type: 'warn',  text: 'HIGH  API key exposed — .env:3' },
    { type: 'info',  text: 'Running Safety dependency check...' },
    { type: 'warn',  text: 'HIGH  CVE-2024-3094 in requests==2.28.0' },
    { type: 'info',  text: 'Querying OSV.dev + NVD for CVEs...' },
    { type: 'ok',    text: 'CVE lookup complete — 3 packages affected' },
    { type: 'ok',    text: 'Scan complete — 12 issues found' },
  ];

  $: visibleLogs = scanLogs.slice(0, logIndex + 1);

  function startLogAnimation() {
    logIndex = 0;
    if (logTimer) clearInterval(logTimer);
    logTimer = setInterval(() => {
      if (logIndex < scanLogs.length - 1) { logIndex++; }
      else { if (logTimer) clearInterval(logTimer); }
    }, 350);
  }

  $: if (open && current === 1) startLogAnimation();

  function startAutoplay() {
    if (autoTimer) clearInterval(autoTimer);
    autoTimer = setInterval(() => {
      current = (current + 1) % TOTAL;
    }, AUTO_MS);
  }

  function stopAutoplay() {
    if (autoTimer) { clearInterval(autoTimer); autoTimer = null; }
  }

  $: if (open && autoplay) startAutoplay();
  $: if (!autoplay || !open) stopAutoplay();

  function prev() { autoplay = false; current = (current - 1 + TOTAL) % TOTAL; }
  function next() { autoplay = false; current = (current + 1) % TOTAL; }
  function goTo(i: number) { autoplay = false; current = i; }
  function close() { stopAutoplay(); dispatch('close'); }

  function handleKey(e: KeyboardEvent) {
    if (!open) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowRight') next();
    if (e.key === 'ArrowLeft')  prev();
  }

  onMount(() => window.addEventListener('keydown', handleKey));
  onDestroy(() => { window.removeEventListener('keydown', handleKey); stopAutoplay(); if (logTimer) clearInterval(logTimer); });
</script>

{#if open}
<!-- Backdrop -->
<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-static-element-interactions -->
<div class="modal-backdrop" on:click={close}></div>

<div class="modal-shell" role="dialog" aria-modal="true">

  <!-- Header bar -->
  <div class="modal-header">
    <div class="flex items-center gap-3">
      <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-neon-cyan/20 to-neon-blue/10 border border-neon-cyan/20 flex items-center justify-center">
        <Shield class="w-3.5 h-3.5 text-neon-cyan" />
      </div>
      <span class="text-sm font-semibold text-white">How SecureShift Works</span>
      <span class="text-xs text-on-surface-variant/40">Step {current + 1} of {TOTAL}</span>
    </div>
    <div class="flex items-center gap-2">
      <button
        class="autoplay-btn"
        on:click={() => { autoplay = !autoplay; }}
        title={autoplay ? 'Pause autoplay' : 'Resume autoplay'}
      >
        {#if autoplay}
          <Pause class="w-3.5 h-3.5" />
        {:else}
          <Play class="w-3.5 h-3.5" />
        {/if}
      </button>
      <button class="close-btn" on:click={close} aria-label="Close">
        <X class="w-4 h-4" />
      </button>
    </div>
  </div>

  <!-- Progress bar -->
  <div class="progress-track">
    <div class="progress-fill" style="width:{((current + 1) / TOTAL) * 100}%"></div>
  </div>

  <!-- Step tabs -->
  <div class="step-tabs">
    {#each steps as s, i}
      <button
        class="step-tab {current === i ? 'step-tab-active' : ''}"
        on:click={() => goTo(i)}
        style={current === i ? `--tc:${s.color}` : ''}
      >
        <svelte:component this={s.icon} class="w-3.5 h-3.5 flex-shrink-0" />
        <span class="hidden sm:inline">{s.label}</span>
      </button>
    {/each}
  </div>

  <!-- Slide content -->
  <div class="slide-area">

    <!-- ── Step 1: Add Repository ── -->
    {#if current === 0}
      <div class="slide-in">
        <div class="slide-title" style="--c:#00d9ff">
          <GitBranch class="w-5 h-5" style="color:#00d9ff" />
          Step 1 — Add Repository
        </div>
        <p class="slide-sub">Connect any GitHub repository in seconds. No installation required.</p>

        <div class="demo-card mt-6">
          <div class="demo-card-label">GitHub Repository URL</div>
          <div class="url-input-demo">
            <GitBranch class="w-4 h-4 text-neon-cyan/60 flex-shrink-0" />
            <span class="text-neon-cyan font-mono text-sm">https://github.com/red-and-black/djangogoat</span>
            <span class="ml-auto text-[11px] px-2 py-0.5 rounded-full bg-neon-cyan/10 text-neon-cyan border border-neon-cyan/20">Valid ✓</span>
          </div>
          <div class="mt-4 flex items-center gap-3">
            <div class="flow-node flow-node-cyan">User</div>
            <div class="flow-arrow">→</div>
            <div class="flow-node flow-node-cyan">Paste URL</div>
            <div class="flow-arrow">→</div>
            <div class="flow-node flow-node-cyan">Connected</div>
          </div>
        </div>

        <div class="mt-4 grid grid-cols-3 gap-3">
          {#each ['Public repos', 'Private repos', 'Any branch'] as f}
            <div class="feature-chip">✓ {f}</div>
          {/each}
        </div>
      </div>

    <!-- ── Step 2: Scan Pipeline ── -->
    {:else if current === 1}
      <div class="slide-in">
        <div class="slide-title" style="--c:#9d4edd">
          <Shield class="w-5 h-5" style="color:#9d4edd" />
          Step 2 — Scan Pipeline
        </div>
        <p class="slide-sub">Four tools run in parallel — static analysis, secret detection, dependency audit, and CVE lookup.</p>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-5">
          <!-- Pipeline diagram -->
          <div class="demo-card">
            <div class="demo-card-label">Pipeline</div>
            <div class="pipeline">
              <div class="pipeline-node pipeline-start">GitHub Repo</div>
              <div class="pipeline-arrow">↓</div>
              <div class="pipeline-row">
                <div class="pipeline-node pipeline-tool">Bandit</div>
                <div class="pipeline-node pipeline-tool">TruffleHog</div>
                <div class="pipeline-node pipeline-tool">Safety</div>
                <div class="pipeline-node pipeline-tool">CVE Lookup</div>
              </div>
              <div class="pipeline-arrow">↓</div>
              <div class="pipeline-node pipeline-end">Results</div>
            </div>
          </div>

          <!-- Live log terminal -->
          <div class="terminal-mini">
            <div class="terminal-mini-header">
              <div class="flex gap-1">
                <span class="w-2.5 h-2.5 rounded-full bg-[#ff5f57]"></span>
                <span class="w-2.5 h-2.5 rounded-full bg-[#febc2e]"></span>
                <span class="w-2.5 h-2.5 rounded-full bg-[#28c840]"></span>
              </div>
              <span class="text-[10px] text-on-surface-variant/50 font-mono">scan · live</span>
              <span class="w-1.5 h-1.5 rounded-full bg-neon-cyan animate-pulse"></span>
            </div>
            <div class="terminal-mini-body">
              {#each visibleLogs as log}
                <div class="log-line">
                  {#if log.type === 'error'}
                    <span class="text-red-400">▶</span><span class="text-red-400/80">{log.text}</span>
                  {:else if log.type === 'warn'}
                    <span class="text-yellow-400">▶</span><span class="text-yellow-400/70">{log.text}</span>
                  {:else if log.type === 'ok'}
                    <span class="text-neon-cyan">✓</span><span class="text-neon-cyan/80">{log.text}</span>
                  {:else}
                    <span class="text-on-surface-variant/40">$</span><span class="text-on-surface-variant/60">{log.text}</span>
                  {/if}
                </div>
              {/each}
              <div class="flex items-center gap-1 mt-1">
                <span class="text-on-surface-variant/40">$</span>
                <span class="w-1.5 h-3 bg-neon-cyan/70 animate-pulse inline-block"></span>
              </div>
            </div>
          </div>
        </div>
      </div>

    <!-- ── Step 3: Vulnerabilities ── -->
    {:else if current === 2}
      <div class="slide-in">
        <div class="slide-title" style="--c:#f87171">
          <Zap class="w-5 h-5" style="color:#f87171" />
          Step 3 — Vulnerabilities Found
        </div>
        <p class="slide-sub">Every issue ranked by severity with file, line number, and tool attribution.</p>

        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5">
          {#each [
            { label: 'Critical', count: 2, color: '#f87171', bg: 'rgba(248,113,113,0.1)', border: 'rgba(248,113,113,0.25)' },
            { label: 'High',     count: 4, color: '#fb923c', bg: 'rgba(251,146,60,0.1)',  border: 'rgba(251,146,60,0.25)'  },
            { label: 'Medium',   count: 6, color: '#fbbf24', bg: 'rgba(251,191,36,0.1)',  border: 'rgba(251,191,36,0.25)'  },
            { label: 'Low',      count: 8, color: '#34d399', bg: 'rgba(52,211,153,0.1)',  border: 'rgba(52,211,153,0.25)'  },
          ] as s}
            <div class="sev-card" style="background:{s.bg}; border-color:{s.border}">
              <div class="text-3xl font-headline font-bold" style="color:{s.color}">{s.count}</div>
              <div class="text-xs font-semibold mt-1" style="color:{s.color}">{s.label}</div>
            </div>
          {/each}
        </div>

        <div class="mt-4 space-y-2">
          {#each [
            { sev: 'CRIT', color: '#f87171', bg: 'rgba(248,113,113,0.08)', file: 'config.py:17',    desc: 'Hardcoded secret — API key exposed in source',   tool: 'TruffleHog' },
            { sev: 'HIGH', color: '#fb923c', bg: 'rgba(251,146,60,0.08)',  file: 'db/queries.py:42', desc: 'SQL injection via unsanitized user input',         tool: 'Bandit'     },
            { sev: 'HIGH', color: '#fb923c', bg: 'rgba(251,146,60,0.08)',  file: 'requirements.txt', desc: 'CVE-2024-3094 in requests==2.28.0',               tool: 'Safety'     },
          ] as v}
            <div class="vuln-row" style="background:{v.bg}; border-color:{v.color}33">
              <span class="sev-badge" style="background:{v.bg}; color:{v.color}; border-color:{v.color}44">{v.sev}</span>
              <div class="flex-1 min-w-0">
                <p class="text-xs font-medium text-white truncate">{v.desc}</p>
                <p class="text-[10px] text-on-surface-variant/50 font-mono mt-0.5">{v.file} · {v.tool}</p>
              </div>
            </div>
          {/each}
        </div>
      </div>

    <!-- ── Step 4: AI Fix Agent ── -->
    {:else if current === 3}
      <div class="slide-in">
        <div class="slide-title" style="--c:#fbbf24">
          <Bot class="w-5 h-5" style="color:#fbbf24" />
          Step 4 — AI Fix Agent
        </div>
        <p class="slide-sub">OpenRouter AI generates precise, context-aware code patches with confidence scores.</p>

        <div class="mt-5 flex flex-col sm:flex-row items-center gap-3">
          <div class="flow-node flow-node-yellow flex-1 text-center py-3">Vulnerability</div>
          <div class="text-on-surface-variant/40 text-lg">→</div>
          <div class="flow-node flow-node-yellow flex-1 text-center py-3">OpenRouter AI</div>
          <div class="text-on-surface-variant/40 text-lg">→</div>
          <div class="flow-node flow-node-green flex-1 text-center py-3">Patch Generated</div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4">
          <div class="code-block">
            <div class="code-block-label text-red-400">Before — vulnerable</div>
            <pre class="code-pre"><span class="text-red-400">query = "SELECT * FROM users WHERE id = " + user_id</span>
<span class="text-on-surface-variant/50">cursor.execute(query)</span></pre>
          </div>
          <div class="code-block">
            <div class="code-block-label text-neon-cyan">After — patched</div>
            <pre class="code-pre"><span class="text-neon-cyan">query = "SELECT * FROM users WHERE id = %s"</span>
<span class="text-on-surface-variant/70">cursor.execute(query, (user_id,))</span></pre>
          </div>
        </div>

        <div class="mt-3 flex items-center gap-3">
          <div class="confidence-bar-wrap">
            <div class="flex justify-between text-[10px] text-on-surface-variant/50 mb-1">
              <span>AI Confidence</span><span class="text-neon-cyan font-semibold">94%</span>
            </div>
            <div class="h-1.5 rounded-full bg-white/[0.06] overflow-hidden">
              <div class="h-full rounded-full bg-gradient-to-r from-neon-cyan to-neon-blue confidence-fill"></div>
            </div>
          </div>
        </div>
      </div>

    <!-- ── Step 5: PR Agent ── -->
    {:else if current === 4}
      <div class="slide-in">
        <div class="slide-title" style="--c:#34d399">
          <GitPullRequest class="w-5 h-5" style="color:#34d399" />
          Step 5 — PR Agent
        </div>
        <p class="slide-sub">Patches are committed to a new branch and a Draft PR is opened automatically — zero manual steps.</p>

        <div class="mt-5 flex flex-wrap items-center gap-2 justify-center">
          {#each [
            { label: 'Apply Patches', color: '#34d399' },
            { label: '→', color: 'rgba(255,255,255,0.2)' },
            { label: 'New Branch', color: '#00d9ff' },
            { label: '→', color: 'rgba(255,255,255,0.2)' },
            { label: 'Commit', color: '#9d4edd' },
            { label: '→', color: 'rgba(255,255,255,0.2)' },
            { label: 'Draft PR', color: '#fbbf24' },
          ] as n}
            {#if n.label === '→'}
              <span class="text-on-surface-variant/30 text-lg">{n.label}</span>
            {:else}
              <div class="flow-node" style="background:{n.color}18; border-color:{n.color}44; color:{n.color}">{n.label}</div>
            {/if}
          {/each}
        </div>

        <!-- GitHub PR preview card -->
        <div class="pr-preview mt-5">
          <div class="pr-preview-header">
            <GitPullRequest class="w-4 h-4 text-neon-cyan" />
            <span class="text-sm font-semibold text-white">🔒 SecureShift Automated Security Fixes</span>
            <span class="pr-badge">Draft</span>
            <span class="ml-auto text-xs text-on-surface-variant/40">#12</span>
          </div>
          <div class="pr-preview-body">
            <p class="text-xs text-on-surface-variant/70 mb-2">Branch: <code class="text-neon-cyan">fix/security-patches-20260426</code> → <code class="text-on-surface-variant/60">main</code></p>
            <div class="space-y-1">
              {#each ['✓ SQL injection fixed — db/queries.py', '✓ Hardcoded secret removed — config.py', '✓ requests upgraded to 2.32.0'] as line}
                <p class="text-[11px] text-neon-cyan/80 font-mono">{line}</p>
              {/each}
            </div>
            <div class="mt-3 flex items-center gap-2 text-[10px] text-on-surface-variant/40">
              <span class="w-1.5 h-1.5 rounded-full bg-yellow-400"></span>
              3 files changed · AI confidence avg 91%
            </div>
          </div>
        </div>
      </div>

    <!-- ── Step 6: Dashboard ── -->
    {:else if current === 5}
      <div class="slide-in">
        <div class="slide-title" style="--c:#3a86ff">
          <BarChart2 class="w-5 h-5" style="color:#3a86ff" />
          Step 6 — Dashboard Monitoring
        </div>
        <p class="slide-sub">Track vulnerabilities and fixes over time. Full audit trail for every scan.</p>

        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5">
          {#each [
            { label: 'Repositories', value: '12',   color: '#00d9ff' },
            { label: 'Total Scans',  value: '47',   color: '#9d4edd' },
            { label: 'Vulns Found',  value: '183',  color: '#f87171' },
            { label: 'Fixes Applied',value: '141',  color: '#34d399' },
          ] as s}
            <div class="dash-stat" style="border-color:{s.color}22">
              <div class="text-2xl font-headline font-bold" style="color:{s.color}">{s.value}</div>
              <div class="text-[10px] text-on-surface-variant/50 uppercase tracking-wider mt-0.5">{s.label}</div>
            </div>
          {/each}
        </div>

        <!-- Mini bar chart -->
        <div class="chart-area mt-5">
          <div class="chart-label">Vulnerabilities over last 7 scans</div>
          <div class="chart-bars">
            {#each [8, 14, 6, 20, 12, 9, 4] as h, i}
              <div class="chart-bar-wrap">
                <div class="chart-bar" style="height:{h * 4}px; animation-delay:{i * 80}ms"></div>
                <span class="chart-bar-val">{h}</span>
              </div>
            {/each}
          </div>
        </div>

        <div class="mt-4 text-center">
          <a href="/#login" class="cta-demo-btn">
            Start securing your code →
          </a>
        </div>
      </div>
    {/if}

  </div>

  <!-- Footer nav -->
  <div class="modal-footer">
    <button class="nav-btn" on:click={prev} disabled={current === 0}>
      <ChevronLeft class="w-4 h-4" /> Prev
    </button>

    <!-- Dot indicators -->
    <div class="flex items-center gap-1.5">
      {#each steps as s, i}
        <button
          class="dot {current === i ? 'dot-active' : ''}"
          style={current === i ? `background:${s.color}` : ''}
          on:click={() => goTo(i)}
          aria-label="Step {i + 1}"
        ></button>
      {/each}
    </div>

    {#if current < TOTAL - 1}
      <button class="nav-btn nav-btn-primary" on:click={next}>
        Next <ChevronRight class="w-4 h-4" />
      </button>
    {:else}
      <a href="/#login" class="nav-btn nav-btn-primary" on:click={close}>
        Get Started <Zap class="w-4 h-4" />
      </a>
    {/if}
  </div>

</div>
{/if}

<style>
  /* Backdrop */
  .modal-backdrop {
    position: fixed; inset: 0; z-index: 900;
    background: rgba(0,0,0,0.75);
    backdrop-filter: blur(6px);
    animation: fadeIn 0.2s ease;
  }

  /* Shell */
  .modal-shell {
    position: fixed; z-index: 901;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: min(92vw, 860px);
    max-height: 90vh;
    display: flex; flex-direction: column;
    border-radius: 1.25rem;
    border: 1px solid rgba(255,255,255,0.08);
    background: rgba(6,9,20,0.97);
    backdrop-filter: blur(24px);
    box-shadow: 0 40px 120px rgba(0,0,0,0.7), 0 0 0 1px rgba(0,217,255,0.06);
    animation: slideUp 0.25s cubic-bezier(0.34,1.56,0.64,1);
    overflow: hidden;
  }

  /* Header */
  .modal-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1rem 1.25rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    flex-shrink: 0;
  }

  .close-btn {
    width: 2rem; height: 2rem;
    display: flex; align-items: center; justify-content: center;
    border-radius: 0.5rem; border: 1px solid rgba(255,255,255,0.08);
    background: rgba(255,255,255,0.04); color: rgba(184,191,214,0.6);
    cursor: pointer; transition: all 0.15s;
  }
  .close-btn:hover { background: rgba(255,255,255,0.08); color: white; }

  .autoplay-btn {
    width: 2rem; height: 2rem;
    display: flex; align-items: center; justify-content: center;
    border-radius: 0.5rem; border: 1px solid rgba(0,217,255,0.2);
    background: rgba(0,217,255,0.07); color: #00d9ff;
    cursor: pointer; transition: all 0.15s;
  }
  .autoplay-btn:hover { background: rgba(0,217,255,0.14); }

  /* Progress */
  .progress-track {
    height: 2px; background: rgba(255,255,255,0.05); flex-shrink: 0;
  }
  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #00d9ff, #9d4edd);
    transition: width 0.4s ease;
  }

  /* Step tabs */
  .step-tabs {
    display: flex; gap: 0.25rem; padding: 0.75rem 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    overflow-x: auto; flex-shrink: 0;
    scrollbar-width: none;
  }
  .step-tabs::-webkit-scrollbar { display: none; }

  .step-tab {
    display: inline-flex; align-items: center; gap: 0.375rem;
    padding: 0.375rem 0.75rem; border-radius: 0.5rem;
    font-size: 0.75rem; font-weight: 500; white-space: nowrap;
    color: rgba(184,191,214,0.5); background: none;
    border: 1px solid transparent; cursor: pointer;
    transition: all 0.15s; flex-shrink: 0;
  }
  .step-tab:hover { color: white; background: rgba(255,255,255,0.04); }
  .step-tab-active {
    color: var(--tc, #00d9ff);
    background: color-mix(in srgb, var(--tc, #00d9ff) 12%, transparent);
    border-color: color-mix(in srgb, var(--tc, #00d9ff) 30%, transparent);
  }

  /* Slide area */
  .slide-area {
    flex: 1; overflow-y: auto; padding: 1.5rem;
    scrollbar-width: thin; scrollbar-color: rgba(0,217,255,0.2) transparent;
  }

  .slide-in {
    animation: slideIn 0.3s ease;
  }

  .slide-title {
    display: flex; align-items: center; gap: 0.625rem;
    font-size: 1.125rem; font-weight: 700; color: white;
    font-family: 'Space Grotesk', sans-serif;
    margin-bottom: 0.375rem;
  }

  .slide-sub {
    font-size: 0.875rem; color: rgba(184,191,214,0.6);
    line-height: 1.6; max-width: 560px;
  }

  /* Demo card */
  .demo-card {
    padding: 1.125rem; border-radius: 0.875rem;
    border: 1px solid rgba(255,255,255,0.07);
    background: rgba(255,255,255,0.02);
  }
  .demo-card-label {
    font-size: 0.65rem; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: rgba(184,191,214,0.5);
    margin-bottom: 0.625rem;
  }

  .url-input-demo {
    display: flex; align-items: center; gap: 0.625rem;
    padding: 0.625rem 0.875rem; border-radius: 0.625rem;
    border: 1px solid rgba(0,217,255,0.25); background: rgba(0,217,255,0.05);
  }

  /* Flow nodes */
  .flow-node {
    display: inline-flex; align-items: center; justify-content: center;
    padding: 0.375rem 0.875rem; border-radius: 0.5rem;
    font-size: 0.75rem; font-weight: 600; border: 1px solid;
  }
  .flow-node-cyan   { background: rgba(0,217,255,0.1);   border-color: rgba(0,217,255,0.3);   color: #00d9ff; }
  .flow-node-yellow { background: rgba(251,191,36,0.1);  border-color: rgba(251,191,36,0.3);  color: #fbbf24; }
  .flow-node-green  { background: rgba(52,211,153,0.1);  border-color: rgba(52,211,153,0.3);  color: #34d399; }
  .flow-arrow { color: rgba(255,255,255,0.3); font-size: 1rem; }

  .feature-chip {
    padding: 0.375rem 0.75rem; border-radius: 9999px;
    font-size: 0.7rem; font-weight: 500;
    background: rgba(0,217,255,0.07); border: 1px solid rgba(0,217,255,0.15);
    color: rgba(0,217,255,0.8);
  }

  /* Pipeline */
  .pipeline {
    display: flex; flex-direction: column; align-items: center; gap: 0.5rem;
    padding: 0.5rem 0;
  }
  .pipeline-node {
    padding: 0.375rem 1rem; border-radius: 0.5rem;
    font-size: 0.75rem; font-weight: 600; text-align: center;
  }
  .pipeline-start { background: rgba(0,217,255,0.1); border: 1px solid rgba(0,217,255,0.3); color: #00d9ff; }
  .pipeline-end   { background: rgba(52,211,153,0.1); border: 1px solid rgba(52,211,153,0.3); color: #34d399; }
  .pipeline-row   { display: flex; gap: 0.375rem; flex-wrap: wrap; justify-content: center; }
  .pipeline-tool  { background: rgba(157,78,221,0.1); border: 1px solid rgba(157,78,221,0.25); color: #9d4edd; font-size: 0.7rem; }
  .pipeline-arrow { color: rgba(255,255,255,0.2); font-size: 1.25rem; }

  /* Terminal mini */
  .terminal-mini {
    border-radius: 0.75rem; border: 1px solid rgba(0,217,255,0.12);
    background: rgba(4,6,16,0.9); overflow: hidden;
  }
  .terminal-mini-header {
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.5rem 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.05);
    background: rgba(255,255,255,0.02);
  }
  .terminal-mini-body {
    padding: 0.75rem; font-family: monospace; font-size: 0.7rem;
    max-height: 180px; overflow-y: auto; space-y: 0.25rem;
  }
  .log-line {
    display: flex; gap: 0.375rem; margin-bottom: 0.25rem;
    animation: fadeIn 0.2s ease;
  }

  /* Severity cards */
  .sev-card {
    padding: 1rem; border-radius: 0.75rem; border: 1px solid;
    text-align: center;
  }

  /* Vuln rows */
  .vuln-row {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.625rem 0.875rem; border-radius: 0.625rem; border: 1px solid;
  }
  .sev-badge {
    font-size: 0.65rem; font-weight: 700; padding: 0.15rem 0.5rem;
    border-radius: 0.25rem; border: 1px solid; flex-shrink: 0;
  }

  /* Code blocks */
  .code-block {
    border-radius: 0.75rem; border: 1px solid rgba(255,255,255,0.07);
    background: rgba(4,6,16,0.8); overflow: hidden;
  }
  .code-block-label {
    padding: 0.375rem 0.75rem; font-size: 0.65rem; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    background: rgba(255,255,255,0.02);
  }
  .code-pre {
    padding: 0.75rem; font-family: monospace; font-size: 0.7rem;
    line-height: 1.6; white-space: pre-wrap; word-break: break-all;
    margin: 0;
  }

  .confidence-bar-wrap { flex: 1; }
  .confidence-fill {
    width: 0;
    animation: growBar 1s ease 0.3s forwards;
  }

  /* PR preview */
  .pr-preview {
    border-radius: 0.875rem; border: 1px solid rgba(52,211,153,0.2);
    background: rgba(52,211,153,0.04); overflow: hidden;
  }
  .pr-preview-header {
    display: flex; align-items: center; gap: 0.625rem;
    padding: 0.75rem 1rem; border-bottom: 1px solid rgba(52,211,153,0.1);
    background: rgba(52,211,153,0.04);
  }
  .pr-preview-body { padding: 0.875rem 1rem; }
  .pr-badge {
    font-size: 0.65rem; font-weight: 600; padding: 0.15rem 0.5rem;
    border-radius: 9999px; background: rgba(251,191,36,0.15);
    color: #fbbf24; border: 1px solid rgba(251,191,36,0.3);
  }

  /* Dashboard stats */
  .dash-stat {
    padding: 1rem; border-radius: 0.75rem; border: 1px solid;
    background: rgba(255,255,255,0.02); text-align: center;
  }

  /* Chart */
  .chart-area {
    padding: 1rem; border-radius: 0.875rem;
    border: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.02);
  }
  .chart-label { font-size: 0.7rem; color: rgba(184,191,214,0.5); margin-bottom: 0.75rem; }
  .chart-bars { display: flex; align-items: flex-end; gap: 0.5rem; height: 80px; }
  .chart-bar-wrap { display: flex; flex-direction: column; align-items: center; gap: 0.25rem; flex: 1; }
  .chart-bar {
    width: 100%; border-radius: 0.25rem 0.25rem 0 0;
    background: linear-gradient(180deg, #00d9ff, #3a86ff);
    animation: growUp 0.6s ease both;
    min-height: 4px;
  }
  .chart-bar-val { font-size: 0.6rem; color: rgba(184,191,214,0.4); }

  .cta-demo-btn {
    display: inline-flex; align-items: center; gap: 0.5rem;
    padding: 0.75rem 1.75rem; border-radius: 0.75rem;
    font-size: 0.875rem; font-weight: 600; color: #060914;
    background: linear-gradient(135deg, #00d9ff, #3a86ff);
    text-decoration: none;
    transition: opacity 0.2s, transform 0.15s, box-shadow 0.3s;
    box-shadow: 0 4px 20px rgba(0,217,255,0.25);
  }
  .cta-demo-btn:hover { opacity: 0.9; transform: translateY(-1px); box-shadow: 0 8px 30px rgba(0,217,255,0.4); }

  /* Footer */
  .modal-footer {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.875rem 1.25rem;
    border-top: 1px solid rgba(255,255,255,0.05);
    flex-shrink: 0;
  }

  .nav-btn {
    display: inline-flex; align-items: center; gap: 0.375rem;
    padding: 0.5rem 1rem; border-radius: 0.625rem;
    font-size: 0.8125rem; font-weight: 500;
    color: rgba(184,191,214,0.7);
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    cursor: pointer; transition: all 0.15s; text-decoration: none;
  }
  .nav-btn:hover:not(:disabled) { background: rgba(255,255,255,0.08); color: white; }
  .nav-btn:disabled { opacity: 0.3; cursor: not-allowed; }
  .nav-btn-primary {
    background: linear-gradient(135deg, #00d9ff, #3a86ff);
    color: #060914; border-color: transparent; font-weight: 600;
  }
  .nav-btn-primary:hover:not(:disabled) { opacity: 0.9; }

  .dot {
    width: 0.5rem; height: 0.5rem; border-radius: 50%;
    background: rgba(255,255,255,0.15); border: none; cursor: pointer;
    transition: all 0.2s;
  }
  .dot:hover { background: rgba(255,255,255,0.35); }
  .dot-active { width: 1.25rem; border-radius: 9999px; }

  /* Animations */
  @keyframes fadeIn  { from { opacity: 0; } to { opacity: 1; } }
  @keyframes slideUp { from { opacity: 0; transform: translate(-50%, calc(-50% + 20px)); } to { opacity: 1; transform: translate(-50%, -50%); } }
  @keyframes slideIn { from { opacity: 0; transform: translateX(12px); } to { opacity: 1; transform: translateX(0); } }
  @keyframes growBar { from { width: 0; } to { width: 94%; } }
  @keyframes growUp  { from { height: 0 !important; } to { } }
</style>
