'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, AlertCircle, CheckCircle } from 'lucide-react';
import Input from './ui/Input';
import Button from './ui/Button';
import GlassFrame from './GlassFrame';
import { supabase } from '@/lib/supabaseClient';

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5 },
  },
};

export default function LoginForm() {
  const [isSignup, setIsSignup] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'error' | 'success'; text: string } | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.id]: e.target.value,
    });
    setMessage(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      if (isSignup) {
        // Validate passwords match
        if (formData.password !== formData.confirmPassword) {
          setMessage({ type: 'error', text: 'Passwords do not match' });
          setLoading(false);
          return;
        }

        // Sign up
        const { data, error } = await supabase.auth.signUp({
          email: formData.email,
          password: formData.password,
          options: {
            data: {
              full_name: formData.name,
            },
          },
        });

        if (error) throw error;

        setMessage({ 
          type: 'success', 
          text: 'Account created! Check your email to verify your account.' 
        });
        
        // Clear form
        setFormData({ name: '', email: '', password: '', confirmPassword: '' });
      } else {
        // Sign in
        const { data, error } = await supabase.auth.signInWithPassword({
          email: formData.email,
          password: formData.password,
        });

        if (error) throw error;

        setMessage({ type: 'success', text: 'Login successful! Redirecting...' });
        
        // Redirect to dashboard after successful login
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 1500);
      }
    } catch (error: any) {
      setMessage({ 
        type: 'error', 
        text: error.message || 'An error occurred. Please try again.' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleGitHubLogin = async () => {
    setLoading(true);
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'github',
        options: {
          redirectTo: `${window.location.origin}/dashboard`,
        },
      });

      if (error) throw error;
    } catch (error: any) {
      setMessage({ 
        type: 'error', 
        text: error.message || 'GitHub login failed. Please try again.' 
      });
      setLoading(false);
    }
  };

  return (
    <motion.div variants={itemVariants} className="relative">
      <GlassFrame className="relative z-10 rounded-xl p-10 neon-glow">
        <div className="mb-10">
          <h2 className="text-2xl font-headline font-bold text-on-background">
            {isSignup ? 'Create Account' : 'Access Console'}
          </h2>
          <p className="mt-1 text-sm text-on-surface-variant">
            {isSignup 
              ? 'Register new operator credentials' 
              : 'Provide credentials to initiate session'}
          </p>
        </div>

        {message && (
          <div className={`mb-6 p-4 rounded-lg flex items-start gap-3 ${
            message.type === 'error' 
              ? 'bg-red-500/10 border border-red-500/20' 
              : 'bg-green-500/10 border border-green-500/20'
          }`}>
            {message.type === 'error' ? (
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            ) : (
              <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
            )}
            <p className={`text-sm ${
              message.type === 'error' ? 'text-red-200' : 'text-green-200'
            }`}>
              {message.text}
            </p>
          </div>
        )}

        <form className="space-y-6" onSubmit={handleSubmit}>
          {isSignup && (
            <div>
              <label className="text-xs font-bold uppercase tracking-widest text-on-surface-variant" htmlFor="name">
                Full Name
              </label>
              <div className="relative group mt-1.5">
                <input
                  className="w-full bg-surface-container-low border border-white/10 rounded-xl py-4 px-4 text-on-background placeholder:text-outline/70 focus:ring-2 focus:ring-primary/35 focus:border-white/30 transition-all outline-none"
                  id="name"
                  placeholder="John Operator"
                  type="text"
                  value={formData.name}
                  onChange={handleChange}
                  required={isSignup}
                />
              </div>
            </div>
          )}

          <div>
            <label className="text-xs font-bold uppercase tracking-widest text-on-surface-variant" htmlFor="email">
              Email Address
            </label>
            <div className="relative group mt-1.5">
              <input
                className="w-full bg-surface-container-low border border-white/10 rounded-xl py-4 px-4 text-on-background placeholder:text-outline/70 focus:ring-2 focus:ring-primary/35 focus:border-white/30 transition-all outline-none"
                id="email"
                placeholder="operator@secureshift.io"
                type="email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center">
              <label className="text-xs font-bold uppercase tracking-widest text-on-surface-variant" htmlFor="password">
                Security Token
              </label>
              {!isSignup && (
                <a className="text-xs text-primary/70 hover:text-primary transition-colors" href="#">
                  Recovery required?
                </a>
              )}
            </div>
            <div className="relative group mt-1.5">
              <input
                className="w-full bg-surface-container-low border border-white/10 rounded-xl py-4 px-4 text-on-background placeholder:text-outline/70 focus:ring-2 focus:ring-primary/35 focus:border-white/30 transition-all outline-none"
                id="password"
                placeholder="************"
                type="password"
                value={formData.password}
                onChange={handleChange}
                required
                minLength={6}
              />
            </div>
          </div>

          {isSignup && (
            <div>
              <label className="text-xs font-bold uppercase tracking-widest text-on-surface-variant" htmlFor="confirmPassword">
                Confirm Security Token
              </label>
              <div className="relative group mt-1.5">
                <input
                  className="w-full bg-surface-container-low border border-white/10 rounded-xl py-4 px-4 text-on-background placeholder:text-outline/70 focus:ring-2 focus:ring-primary/35 focus:border-white/30 transition-all outline-none"
                  id="confirmPassword"
                  placeholder="************"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required={isSignup}
                  minLength={6}
                />
              </div>
            </div>
          )}

          <Button type="submit" variant="primary" fullWidth disabled={loading}>
            {loading ? 'Processing...' : (isSignup ? 'Initialize Account' : 'Establish Connection')}
          </Button>
        </form>

        <div className="mt-6 text-center">
          <button
            type="button"
            onClick={() => {
              setIsSignup(!isSignup);
              setMessage(null);
              setFormData({ name: '', email: '', password: '', confirmPassword: '' });
            }}
            className="text-sm text-on-surface-variant hover:text-on-surface transition-colors"
            disabled={loading}
          >
            {isSignup ? (
              <>
                Already have an account?{' '}
                <span className="text-primary font-semibold">Sign In</span>
              </>
            ) : (
              <>
                New operator?{' '}
                <span className="text-primary font-semibold">Create Account</span>
              </>
            )}
          </button>
        </div>

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
          <Button variant="secondary" fullWidth>
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
