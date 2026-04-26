<script lang="ts">
  import {
    Shield, Zap, GitPullRequest, Search,
    Bot, Lock, FileCode, Bell
  } from 'lucide-svelte';

  const features = [
    {
      icon: Search,
      color: 'cyan',
      title: 'Multi-Tool Scanning',
      description:
        'Runs Bandit, TruffleHog, and Safety in parallel — catching code vulnerabilities, exposed secrets, and vulnerable dependencies in a single pass.',
      tags: ['Bandit', 'TruffleHog', 'Safety'],
    },
    {
      icon: Bot,
      color: 'purple',
      title: 'AI-Generated Fixes',
      description:
        'Every vulnerability gets an AI-written code fix via OpenRouter. Each fix includes a confidence score and a plain-English explanation of the change.',
      tags: ['OpenRouter', 'Confidence Score', 'Auto-patch'],
    },
    {
      icon: GitPullRequest,
      color: 'pink',
      title: 'Automated PR Agent',
      description:
        'After fixes are generated, the PR Agent clones your repo, applies patches to the right files, and opens a Draft Pull Request on GitHub — zero manual steps.',
      tags: ['GitHub API', 'Draft PR', 'Auto-branch'],
    },
    {
      icon: Shield,
      color: 'blue',
      title: 'CVE Lookup Engine',
      description:
        'Parses requirements.txt, package.json, Pipfile, and poetry.lock then cross-references every dependency against OSV.dev and the NVD 2.0 database.',
      tags: ['OSV.dev', 'NVD API', 'CVSS Scores'],
    },
    {
      icon: FileCode,
      color: 'cyan',
      title: 'Dependency Intelligence',
      description:
        'Identifies outdated and vulnerable packages across Python and Node ecosystems. Shows fix versions so you know exactly what to upgrade to.',
      tags: ['PyPI', 'npm', 'Fix Versions'],
    },
    {
      icon: Lock,
      color: 'purple',
      title: 'Supabase Auth & RLS',
      description:
        'Email/password auth with Supabase. Every table is protected by Row Level Security — users can only ever see their own repositories and scan results.',
      tags: ['Supabase Auth', 'RLS', 'SOC 2 Ready'],
    },
    {
      icon: Zap,
      color: 'pink',
      title: 'Real-time Dashboard',
      description:
        'Live scan status, animated vulnerability counters, severity breakdowns, and a recent activity timeline — all updating without a page refresh.',
      tags: ['Live Updates', 'Severity Triage', 'Timeline'],
    },
    {
      icon: Bell,
      color: 'blue',
      title: 'Scan Logs & Audit Trail',
      description:
        'Every scan step is logged to Supabase with timestamps and severity levels, giving you a full audit trail for compliance and debugging.',
      tags: ['Audit Trail', 'Compliance', 'Timestamped'],
    },
  ];

  const colorMap: Record<string, { icon: string; tag: string; glow: string; border: string }> = {
    cyan:   { icon: '#00d9ff', tag: 'rgba(0,217,255,0.12)',   glow: 'rgba(0,217,255,0.15)',   border: 'rgba(0,217,255,0.2)'   },
    purple: { icon: '#9d4edd', tag: 'rgba(157,78,221,0.12)',  glow: 'rgba(157,78,221,0.15)',  border: 'rgba(157,78,221,0.2)'  },
    pink:   { icon: '#ff006e', tag: 'rgba(255,0,110,0.12)',   glow: 'rgba(255,0,110,0.15)',   border: 'rgba(255,0,110,0.2)'   },
    blue:   { icon: '#3a86ff', tag: 'rgba(58,134,255,0.12)',  glow: 'rgba(58,134,255,0.15)',  border: 'rgba(58,134,255,0.2)'  },
  };
</script>

