<script lang="ts">
  import { onMount } from 'svelte';

  let mounted = false;
  onMount(() => { mounted = true; });
</script>

<!-- Static deep background — uses CSS var so it responds to theme -->
<div class="fixed inset-0 z-0 theme-bg-page"></div>

<!-- Aurora orbs — pure CSS, zero JS, zero clutter -->
{#if mounted}
  <div class="fixed inset-0 z-0 overflow-hidden pointer-events-none aurora-container" aria-hidden="true">
    <!-- Primary cyan orb -->
    <div class="aurora-orb aurora-1"></div>
    <!-- Purple orb -->
    <div class="aurora-orb aurora-2"></div>
    <!-- Pink accent orb -->
    <div class="aurora-orb aurora-3"></div>
    <!-- Blue deep orb -->
    <div class="aurora-orb aurora-4"></div>

    <!-- Subtle grid overlay -->
    <div class="absolute inset-0 cyber-grid opacity-[0.03]"></div>

    <!-- Scanline sweep -->
    <div class="scanline"></div>
  </div>
{/if}

<style>
  .aurora-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    will-change: transform, opacity;
  }

  .aurora-1 {
    width: 700px; height: 700px;
    top: -200px; left: -150px;
    background: radial-gradient(circle, rgba(0, 217, 255, 0.18) 0%, rgba(0, 217, 255, 0.04) 60%, transparent 100%);
    animation: drift1 18s ease-in-out infinite;
  }

  .aurora-2 {
    width: 600px; height: 600px;
    bottom: -100px; right: -100px;
    background: radial-gradient(circle, rgba(157, 78, 221, 0.2) 0%, rgba(157, 78, 221, 0.05) 60%, transparent 100%);
    animation: drift2 22s ease-in-out infinite;
  }

  .aurora-3 {
    width: 400px; height: 400px;
    top: 40%; left: 50%;
    background: radial-gradient(circle, rgba(247, 37, 133, 0.1) 0%, rgba(247, 37, 133, 0.02) 60%, transparent 100%);
    animation: drift3 16s ease-in-out infinite;
  }

  .aurora-4 {
    width: 500px; height: 500px;
    top: 20%; right: 20%;
    background: radial-gradient(circle, rgba(58, 134, 255, 0.12) 0%, rgba(58, 134, 255, 0.03) 60%, transparent 100%);
    animation: drift4 20s ease-in-out infinite;
  }

  @keyframes drift1 {
    0%, 100% { transform: translate(0, 0) scale(1); }
    33%       { transform: translate(60px, 80px) scale(1.1); }
    66%       { transform: translate(-40px, 40px) scale(0.95); }
  }
  @keyframes drift2 {
    0%, 100% { transform: translate(0, 0) scale(1); }
    33%       { transform: translate(-80px, -60px) scale(1.05); }
    66%       { transform: translate(50px, -30px) scale(1.1); }
  }
  @keyframes drift3 {
    0%, 100% { transform: translate(-50%, -50%) scale(1); }
    50%       { transform: translate(-50%, -50%) scale(1.3) rotate(20deg); }
  }
  @keyframes drift4 {
    0%, 100% { transform: translate(0, 0) scale(1); }
    40%       { transform: translate(-60px, 50px) scale(0.9); }
    80%       { transform: translate(40px, -40px) scale(1.1); }
  }

  .cyber-grid {
    background-image:
      linear-gradient(rgba(0, 217, 255, 1) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0, 217, 255, 1) 1px, transparent 1px);
    background-size: 60px 60px;
  }

  .scanline {
    position: absolute;
    top: -100%;
    left: 0;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(0, 217, 255, 0.15), transparent);
    animation: scan 8s linear infinite;
  }

  @keyframes scan {
    0%   { top: -2px; opacity: 0; }
    5%   { opacity: 1; }
    95%  { opacity: 1; }
    100% { top: 100%; opacity: 0; }
  }
</style>
