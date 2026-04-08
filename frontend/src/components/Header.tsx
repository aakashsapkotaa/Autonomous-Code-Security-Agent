'use client';

import { useState } from 'react';
import { motion } from 'motion/react';
import { Bot, Sparkles } from 'lucide-react';
import HelpBot from './HelpBot';

export default function Header() {
  const [botOpen, setBotOpen] = useState(false);

  return (
    <header className="relative z-20 w-full flex justify-between items-center px-8 py-6">
      <motion.div 
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="flex items-center gap-2"
      >
        <span className="text-2xl font-headline font-bold tracking-tighter text-primary">
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
          className="group flex items-center gap-3 rounded-full border border-white/10 bg-white/[0.04] px-3 py-2 text-left transition-all hover:border-white/20 hover:bg-white/[0.07] hover:text-on-surface"
        >
          <span className="flex h-10 w-10 items-center justify-center rounded-full border border-white/10 bg-white/[0.06] text-primary shadow-[0_0_22px_rgba(255,255,255,0.14)]">
            <Bot className="h-5 w-5" />
          </span>
          <span className="flex flex-col leading-none">
            <span className="flex items-center gap-1 text-[10px] font-semibold uppercase tracking-[0.24em] text-on-surface-variant">
              AI Bot
              <Sparkles className="h-3 w-3 text-primary/80" />
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
