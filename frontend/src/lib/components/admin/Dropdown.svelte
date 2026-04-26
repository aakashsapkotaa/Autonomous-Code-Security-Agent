<script lang="ts">
  import { onMount } from 'svelte';
  import { ChevronDown } from 'lucide-svelte';

  export let value: string | number = '';
  export let options: { value: string | number; label: string }[] = [];
  export let onChange: (v: string | number) => void = () => {};

  let open = false;

  $: selected = options.find(o => o.value === value)?.label ?? String(value);

  function pick(v: string | number) {
    value = v;
    open = false;
    onChange(v);
  }

  function handleOutside(e: MouseEvent) {
    const el = (e.target as HTMLElement).closest('.dd-wrap');
    if (!el) open = false;
  }

  onMount(() => {
    window.addEventListener('click', handleOutside);
    return () => window.removeEventListener('click', handleOutside);
  });
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-static-element-interactions -->
<div class="dd-wrap" on:click|stopPropagation={() => (open = !open)}>
  <span class="dd-label">{selected}</span>
  <ChevronDown class="dd-chevron {open ? 'open' : ''}" />

  {#if open}
    <div class="dd-menu">
      {#each options as opt}
        <button
          class="dd-item {value === opt.value ? 'dd-item-active' : ''}"
          on:click|stopPropagation={() => pick(opt.value)}
        >
          {opt.label}
        </button>
      {/each}
    </div>
  {/if}
</div>

<style>
  .dd-wrap {
    position: relative;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.375rem 0.75rem;
    border-radius: 0.625rem;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(255, 255, 255, 0.04);
    color: #f0f4ff;
    font-size: 0.8125rem;
    cursor: pointer;
    user-select: none;
    min-width: 130px;
    transition: border-color 0.15s, background 0.15s;
  }
  .dd-wrap:hover {
    border-color: rgba(255, 255, 255, 0.15);
    background: rgba(255, 255, 255, 0.07);
  }

  .dd-label { flex: 1; white-space: nowrap; }

  :global(.dd-chevron) {
    width: 0.75rem;
    height: 0.75rem;
    opacity: 0.5;
    flex-shrink: 0;
    transition: transform 0.2s;
  }
  :global(.dd-chevron.open) { transform: rotate(180deg); }

  .dd-menu {
    position: absolute;
    top: calc(100% + 6px);
    left: 0;
    z-index: 500;
    min-width: 100%;
    background: #0d1117;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 0.625rem;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.75);
    padding: 0.25rem;
    overflow: hidden;
  }

  .dd-item {
    display: block;
    width: 100%;
    text-align: left;
    padding: 0.5rem 0.75rem;
    border-radius: 0.375rem;
    font-size: 0.8125rem;
    color: rgba(184, 191, 214, 0.8);
    background: none;
    border: none;
    cursor: pointer;
    transition: background 0.12s, color 0.12s;
    white-space: nowrap;
  }
  .dd-item:hover { background: rgba(255, 255, 255, 0.07); color: #fff; }
  .dd-item-active { color: #00d9ff; background: rgba(0, 217, 255, 0.08); }
</style>
