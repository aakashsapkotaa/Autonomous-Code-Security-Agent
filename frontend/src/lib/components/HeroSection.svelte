<script lang="ts">
  import { Shield, Zap, GitBranch, Lock, TrendingUp, Eye } from 'lucide-svelte';
  import DemoModal from './DemoModal.svelte';

  let demoOpen = false;

  const stats = [
    { value: '99.9%', label: 'Detection Rate', icon: Eye,       color: 'cyan'   },
    { value: '24/7',  label: 'Monitoring',     icon: Shield,    color: 'purple' },
    { value: '<2min', label: 'Scan Speed',     icon: Zap,       color: 'pink'   },
  ];

  const trust = [
    { label: 'SOC 2 Ready'   },
    { label: 'OWASP Aligned' },
    { label: 'CVE Database'  },
  ];

  // Fake scan preview lines
  const scanLines = [
    { type: 'info',  text: 'Initializing Bandit static analysis...' },
    { type: 'warn',  text: 'HIGH  SQL injection risk — db/queries.py:42' },
    { type: 'error', text: 'CRIT  Hardcoded secret detected — config.py:17' },
    { type: 'warn',  text: 'MED   Insecure deserialization — api/views.py:88' },
    { type: 'ok',    text: 'TruffleHog scan complete — 1 secret found' },
    { type: 'info',  text: 'Running Safety dependency check...' },
    { type: 'warn',  text: 'HIGH  CVE-2024-3094 in requests==2.28.0' },
    { type: 'ok',    text: 'AI fix generated — confidence 94%' },
  ];
</script>

