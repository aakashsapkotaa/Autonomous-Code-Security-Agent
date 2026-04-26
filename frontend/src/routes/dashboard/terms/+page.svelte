<script lang="ts">
  import AuroraBackground from '$lib/components/AuroraBackground.svelte';
  import { FileText, ArrowLeft } from 'lucide-svelte';
</script>

<svelte:head><title>Terms of Service — SecureShift</title></svelte:head>

<div class="min-h-screen bg-[#060914]">
  <AuroraBackground />
  <div class="relative z-10 max-w-3xl mx-auto px-6 py-16">
    <a href="/dashboard" class="inline-flex items-center gap-2 text-sm text-on-surface-variant/60 hover:text-neon-cyan transition-colors mb-10">
      <ArrowLeft class="w-4 h-4" /> Back to Dashboard
    </a>

    <div class="flex items-center gap-3 mb-8">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-neon-purple/20 to-accent-1/10 border border-neon-purple/20 flex items-center justify-center">
        <FileText class="w-5 h-5 text-neon-purple" />
      </div>
      <div>
        <h1 class="text-2xl font-headline font-bold text-white">Terms of Service</h1>
        <p class="text-xs text-on-surface-variant/50 mt-0.5">Last updated: April 2026</p>
      </div>
    </div>

    <div class="space-y-8">
      {#each [
        { title: '1. Acceptance of Terms', body: 'By accessing and using SecureShift, you accept and agree to be bound by the terms and provision of this agreement. If you do not agree to abide by these terms, please do not use this service.' },
        { title: '2. Use of Service', body: 'SecureShift is a security scanning platform. You may use it only for lawful purposes and in accordance with these Terms. You agree not to use the service to scan repositories you do not own or have explicit permission to scan.' },
        { title: '3. Account Responsibility', body: 'You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account. Notify us immediately of any unauthorized use.' },
        { title: '4. Intellectual Property', body: 'The service and its original content, features, and functionality are and will remain the exclusive property of SecureShift. Our service is protected by copyright, trademark, and other laws.' },
        { title: '5. Limitation of Liability', body: 'SecureShift shall not be liable for any indirect, incidental, special, consequential or punitive damages resulting from your use of the service. Security scanning results are provided as-is and should be verified by qualified security professionals.' },
        { title: '6. Changes to Terms', body: 'We reserve the right to modify these terms at any time. We will notify users of significant changes via email or a prominent notice on our platform.' },
        { title: '7. Contact', body: 'Questions about the Terms of Service should be sent to legal@secureshift.io.' },
      ] as section}
        <div>
          <h2 class="text-base font-semibold text-white mb-2">{section.title}</h2>
          <p class="text-sm text-on-surface-variant/70 leading-relaxed">{section.body}</p>
        </div>
      {/each}
    </div>
  </div>
</div>
