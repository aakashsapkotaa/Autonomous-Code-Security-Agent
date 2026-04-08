'use client';

import { motion } from 'motion/react';
import { HelpCircle } from 'lucide-react';

export default function Header() {
  return (
    <header className="w-full flex justify-between items-center px-8 py-6 z-50">
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
      >
        <button className="text-on-surface-variant font-medium text-sm px-4 py-2 hover:text-on-surface transition-colors flex items-center gap-2">
          <HelpCircle className="w-4 h-4" />
          Need help?
        </button>
      </motion.div>
    </header>
  );
}