<div class="space-y-8 max-w-2xl relative z-10">

  <!-- Status badge -->
  <div class="inline-flex items-center gap-2.5 px-4 py-2 rounded-full border border-neon-cyan/30 bg-neon-cyan/5 backdrop-blur-sm">
    <span class="relative flex h-2 w-2">
      <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-neon-cyan opacity-75"></span>
      <span class="relative inline-flex rounded-full h-2 w-2 bg-neon-cyan"></span>
    </span>
    <span class="text-[11px] font-semibold uppercase tracking-[0.2em] text-neon-cyan">
      AI Security Engine · Active
    </span>
  </div>

  <!-- Heading -->
  <div class="space-y-4">
    <h1 class="text-5xl sm:text-6xl lg:text-[4.5rem] font-headline font-bold leading-[1.05] tracking-tight">
      <span class="text-white">Secure Your</span><br />
      <span class="bg-gradient-to-r from-neon-cyan via-neon-blue to-neon-purple bg-clip-text text-transparent">
        Code at Scale
      </span>
    </h1>
    <p class="text-base sm:text-lg text-on-surface-variant leading-relaxed max-w-md font-light">
      Autonomous vulnerability detection across your GitHub repositories.
      AI-generated fixes. Zero noise.
    </p>
  </div>

  <!-- CTA -->
  <div class="flex flex-wrap items-center gap-4">
    <a href="/#login"
      class="cta-primary group relative inline-flex items-center gap-2.5 px-7 py-3.5 rounded-xl font-semibold text-sm text-dark-bg overflow-hidden">
      <span class="relative z-10 flex items-center gap-2">
        Start Free Scan
        <Zap class="w-4 h-4 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
      </span>
    </a>
    <button
      on:click={() => demoOpen = true}
      class="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl font-semibold text-sm text-on-surface-variant border border-white/10 hover:border-white/20 hover:text-white transition-all duration-200 backdrop-blur-sm">
      <GitBranch class="w-4 h-4" />
      See how it works
    </button>
  </div>

  <DemoModal open={demoOpen} on:close={() => demoOpen = false} />

  <!-- Trust badges -->
  <div class="flex flex-wrap items-center gap-3 pt-1">
    {#each trust as t}
      <span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/[0.04] border border-white/[0.08] text-[11px] font-medium text-on-surface-variant">
        <Lock class="w-3 h-3 text-neon-cyan/70" />
        {t.label}
      </span>
    {/each}
  </div>

  <!-- Stats row -->
  <div class="grid grid-cols-3 gap-3 pt-2">
    {#each stats as s, i}
      <div class="stat-card stat-{s.color}" style="animation-delay: {i * 120}ms">
        <svelte:component this={s.icon} class="w-4 h-4 stat-icon-{s.color} mb-2" />
        <div class="text-2xl sm:text-3xl font-headline font-bold stat-value-{s.color}">{s.value}</div>
        <div class="text-[10px] font-semibold uppercase tracking-wider text-on-surface-variant mt-0.5">{s.label}</div>
      </div>
    {/each}
  </div>

  <!-- Scan preview terminal -->
  <div class="terminal-card hidden lg:block">
    <div class="terminal-header">
      <div class="flex gap-1.5">
        <span class="w-3 h-3 rounded-full bg-[#ff5f57]"></span>
        <span class="w-3 h-3 rounded-full bg-[#febc2e]"></span>
        <span class="w-3 h-3 rounded-full bg-[#28c840]"></span>
      </div>
      <span class="text-[11px] text-on-surface-variant font-mono">secureshift · scan · main</span>
      <span class="text-[10px] text-neon-cyan/60 font-mono">● live</span>
    </div>
    <div class="terminal-body font-mono text-[11px] space-y-1.5">
      {#each scanLines as line, i}
        <div class="terminal-line" style="animation-delay: {i * 300}ms">
          {#if line.type === 'error'}
            <span class="text-red-400">▶</span>
            <span class="text-red-400/90">{line.text}</span>
          {:else if line.type === 'warn'}
            <span class="text-yellow-400">▶</span>
            <span class="text-yellow-400/80">{line.text}</span>
          {:else if line.type === 'ok'}
            <span class="text-neon-cyan">✓</span>
            <span class="text-neon-cyan/80">{line.text}</span>
          {:else}
            <span class="text-on-surface-variant/40">$</span>
            <span class="text-on-surface-variant/70">{line.text}</span>
          {/if}
        </div>
      {/each}
      <div class="flex items-center gap-1 pt-1">
        <span class="text-on-surface-variant/40">$</span>
        <span class="w-2 h-3.5 bg-neon-cyan/80 animate-pulse inline-block"></span>
      </div>
    </div>
  </div>

</div>

<style>
  .cta-primary {
    background: linear-gradient(135deg, #00d9ff, #3a86ff);
    box-shadow: 0 0 0 0 rgba(0, 217, 255, 0.4);
    transition: box-shadow 0.3s ease, transform 0.2s ease;
  }
  .cta-primary:hover {
    box-shadow: 0 0 30px rgba(0, 217, 255, 0.35), 0 0 60px rgba(0, 217, 255, 0.15);
    transform: translateY(-1px);
  }
  .cta-primary:active { transform: translateY(0); }

  .stat-card {
    padding: 1rem;
    border-radius: 0.875rem;
    border: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(12px);
    animation: fadeUp 0.5s ease both;
    transition: border-color 0.2s, background 0.2s;
  }
  .stat-card:hover { background: rgba(255,255,255,0.05); }

  .stat-cyan:hover   { border-color: rgba(0,217,255,0.25); }
  .stat-purple:hover { border-color: rgba(157,78,221,0.25); }
  .stat-pink:hover   { border-color: rgba(247,37,133,0.25); }

  .stat-icon-cyan   { color: #00d9ff; }
  .stat-icon-purple { color: #9d4edd; }
  .stat-icon-pink   { color: #ff006e; }

  .stat-value-cyan   { background: linear-gradient(135deg, #00d9ff, #3a86ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
  .stat-value-purple { background: linear-gradient(135deg, #9d4edd, #c77dff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
  .stat-value-pink   { background: linear-gradient(135deg, #ff006e, #f72585); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }

  .terminal-card {
    border-radius: 1rem;
    border: 1px solid rgba(0, 217, 255, 0.12);
    background: rgba(6, 9, 20, 0.8);
    backdrop-filter: blur(20px);
    overflow: hidden;
    box-shadow: 0 0 0 1px rgba(0,217,255,0.05), 0 20px 60px rgba(0,0,0,0.4);
  }

  .terminal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    background: rgba(255,255,255,0.02);
  }

  .terminal-body {
    padding: 1rem;
    max-height: 180px;
    overflow: hidden;
  }

  .terminal-line {
    display: flex;
    gap: 0.5rem;
    opacity: 0;
    animation: fadeIn 0.3s ease forwards;
  }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateX(-4px); }
    to   { opacity: 1; transform: translateX(0); }
  }
</style>
