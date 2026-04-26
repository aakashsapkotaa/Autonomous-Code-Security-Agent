<script lang="ts">
  let className = '';
  export { className as class };

  let isHovered = false;
  let mouseX = 0;
  let mouseY = 0;

  function handleMouseMove(e: MouseEvent) {
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    mouseX = e.clientX - rect.left;
    mouseY = e.clientY - rect.top;
  }
</script>

<div
  on:mouseenter={() => isHovered = true}
  on:mouseleave={() => isHovered = false}
  on:mousemove={handleMouseMove}
  class="relative overflow-hidden rounded-2xl border backdrop-blur-2xl transition-all duration-300
    {isHovered
      ? 'bg-white/10 border-white/[0.24] shadow-[0_18px_44px_-26px_rgba(255,255,255,0.16)]'
      : 'bg-white/[0.06] border-white/10 shadow-[0_18px_44px_-30px_rgba(255,255,255,0.1)]'}
    {className}"
  role="presentation"
>
  <div class="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-br from-white/[0.1] via-white/[0.025] to-transparent"></div>

  {#if isHovered}
    <div
      class="pointer-events-none absolute h-40 w-40 rounded-full bg-white/10 blur-3xl transition-all duration-300"
      style="top: {mouseY - 80}px; left: {mouseX - 80}px;"
    ></div>
    <div class="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-br from-white/[0.18] via-transparent to-transparent"></div>
  {/if}

  <div class="relative z-10">
    <slot />
  </div>
</div>
