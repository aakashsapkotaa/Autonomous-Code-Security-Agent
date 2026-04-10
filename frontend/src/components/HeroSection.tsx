'use client';

import { motion } from 'framer-motion';
import GlassFrame from './GlassFrame';
import { Zap, Shield, TrendingUp } from 'lucide-react';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.12,
      delayChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: "easeOut" },
  },
};

const floatingVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.8 },
  },
  animate: {
    y: [0, -10, 0],
    transition: { duration: 3, repeat: Infinity, ease: "easeInOut" },
  },
};

export default function HeroSection() {
  return (
    <motion.div 
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6 sm:space-y-8 max-w-2xl relative z-10"
    >
      {/* Badge */}
      <motion.div variants={itemVariants}>
        <div className="inline-flex items-center gap-2 px-3 sm:px-4 py-1.5 sm:py-2 bg-gradient-to-r from-neon-cyan/20 to-neon-purple/20 rounded-full border border-neon-cyan/50 backdrop-blur-sm hover:border-neon-cyan transition-all duration-300">
          <span className="w-2 h-2 rounded-full bg-neon-cyan animate-pulse-neon" />
          <span className="text-[10px] sm:text-xs font-bold uppercase tracking-widest bg-gradient-to-r from-neon-cyan to-neon-blue bg-clip-text text-transparent">
            🔒 Next-Gen Security Platform
          </span>
        </div>
      </motion.div>

      {/* Main Heading */}
      <motion.div variants={itemVariants} className="space-y-3 sm:space-y-4">
        <h1 className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-headline font-bold uppercase tracking-[-0.04em] leading-[1.1]">
          <span className="gradient-text-cyan">Autonomous</span>
          <br />
          <span className="text-white">Security</span>
          <br />
          <span className="gradient-text">Intelligence</span>
        </h1>
        
        <p className="text-sm sm:text-base lg:text-lg text-on-surface-variant font-light leading-relaxed max-w-lg">
          Harness the power of <span className="text-neon-cyan font-semibold">AI-driven agents</span> to detect, analyze, and remediate vulnerabilities <span className="text-neon-purple font-semibold">24/7</span> with surgical precision.
        </p>
      </motion.div>

      {/* Stats Grid */}
      <motion.div 
        variants={itemVariants} 
        className="pt-6 sm:pt-8 border-t border-neon-cyan/20 grid grid-cols-3 gap-2 sm:gap-4"
      >
        <motion.div variants={floatingVariants} animate="animate">
          <GlassFrame className="rounded-lg sm:rounded-xl px-2 sm:px-5 py-3 sm:py-4 border-neon card-hover">
            <div className="flex flex-col gap-1 sm:gap-2">
              <div className="flex items-center gap-1 sm:gap-2">
                <Zap className="w-3 h-3 sm:w-4 sm:h-4 text-neon-cyan animate-pulse" />
                <span className="text-xl sm:text-2xl lg:text-3xl font-headline font-bold gradient-text-cyan">99.9%</span>
              </div>
              <span className="text-[8px] sm:text-xs font-bold text-neon-cyan/80 uppercase tracking-wider">
                Detection
              </span>
            </div>
          </GlassFrame>
        </motion.div>

        <motion.div variants={floatingVariants} animate="animate" transition={{ delay: 0.2 }}>
          <GlassFrame className="rounded-lg sm:rounded-xl px-2 sm:px-5 py-3 sm:py-4 border border-neon-purple/30 hover:border-neon-purple/60 transition-all duration-300 card-hover">
            <div className="flex flex-col gap-1 sm:gap-2">
              <div className="flex items-center gap-1 sm:gap-2">
                <Shield className="w-3 h-3 sm:w-4 sm:h-4 text-neon-purple animate-pulse" />
                <span className="text-xl sm:text-2xl lg:text-3xl font-headline font-bold bg-gradient-to-r from-neon-purple to-neon-pink bg-clip-text text-transparent">24/7</span>
              </div>
              <span className="text-[8px] sm:text-xs font-bold text-neon-purple/80 uppercase tracking-wider">
                Monitor
              </span>
            </div>
          </GlassFrame>
        </motion.div>

        <motion.div variants={floatingVariants} animate="animate" transition={{ delay: 0.4 }}>
          <GlassFrame className="rounded-lg sm:rounded-xl px-2 sm:px-5 py-3 sm:py-4 border border-neon-pink/30 hover:border-neon-pink/60 transition-all duration-300 card-hover">
            <div className="flex flex-col gap-1 sm:gap-2">
              <div className="flex items-center gap-1 sm:gap-2">
                <TrendingUp className="w-3 h-3 sm:w-4 sm:h-4 text-neon-pink animate-pulse" />
                <span className="text-xl sm:text-2xl lg:text-3xl font-headline font-bold bg-gradient-to-r from-neon-pink to-accent-2 bg-clip-text text-transparent">100+</span>
              </div>
              <span className="text-[8px] sm:text-xs font-bold text-neon-pink/80 uppercase tracking-wider">
                Scans
              </span>
            </div>
          </GlassFrame>
        </motion.div>
      </motion.div>

      {/* CTA Button */}
      <motion.div variants={itemVariants} className="pt-2 sm:pt-4 hidden lg:block">
        <motion.button 
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="relative group px-6 sm:px-8 py-3 sm:py-4 rounded-lg font-bold text-base sm:text-lg overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-neon-cyan to-neon-blue opacity-100 group-hover:opacity-90 transition-opacity" />
          <div className="absolute inset-0 bg-gradient-to-r from-neon-purple to-neon-pink opacity-0 group-hover:opacity-50 transition-opacity duration-300" />
          <span className="relative flex items-center justify-center gap-2 text-dark-bg">
            Start Securing Now
            <Zap className="w-4 h-4 sm:w-5 sm:h-5" />
          </span>
        </motion.button>
      </motion.div>
    </motion.div>
  );
}
