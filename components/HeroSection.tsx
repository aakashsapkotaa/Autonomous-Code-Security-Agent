'use client';

import { motion } from 'motion/react';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5 },
  },
};

export default function HeroSection() {
  return (
    <motion.div 
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-8 max-w-xl"
    >
      <motion.div variants={itemVariants} className="space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-surface-container-highest/50 rounded-full border border-outline-variant/20">
          <span className="w-2 h-2 rounded-full bg-secondary animate-pulse" />
          <span className="text-xs font-bold uppercase tracking-widest text-secondary">
            The Neon Sentinel
          </span>
        </div>
        
        <h1 className="text-6xl lg:text-7xl font-headline font-bold text-on-background tracking-tighter leading-tight">
          Intelligence at the <span className="text-primary italic">Edge.</span>
        </h1>
        
        <p className="text-lg text-on-surface-variant font-light leading-relaxed">
          Next-gen security analysis powered by <span className="text-on-surface font-medium">AI Agents</span> and cloud-native tools. SecureShift transforms fragmented data into a cohesive shield for your infrastructure.
        </p>
      </motion.div>

      <motion.div 
        variants={itemVariants} 
        className="pt-8 border-t border-outline-variant/10 grid grid-cols-2 gap-6"
      >
        <div className="flex flex-col gap-1">
          <span className="text-3xl font-headline font-bold text-primary">99.9%</span>
          <span className="text-xs font-bold text-on-surface-variant uppercase tracking-wider">
            Threat Detection
          </span>
        </div>
        <div className="flex flex-col gap-1">
          <span className="text-3xl font-headline font-bold text-primary">24/7</span>
          <span className="text-xs font-bold text-on-surface-variant uppercase tracking-wider">
            Autonomous Monitoring
          </span>
        </div>
      </motion.div>
    </motion.div>
  );
}
