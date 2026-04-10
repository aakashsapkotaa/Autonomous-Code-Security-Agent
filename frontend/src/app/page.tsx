'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
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
    <div className="min-h-screen flex flex-col mesh-bg selection:bg-neon-cyan/20 selection:text-neon-cyan relative overflow-hidden">
      <ParticleBackground />
      <Header />
      
      <main className="flex-grow flex items-center justify-center px-4 sm:px-6 py-8 sm:py-12 relative overflow-hidden">
        {/* Animated background gradient orbs */}
        <motion.div 
          className="absolute top-1/3 left-1/4 w-[300px] sm:w-[600px] h-[300px] sm:h-[600px] bg-gradient-to-br from-neon-cyan/15 to-transparent rounded-full blur-[80px] sm:blur-[140px] pointer-events-none"
          animate={{
            x: [0, 50, 0],
            y: [0, 30, 0],
          }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div 
          className="absolute bottom-1/3 right-1/4 w-[300px] sm:w-[600px] h-[300px] sm:h-[600px] bg-gradient-to-bl from-neon-purple/15 to-transparent rounded-full blur-[80px] sm:blur-[140px] pointer-events-none"
          animate={{
            x: [0, -50, 0],
            y: [0, -30, 0],
          }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
        />
        
        <div className="relative z-10 w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-8 sm:gap-12 lg:gap-16 items-center">
          <HeroSection />
          <LoginForm />
        </div>
      </main>
      
      <Footer />
    </div>
  );
}
