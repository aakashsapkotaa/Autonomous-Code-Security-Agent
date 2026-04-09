'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getCurrentUser } from '@/lib/auth';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import HeroSection from '@/components/HeroSection';
import LoginForm from '@/components/LoginForm';
import ParticleBackground from '@/components/ParticleBackground';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is already logged in
    const checkAuth = async () => {
      const { data: user } = await getCurrentUser();
      if (user) {
        // Redirect to dashboard if already authenticated
        router.push('/dashboard');
      }
    };
    checkAuth();
  }, [router]);

  return (
    <div className="min-h-screen flex flex-col mesh-bg selection:bg-primary-container selection:text-on-primary-container">
      <ParticleBackground />
      <Header />
      
      <main className="flex-grow flex items-center justify-center px-6 py-12 relative overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/10 rounded-full blur-[120px] pointer-events-none" />
        
        <div className="relative z-10 w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <HeroSection />
          <LoginForm />
        </div>
      </main>
      
      <Footer />
    </div>
  );
}
