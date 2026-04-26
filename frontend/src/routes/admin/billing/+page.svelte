<script lang="ts">
  import { Check, CreditCard, Zap, Building2 } from 'lucide-svelte';

  const PLANS = [
    {
      name: 'Free',
      price: '$0',
      period: '/mo',
      icon: Zap,
      color: '#94a3b8',
      accent: 'rgba(148,163,184,0.15)',
      border: 'rgba(148,163,184,0.2)',
      features: [
        '1 repository',
        '5 scans per month',
        'Basic vulnerability detection',
        'Community support',
        '7-day scan history',
      ],
    },
    {
      name: 'Pro',
      price: '$29',
      period: '/mo',
      icon: CreditCard,
      color: '#00d9ff',
      accent: 'rgba(0,217,255,0.08)',
      border: 'rgba(0,217,255,0.25)',
      popular: true,
      features: [
        'Unlimited repositories',
        'Unlimited scans',
        'AI-powered fix suggestions',
        'Auto PR creation',
        'Priority support',
        '90-day scan history',
        'CVE enrichment',
      ],
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      period: '',
      icon: Building2,
      color: '#9d4edd',
      accent: 'rgba(157,78,221,0.08)',
      border: 'rgba(157,78,221,0.25)',
      features: [
        'Everything in Pro',
        'SSO / SAML',
        'Custom integrations',
        'Dedicated support',
        'SLA guarantee',
        'On-premise option',
        'Audit logs & compliance',
      ],
    },
  ];
</script>

<svelte:head><title>Billing — Admin</title></svelte:head>

<div class="space-y-6">
  <div>
    <h1 class="text-xl font-bold text-white">Billing &amp; Subscriptions</h1>
    <p class="text-xs text-muted mt-0.5">Manage plans and subscription tiers</p>
  </div>

  <div class="stripe-note">
    <CreditCard class="w-4 h-4 text-[#00d9ff]" />
    <span>Stripe integration coming soon — billing features are not yet active.</span>
  </div>

  <div class="plans-grid">
    {#each PLANS as plan}
      <div class="plan-card" style="border-color:{plan.border}; background:{plan.accent}">
        {#if plan.popular}
          <div class="popular-badge">Most Popular</div>
        {/if}

        <div class="plan-header">
          <div class="plan-icon" style="background:{plan.color}15; color:{plan.color}; border-color:{plan.color}30">
            <svelte:component this={plan.icon} class="w-5 h-5" />
          </div>
          <div>
            <h2 class="text-base font-bold text-white">{plan.name}</h2>
            <div class="flex items-baseline gap-0.5 mt-0.5">
              <span class="text-2xl font-bold" style="color:{plan.color}">{plan.price}</span>
              {#if plan.period}
                <span class="text-xs text-muted">{plan.period}</span>
              {/if}
            </div>
          </div>
        </div>

        <ul class="feature-list">
          {#each plan.features as feat}
            <li class="feature-item">
              <Check class="w-3.5 h-3.5 flex-shrink-0" style="color:{plan.color}" />
              <span class="text-xs text-on-surface">{feat}</span>
            </li>
          {/each}
        </ul>

        <div class="coming-soon-btn" style="color:{plan.color}; border-color:{plan.color}30; background:{plan.color}08">
          Coming Soon
        </div>
      </div>
    {/each}
  </div>

  <p class="text-xs text-muted text-center">
    All plans include SSL encryption, GDPR compliance, and 99.9% uptime SLA.
  </p>
</div>

<style>
  .text-muted { color: rgba(184,191,214,0.5); }
  .text-on-surface { color: rgba(184,191,214,0.75); }

  .stripe-note {
    display: flex; align-items: center; gap: 0.625rem;
    padding: 0.75rem 1rem; border-radius: 0.75rem;
    background: rgba(0,217,255,0.05); border: 1px solid rgba(0,217,255,0.15);
    font-size: 0.8125rem; color: rgba(184,191,214,0.7);
  }

  .plans-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; }

  .plan-card {
    position: relative; padding: 1.5rem; border-radius: 1rem;
    border: 1px solid; display: flex; flex-direction: column; gap: 1.25rem;
    transition: transform 0.2s;
  }
  .plan-card:hover { transform: translateY(-2px); }

  .popular-badge {
    position: absolute; top: -0.625rem; left: 50%; transform: translateX(-50%);
    padding: 0.2rem 0.75rem; border-radius: 9999px;
    font-size: 0.65rem; font-weight: 700; letter-spacing: 0.05em;
    background: linear-gradient(135deg, #00d9ff, #3a86ff);
    color: #060914; white-space: nowrap;
  }

  .plan-header { display: flex; align-items: center; gap: 0.875rem; }

  .plan-icon {
    width: 3rem; height: 3rem; border-radius: 0.75rem;
    display: flex; align-items: center; justify-content: center;
    border: 1px solid; flex-shrink: 0;
  }

  .feature-list { display: flex; flex-direction: column; gap: 0.5rem; flex: 1; }
  .feature-item { display: flex; align-items: center; gap: 0.5rem; }

  .coming-soon-btn {
    display: flex; align-items: center; justify-content: center;
    padding: 0.625rem; border-radius: 0.625rem;
    font-size: 0.8125rem; font-weight: 600;
    border: 1px solid; letter-spacing: 0.03em;
  }
</style>
