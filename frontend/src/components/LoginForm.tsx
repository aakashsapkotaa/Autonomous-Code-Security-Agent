'use client';

import { motion } from 'motion/react';
import { Github, ArrowRight } from 'lucide-react';
import Input from './ui/Input';
import Button from './ui/Button';
import GlassFrame from './GlassFrame';

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5 },
  },
};

export default function LoginForm() {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Login submitted');
  };

  return (
    <motion.div variants={itemVariants} className="relative">
      <GlassFrame className="relative z-10 rounded-xl p-10 neon-glow">
        <div className="mb-10">
          <h2 className="text-2xl font-headline font-bold text-on-background">
            Access Console
          </h2>
          <p className="mt-1 text-sm text-on-surface-variant">
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
            placeholder="************"
            icon="lock"
            helperLink={{ text: 'Recovery required?', href: '#' }}
          />

          <Button type="submit" variant="primary" fullWidth>
            Establish Connection
          </Button>
        </form>

        <div className="relative mt-8">
          <div aria-hidden="true" className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-outline-variant/20" />
          </div>
          <div className="relative flex justify-center text-xs font-semibold uppercase tracking-widest">
            <span className="bg-surface-container px-4 text-on-surface-variant">
              External Protocol
            </span>
          </div>
        </div>

        <div className="mt-8">
          <Button variant="secondary" fullWidth icon={<Github className="h-5 w-5" />}>
            Connect to GitHub
            <ArrowRight className="h-4 w-4 text-primary opacity-0 transition-all group-hover:translate-x-1 group-hover:opacity-100" />
          </Button>
        </div>
      </GlassFrame>

      <div className="absolute -bottom-6 -right-6 -z-10 h-32 w-32 rounded-xl bg-white/8 blur-2xl" />
      <div className="absolute -left-10 -top-10 -z-10 h-48 w-48 rounded-full bg-white/10 blur-3xl" />
    </motion.div>
  );
}
