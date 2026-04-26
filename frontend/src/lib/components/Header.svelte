<script lang="ts">
  import { Shield, Bot, Sparkles } from 'lucide-svelte';
  import HelpBot from './HelpBot.svelte';

  let botOpen = false;
</script>

<header class="relative z-20 w-full flex justify-between items-center px-6 sm:px-10 py-5">

  <!-- Brand -->
  <a href="/" class="flex items-center gap-3 group">
    <div class="relative w-9 h-9 flex items-center justify-center rounded-xl bg-gradient-to-br from-neon-cyan/20 to-neon-blue/10 border border-neon-cyan/20 group-hover:border-neon-cyan/40 transition-all duration-300">
      <Shield class="w-4.5 h-4.5 text-neon-cyan" />
      <div class="absolute inset-0 rounded-xl bg-neon-cyan/10 opacity-0 group-hover:opacity-100 blur-sm transition-opacity duration-300"></div>
    </div>
    <span class="text-xl font-headline font-bold tracking-tight">
      <span class="text-white">Secure</span><span class="bg-gradient-to-r from-neon-cyan to-neon-blue bg-clip-text text-transparent">Shift</span>
    </span>
  </a>

  <!-- Nav + Bot -->
  <div class="flex items-center gap-3">
    <nav class="hidden sm:flex items-center gap-1 text-sm text-on-surface-variant">
      <a href="/#features"  class="px-3 py-1.5 rounded-lg hover:text-white hover:bg-white/5 transition-all duration-200">Features</a>
      <a href="/privacy"    class="px-3 py-1.5 rounded-lg hover:text-white hover:bg-white/5 transition-all duration-200">Privacy</a>
      <a href="/terms"      class="px-3 py-1.5 rounded-lg hover:text-white hover:bg-white/5 transition-all duration-200">Terms</a>
    </nav>

    <div class="w-px h-5 bg-white/10 hidden sm:block"></div>

    <button
      type="button"
      on:click={() => botOpen = !botOpen}
      class="flex items-center gap-2 px-3.5 py-2 rounded-xl border border-white/10 bg-white/[0.04] hover:bg-white/[0.07] hover:border-white/20 transition-all duration-200 text-sm text-on-surface-variant hover:text-white"
    >
      <Bot class="w-4 h-4 text-neon-cyan" />
      <span class="hidden sm:inline font-medium">AI Help</span>
      <Sparkles class="w-3 h-3 text-neon-purple/70" />
    </button>

    <HelpBot open={botOpen} onClose={() => botOpen = false} />
  </div>
</header>
