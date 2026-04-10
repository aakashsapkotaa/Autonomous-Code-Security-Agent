'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Bot, Sparkles, Shield } from 'lucide-react';
import HelpBot from './HelpBot';

export default function Header() {
  const [botOpen, setBotOpen] = useState(false);

  return (
    <header className="relative z-20 w-full flex justify-between items-center px-8 py-6">
      <motion.div 
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="flex items-center gap-3 group"
      >
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-neon-cyan to-neon-blue rounded-lg blur opacity-75 group-hover:opacity-100 transition duration-300" />
          <div className="relative bg-dark-bg px-3 py-2 rounded-lg flex items-center gap-2">
            <Shield className="w-5 h-5 text-neon-cyan" />
          </div>
        </div>
        <span className="text-2xl font-headline font-bold bg-gradient-to-r from-neon-cyan to-neon-purple bg-clip-text text-transparent tracking-tighter">
          SecureShift
        </span>
      </motion.div>
      
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="relative"
      >
        <button
          type="button"
          onClick={() => setBotOpen((open) => !open)}
          className="group relative flex items-center gap-3 rounded-full border border-neon-cyan/30 bg-gradient-to-r from-neon-cyan/10 to-neon-purple/10 px-4 py-2 text-left transition-all duration-300 hover:border-neon-cyan/60 hover:from-neon-cyan/20 hover:to-neon-purple/20 hover:shadow-neon-cyan/50"
        >
          <span className="flex h-10 w-10 items-center justify-center rounded-full border border-neon-cyan/50 bg-gradient-to-br from-neon-cyan/20 to-neon-blue/10 text-neon-cyan shadow-lg shadow-neon-cyan/30 group-hover:shadow-neon-cyan/60 transition-all duration-300">
            <Bot className="h-5 w-5" />
          </span>
          <span className="flex flex-col leading-none">
            <span className="flex items-center gap-1 text-[10px] font-semibold uppercase tracking-[0.24em] bg-gradient-to-r from-neon-cyan to-neon-blue bg-clip-text text-transparent">
              AI Bot
              <Sparkles className="h-3 w-3 text-neon-cyan" />
            </span>
            <span className="mt-1 text-sm font-medium text-on-surface">
              Need help?
            </span>
          </span>
        </button>
        <HelpBot open={botOpen} onClose={() => setBotOpen(false)} />
      </motion.div>
    </header>
  );
}
