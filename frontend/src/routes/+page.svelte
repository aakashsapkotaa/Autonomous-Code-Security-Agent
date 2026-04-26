<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { supabase } from '$lib/supabaseClient';
  import AuroraBackground from '$lib/components/AuroraBackground.svelte';
  import Header from '$lib/components/Header.svelte';
  import HeroSection from '$lib/components/HeroSection.svelte';
  import LoginForm from '$lib/components/LoginForm.svelte';
  import FeaturesSection from '$lib/components/FeaturesSection.svelte';
  import Footer from '$lib/components/Footer.svelte';

  // If already authenticated, skip the landing page entirely
  onMount(async () => {
    const { data: { session } } = await supabase.auth.getSession();
    if (session) goto('/dashboard', { replaceState: true });
  });
</script>

<svelte:head>
  <title>SecureShift — AI-Powered Security Scanner</title>
  <meta name="description" content="Autonomous vulnerability detection and AI-generated fixes for your GitHub repositories." />
</svelte:head>

<div class="min-h-screen flex flex-col">
  <AuroraBackground />

  <div class="relative z-10 flex flex-col">
    <Header />

    <!-- Hero + Login -->
    <section class="flex items-center px-6 sm:px-10 lg:px-16 py-10 sm:py-14 min-h-[calc(100vh-72px)]">
      <div class="w-full max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-14 lg:gap-20 items-center">
        <HeroSection />
        <div id="login" class="w-full max-w-md mx-auto lg:mx-0 lg:ml-auto">
          <LoginForm />
        </div>
      </div>
    </section>

    <!-- Divider -->
    <div class="w-full max-w-7xl mx-auto px-6 sm:px-10 lg:px-16">
      <div class="h-px bg-gradient-to-r from-transparent via-white/[0.07] to-transparent"></div>
    </div>

    <!-- Features -->
    <FeaturesSection />

    <Footer />
  </div>
</div>