<section id="features" class="relative z-10 w-full px-6 sm:px-10 lg:px-16 py-20 sm:py-28">
  <div class="max-w-7xl mx-auto">

    <!-- Section header -->
    <div class="text-center mb-14">
      <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-neon-cyan/20 bg-neon-cyan/5 mb-5">
        <span class="w-1.5 h-1.5 rounded-full bg-neon-cyan animate-pulse"></span>
        <span class="text-[11px] font-semibold uppercase tracking-[0.2em] text-neon-cyan/80">
          Platform Capabilities
        </span>
      </div>
      <h2 class="text-3xl sm:text-4xl lg:text-5xl font-headline font-bold text-white leading-tight">
        Everything you need to<br />
        <span class="bg-gradient-to-r from-neon-cyan via-neon-blue to-neon-purple bg-clip-text text-transparent">
          ship secure code
        </span>
      </h2>
      <p class="mt-4 text-base text-on-surface-variant/60 max-w-xl mx-auto leading-relaxed">
        SecureShift combines static analysis, secret detection, dependency auditing,
        and AI-powered remediation into one automated pipeline.
      </p>
    </div>

    <!-- Feature grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {#each features as f, i}
        {@const c = colorMap[f.color]}
        <div
          class="feature-card"
          style="animation-delay:{i * 60}ms"
        >
          <!-- Icon -->
          <div
            class="feature-icon-wrap"
            style="background:{c.tag}; border-color:{c.border}"
          >
            <svelte:component this={f.icon} class="w-5 h-5" style="color:{c.icon}" />
          </div>

          <!-- Text -->
          <h3 class="text-sm font-semibold text-white mt-4 mb-2 leading-snug">
            {f.title}
          </h3>
          <p class="text-xs text-on-surface-variant/60 leading-relaxed flex-1">
            {f.description}
          </p>

          <!-- Tags -->
          <div class="flex flex-wrap gap-1.5 mt-4">
            {#each f.tags as tag}
              <span
                class="tag"
                style="background:{c.tag}; color:{c.icon}; border-color:{c.border}"
              >
                {tag}
              </span>
            {/each}
          </div>

          <!-- Hover glow -->
          <div class="feature-glow" style="background:{c.glow}"></div>
        </div>
      {/each}
    </div>

    <!-- Bottom CTA strip -->
    <div class="mt-16 flex flex-col sm:flex-row items-center justify-center gap-4 text-sm">
      <a
        href="/#login"
        class="cta-btn"
      >
        Start scanning for free
      </a>
      <span class="text-on-surface-variant/40 text-xs">
        No credit card · Free tier available · Supabase-powered
      </span>
    </div>

  </div>
</section>

<style>
  .feature-card {
    position: relative;
    display: flex;
    flex-direction: column;
    padding: 1.375rem;
    border-radius: 1rem;
    border: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.02);
    backdrop-filter: blur(12px);
    overflow: hidden;
    animation: fadeUp 0.5s ease both;
    transition: border-color 0.25s, transform 0.2s;
  }
  .feature-card:hover {
    border-color: rgba(255,255,255,0.12);
    transform: translateY(-2px);
  }
  .feature-card:hover .feature-glow {
    opacity: 1;
  }

  .feature-icon-wrap {
    width: 2.5rem; height: 2.5rem;
    border-radius: 0.75rem;
    border: 1px solid;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }

  .tag {
    display: inline-flex;
    align-items: center;
    padding: 0.2rem 0.5rem;
    border-radius: 9999px;
    font-size: 0.65rem;
    font-weight: 600;
    border: 1px solid;
    letter-spacing: 0.02em;
  }

  .feature-glow {
    position: absolute;
    bottom: -40px; right: -40px;
    width: 120px; height: 120px;
    border-radius: 50%;
    filter: blur(40px);
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.3s;
  }

  .cta-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.75rem;
    border-radius: 0.75rem;
    font-weight: 600;
    font-size: 0.875rem;
    color: #060914;
    background: linear-gradient(135deg, #00d9ff, #3a86ff);
    transition: opacity 0.2s, transform 0.15s, box-shadow 0.3s;
    box-shadow: 0 4px 20px rgba(0,217,255,0.2);
    text-decoration: none;
  }
  .cta-btn:hover {
    opacity: 0.92;
    transform: translateY(-1px);
    box-shadow: 0 8px 30px rgba(0,217,255,0.35);
  }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
  }
</style>
