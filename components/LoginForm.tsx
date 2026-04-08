'use client';

import { motion } from 'motion/react';
import { Github, ArrowRight } from 'lucide-react';
import Input from './ui/Input';
import Button from './ui/Button';

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: 'easeOut' },
  },
};

export default function LoginForm() {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Login submitted');
  };

  return (
    <motion.div variants={itemVariants} className="relative">
      <div className="glass-panel p-10 rounded-xl border border-outline-variant/20 neon-glow relative z-10">
        <div className="mb-10">
          <h2 className="text-2xl font-headline font-bold text-on-background">
            Access Console
          </h2>
          <p className="text-on-surface-variant text-sm mt-1">
            Provide credentials to initiate session
          </p>
        </div>

        <form className="space-y-6" onSubmit={handleSubmit}>
          <Input
            id="email"
            label="Email Address"
            type="email"
            placeholder="operator@secureshift.io"
            icon="email"
          />

          <Input
            id="password"
            label="Security Token"
            type="password"
            placeholder="••••••••••••"
            icon="lock"
            helperLink={{ text: 'Recovery Required?', href: '#' }}
          />

          <Button type="submit" variant="primary" fullWidth>
            Establish Connection
          </Button>
        </form>

        <div className="mt-8 relative">
          <div aria-hidden="true" className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-outline-variant/20" />
          </div>
          <div className="relative flex justify-center text-xs uppercase tracking-widest">
            <span className="bg-[#151a21] px-4 text-on-surface-variant font-semibold">
              External Protocol
            </span>
          </div>
        </div>

        <div className="mt-8">
          <Button variant="secondary" fullWidth icon={<Github className="w-5 h-5" />}>
            Connect to GitHub
            <ArrowRight className="w-4 h-4 text-primary opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
          </Button>
        </div>
      </div>

      <div className="absolute -bottom-6 -right-6 w-32 h-32 bg-secondary/10 rounded-xl blur-2xl -z-10" />
      <div className="absolute -top-10 -left-10 w-48 h-48 bg-primary/10 rounded-full blur-3xl -z-10" />
    </motion.div>
  );
}
