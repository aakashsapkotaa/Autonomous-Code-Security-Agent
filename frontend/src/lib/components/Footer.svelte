<script lang="ts">
  import { Shield } from 'lucide-svelte';
</script>

<footer class="relative z-20 w-full px-6 sm:px-10 py-6 border-t border-white/[0.05]">
  <div class="flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] text-on-surface-variant/50">

    <div class="flex items-center gap-2">
      <Shield class="w-3.5 h-3.5 text-neon-cyan/50" />
      <span class="font-semibold tracking-wide">SecureShift</span>
      <span class="text-white/20">·</span>
      <span>AI-Powered Security Scanner</span>
    </div>

    <div class="flex items-center gap-4">
      <span class="flex items-center gap-1.5">
        <span class="relative flex h-1.5 w-1.5">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-1.5 w-1.5 bg-green-400"></span>
        </span>
        All systems operational
      </span>
      <span class="text-white/10">|</span>
      <a href="/security-policy" class="hover:text-white/70 transition-colors">Privacy</a>
      <a href="/terms" class="hover:text-white/70 transition-colors">Terms</a>
    </div>

  </div>
</footer>
