<script lang="ts">
  import { Bot, MessageSquare, Send, X, Loader2 } from 'lucide-svelte';
  import GlassFrame from './GlassFrame.svelte';
  import { PUBLIC_API_URL } from '$env/static/public';

  export let open = false;
  export let onClose: () => void;

  const quickPrompts = [
    'How do I sign in?',
    'What does SecureShift monitor?',
    'How do I add a repository?',
  ];
  const answers: Record<string, string> = {
    'How do I sign in?': 'Click "Sign In" on the home page, enter your email and password. New users can create an account by clicking "Sign Up" instead.',
    'What does SecureShift monitor?': 'SecureShift scans your GitHub repositories for security vulnerabilities using multiple tools (Bandit, Safety, TruffleHog) and provides AI-powered fix suggestions.',
    'How do I add a repository?': 'In the dashboard, enter your GitHub repository URL in the "Add Repository" section and click "Add Repository". The system will automatically scan it for vulnerabilities.',
  };
  const fallback = 'SecureShift AI can help with sign-in, repository scanning, vulnerability monitoring, and navigating the security dashboard.';

  let selectedPrompt = quickPrompts[0];
  let customQuestion = '';
  let aiResponse = '';
  let isLoading = false;

  $: response = aiResponse || answers[selectedPrompt] || fallback;

  function selectPrompt(p: string) { selectedPrompt = p; customQuestion = ''; aiResponse = ''; }

  async function handleAsk(e: Event) {
    e.preventDefault();
    const q = customQuestion.trim();
    if (!q) return;
    isLoading = true; selectedPrompt = q; aiResponse = '';
    try {
      const apiUrl = PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiUrl}/api/chatbot/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: q }),
      });
      if (!res.ok) throw new Error(`API returned ${res.status}`);
      const data = await res.json();
      if (data.response) { aiResponse = data.response; customQuestion = ''; }
      else throw new Error('No response from AI');
    } catch (err: any) {
      const msg = err.message || '';
      if (msg.includes('Failed to fetch') || msg.includes('NetworkError'))
        aiResponse = `Cannot connect to AI service. Please check backend is running on ${PUBLIC_API_URL || 'http://localhost:8000'}.`;
      else if (msg.includes('429')) aiResponse = 'The AI service is temporarily busy. Please try again in a moment.';
      else aiResponse = `Error: ${msg}\n\nPlease try again or select a quick prompt above.`;
    } finally { isLoading = false; }
  }
</script>

{#if open}
  <div class="absolute right-0 top-[calc(100%+14px)] z-50 w-[360px] max-w-[calc(100vw-2rem)]"
    style="animation: fadeInDown 0.2s ease;">
    <GlassFrame class="rounded-3xl p-4 shadow-[0_24px_80px_-32px_rgba(255,255,255,0.3)]">
      <div class="flex items-start justify-between gap-4">
        <div class="flex items-center gap-3">
          <span class="flex h-11 w-11 items-center justify-center rounded-full border border-white/10 bg-white/[0.08] text-neon-cyan">
            <Bot class="h-5 w-5" />
          </span>
          <div>
            <p class="text-sm font-semibold text-on-background">SecureShift AI Bot</p>
            <p class="text-xs uppercase tracking-[0.2em] text-on-surface-variant">Instant Help</p>
          </div>
        </div>
        <button type="button" on:click={onClose}
          class="rounded-full border border-white/10 bg-white/[0.04] p-2 text-on-surface-variant hover:text-on-surface transition-colors">
          <X class="h-4 w-4" />
        </button>
      </div>

      <div class="mt-4 rounded-2xl border border-white/[0.08] bg-black/30 p-4">
        <div class="flex items-start gap-3">
          <span class="mt-1 text-neon-cyan">
            {#if isLoading}<Loader2 class="h-4 w-4 animate-spin" />{:else}<MessageSquare class="h-4 w-4" />{/if}
          </span>
          <div class="flex-1">
            <p class="text-sm font-medium text-on-background">{selectedPrompt}</p>
            <p class="mt-2 text-sm leading-6 text-on-surface-variant whitespace-pre-line">
              {isLoading ? 'Thinking...' : response}
            </p>
          </div>
        </div>
      </div>

      <div class="mt-4 space-y-2">
        {#each quickPrompts as prompt}
          <button type="button" on:click={() => selectPrompt(prompt)}
            class="w-full rounded-2xl border px-4 py-3 text-left text-sm transition-all
              {selectedPrompt === prompt
                ? 'border-white/20 bg-white/[0.08] text-on-background'
                : 'border-white/[0.08] bg-white/[0.03] text-on-surface-variant hover:bg-white/[0.06] hover:text-on-surface'}">
            {prompt}
          </button>
        {/each}
      </div>

      <form on:submit={handleAsk} class="mt-4 flex items-center gap-3 rounded-2xl border border-white/[0.08] bg-white/[0.03] px-3 py-3">
        <input bind:value={customQuestion} placeholder="Ask SecureShift AI for guided help"
          class="w-full bg-transparent px-1 text-sm text-on-background outline-none placeholder:text-on-surface-variant" />
        <button type="submit" disabled={isLoading || !customQuestion.trim()}
          class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white text-black transition-transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed">
          {#if isLoading}<Loader2 class="h-4 w-4 animate-spin" />{:else}<Send class="h-4 w-4" />{/if}
        </button>
      </form>
    </GlassFrame>
  </div>
{/if}

<style>
  @keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-10px) scale(0.98); }
    to   { opacity: 1; transform: translateY(0)     scale(1); }
  }
</style>
