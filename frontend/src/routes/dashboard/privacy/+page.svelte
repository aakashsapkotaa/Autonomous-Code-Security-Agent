<script lang="ts">
  import AuroraBackground from '$lib/components/AuroraBackground.svelte';
  import { Shield, ArrowLeft } from 'lucide-svelte';
</script>

<svelte:head><title>Privacy Policy — SecureShift</title></svelte:head>

<div class="min-h-screen bg-[#060914]">
  <AuroraBackground />
  <div class="relative z-10 max-w-3xl mx-auto px-6 py-16">
    <a href="/dashboard" class="inline-flex items-center gap-2 text-sm text-on-surface-variant/60 hover:text-neon-cyan transition-colors mb-10">
      <ArrowLeft class="w-4 h-4" /> Back to Dashboard
    </a>

    <div class="flex items-center gap-3 mb-8">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-neon-cyan/20 to-neon-blue/10 border border-neon-cyan/20 flex items-center justify-center">
        <Shield class="w-5 h-5 text-neon-cyan" />
      </div>
      <div>
        <h1 class="text-2xl font-headline font-bold text-white">Privacy Policy</h1>
        <p class="text-xs text-on-surface-variant/50 mt-0.5">Last updated: April 2026</p>
      </div>
    </div>

    <div class="space-y-8">
      {#each [
        { title: '1. Information We Collect', body: 'We collect information you provide directly to us, such as your email address and repository URLs when you create an account or connect a repository. We also collect usage data to improve our service.' },
        { title: '2. How We Use Your Information', body: 'We use the information we collect to provide, maintain, and improve our services, process security scans on your repositories, send you technical notices and support messages, and respond to your comments and questions.' },
        { title: '3. Data Storage', body: 'Your data is stored securely using Supabase PostgreSQL with row-level security policies. We do not sell, trade, or otherwise transfer your personally identifiable information to outside parties.' },
        { title: '4. Repository Access', body: 'SecureShift only accesses repository code for the purpose of security scanning. We do not store your source code permanently — scan results and vulnerability metadata are stored, not the code itself.' },
        { title: '5. Security', body: 'We implement industry-standard security measures including TLS encryption in transit, AES-256 encryption at rest, and regular security audits of our own platform.' },
        { title: '6. Contact', body: 'If you have any questions about this Privacy Policy, please contact us at privacy@secureshift.io.' },
      ] as section}
        <div>
          <h2 class="text-base font-semibold text-white mb-2">{section.title}</h2>
          <p class="text-sm text-on-surface-variant/70 leading-relaxed">{section.body}</p>
        </div>
      {/each}
    </div>
  </div>
</div>
