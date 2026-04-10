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
            emailRedirectTo: `${window.location.origin}/dashboard`,
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

  return (
    <motion.div variants={itemVariants} className="relative">
      <GlassFrame className="relative z-10 rounded-2xl p-6 sm:p-8 lg:p-10 border-neon neon-glow">
        <div className="mb-8 sm:mb-10">
          <h2 className="text-2xl sm:text-3xl font-headline font-bold bg-gradient-to-r from-neon-cyan to-neon-blue bg-clip-text text-transparent">
            {isSignup ? '🔐 Create Account' : '🚀 Access Console'}
          </h2>
          <p className="mt-2 text-xs sm:text-sm text-on-surface-variant">
            {isSignup 
              ? 'Register with your credentials to start securing' 
              : 'Enter your credentials to access your security dashboard'}
          </p>
        </div>

        {message && (
          <motion.div 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`mb-6 p-4 rounded-lg flex items-start gap-3 border backdrop-blur-sm ${
            message.type === 'error' 
              ? 'bg-neon-pink/10 border-neon-pink/50' 
              : 'bg-neon-cyan/10 border-neon-cyan/50'
          }`}>
            {message.type === 'error' ? (
              <AlertCircle className="w-5 h-5 text-neon-pink flex-shrink-0 mt-0.5" />
            ) : (
              <CheckCircle className="w-5 h-5 text-neon-cyan flex-shrink-0 mt-0.5" />
            )}
            <p className={`text-sm font-medium ${
              message.type === 'error' ? 'text-neon-pink/90' : 'text-neon-cyan/90'
            }`}>
              {message.text}
            </p>
          </motion.div>
        )}

        <form className="space-y-4 sm:space-y-6" onSubmit={handleSubmit}>
          {isSignup && (
            <div>
              <label className="text-xs font-bold uppercase tracking-widest text-neon-cyan/80" htmlFor="name">
                Full Name
              </label>
              <div className="relative group mt-2">
                <input
                  className="w-full bg-card-bg border border-neon-cyan/30 hover:border-neon-cyan/60 rounded-lg py-3 px-4 text-on-background placeholder:text-outline/50 focus:border-neon-cyan focus:ring-2 focus:ring-neon-cyan/20 transition-all outline-none"
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
            <label className="text-xs font-bold uppercase tracking-widest text-neon-cyan/80" htmlFor="email">
              Email Address
            </label>
            <div className="relative group mt-2">
              <input
                className="w-full bg-card-bg border border-neon-cyan/30 hover:border-neon-cyan/60 rounded-lg py-3 px-4 text-on-background placeholder:text-outline/50 focus:border-neon-cyan focus:ring-2 focus:ring-neon-cyan/20 transition-all outline-none"
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
              <label className="text-xs font-bold uppercase tracking-widest text-neon-cyan/80" htmlFor="password">
                Password
              </label>
              {!isSignup && (
                <a className="text-xs text-neon-cyan/60 hover:text-neon-cyan transition-colors" href="#">
                  Forgot password?
                </a>
              )}
            </div>
            <div className="relative group mt-2">
              <input
                className="w-full bg-card-bg border border-neon-cyan/30 hover:border-neon-cyan/60 rounded-lg py-3 px-4 text-on-background placeholder:text-outline/50 focus:border-neon-cyan focus:ring-2 focus:ring-neon-cyan/20 transition-all outline-none"
                id="password"
                placeholder="••••••••"
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
              <label className="text-xs font-bold uppercase tracking-widest text-neon-cyan/80" htmlFor="confirmPassword">
                Confirm Password
              </label>
              <div className="relative group mt-2">
                <input
                  className="w-full bg-card-bg border border-neon-cyan/30 hover:border-neon-cyan/60 rounded-lg py-3 px-4 text-on-background placeholder:text-outline/50 focus:border-neon-cyan focus:ring-2 focus:ring-neon-cyan/20 transition-all outline-none"
                  id="confirmPassword"
                  placeholder="••••••••"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required={isSignup}
                  minLength={6}
                />
              </div>
            </div>
          )}

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-neon-cyan to-neon-blue hover:from-neon-cyan/90 hover:to-neon-blue/90 text-dark-bg font-bold py-2.5 sm:py-3 text-sm sm:text-base rounded-lg transition-all duration-300 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? 'Processing...' : (
              <>
                {isSignup ? 'Create Account' : 'Sign In'}
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </motion.button>
        </form>

        <div className="mt-6 sm:mt-8 text-center">
          <button
            type="button"
            onClick={() => {
              setIsSignup(!isSignup);
              setMessage(null);
              setFormData({ name: '', email: '', password: '', confirmPassword: '' });
            }}
            className="text-xs sm:text-sm text-on-surface-variant hover:text-neon-cyan transition-colors"
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
      </GlassFrame>

      <div className="absolute -bottom-6 -right-6 -z-10 h-32 w-32 rounded-xl bg-white/8 blur-2xl" />
      <div className="absolute -left-10 -top-10 -z-10 h-48 w-48 rounded-full bg-white/10 blur-3xl" />
    </motion.div>
  );
}
