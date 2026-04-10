'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getRepositories } from '@/lib/database';
import { getCurrentUser, signOut } from '@/lib/auth';
import type { Repository } from '@/lib/types';
import RepoList from './RepoList';
import HelpBot from './HelpBot';
import { Shield, AlertTriangle, CheckCircle, LogOut } from 'lucide-react';

export default function Dashboard() {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    initDashboard();
  }, []);

  const initDashboard = async () => {
    // Get current user
    const { data: userData, error: userError } = await getCurrentUser();
    
    if (userError || !userData) {
      // Redirect to login if not authenticated
      window.location.href = '/';
      return;
    }

    setUser(userData);
    loadRepositories();
  };

  const loadRepositories = async () => {
    setLoading(true);
    setError(null);

    const { data, error: err } = await getRepositories();

    if (err) {
      setError(err);
      setLoading(false);
      return;
    }

    setRepositories(data || []);
    setLoading(false);
  };

  const handleSignOut = async () => {
    const { error } = await signOut();
    if (error) {
      console.error('Sign out error:', error);
      alert('Failed to sign out. Please try again.');
      return;
    }
    // Redirect to home page after sign out
    window.location.href = '/';
  };

  if (loading) {
    return (
      <div className="w-full max-w-6xl mx-auto px-6 py-12 relative z-10">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="flex flex-col items-center gap-4">
            <div className="w-12 h-12 border-4 border-neon-cyan/30 border-t-neon-cyan rounded-full animate-spin" />
            <p className="text-on-surface-variant animate-pulse">Loading repositories...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full max-w-6xl mx-auto px-6 py-12 relative z-10">
        <div className="space-y-6">
          <div className="glass-panel border border-neon-pink/50 rounded-xl p-6 flex items-start gap-4">
            <AlertTriangle className="w-6 h-6 text-neon-pink flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg font-headline font-bold text-neon-pink mb-2">
                Error Loading Data
              </h3>
              <p className="text-on-surface-variant mb-2">{error}</p>
              <details className="text-sm text-on-surface-variant/70 mt-4">
                <summary className="cursor-pointer hover:text-on-surface-variant">
                  Troubleshooting Tips
                </summary>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li>Check if your .env.local file exists with correct values</li>
                  <li>Verify NEXT_PUBLIC_SUPABASE_URL is set correctly</li>
                  <li>Verify NEXT_PUBLIC_SUPABASE_ANON_KEY is a valid JWT token</li>
                  <li>Ensure the database schema has been applied in Supabase</li>
                  <li>Check if Row Level Security (RLS) policies allow anonymous access</li>
                </ul>
              </details>
              <button
                onClick={loadRepositories}
                className="mt-4 px-4 py-2 bg-neon-pink/20 hover:bg-neon-pink/30 text-neon-pink rounded-lg transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-6xl mx-auto px-4 sm:px-6 py-8 sm:py-12 relative z-10">
      {/* Header with Sign Out */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8 sm:mb-12">
        <div>
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-headline font-bold bg-gradient-to-r from-neon-cyan to-neon-purple bg-clip-text text-transparent">
            Security Dashboard
          </h1>
          {user && (
            <p className="text-xs sm:text-sm text-on-surface-variant mt-2">
              👋 Welcome back, <span className="text-neon-cyan font-semibold break-all">{user.email}</span>
            </p>
          )}
        </div>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleSignOut}
          className="flex items-center gap-2 px-4 sm:px-6 py-2 sm:py-3 text-sm sm:text-base bg-gradient-to-r from-neon-pink/20 to-accent-2/20 hover:from-neon-pink/40 hover:to-accent-2/40 text-neon-pink border border-neon-pink/50 rounded-lg transition-all duration-300 whitespace-nowrap"
        >
          <LogOut className="w-4 h-4" />
          Sign Out
        </motion.button>
      </div>

      {/* Stats Overview */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mb-8 sm:mb-12"
      >
        {/* Repositories Card */}
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="glass-panel p-6 rounded-xl border-neon card-hover relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/5 to-transparent opacity-0 hover:opacity-100 transition-opacity" />
          <div className="flex items-center justify-between relative z-10">
            <div>
              <p className="text-sm text-neon-cyan/80 uppercase font-bold tracking-wider mb-2">
                Repositories
              </p>
              <p className="text-3xl font-headline font-bold gradient-text-cyan">
                {repositories.length}
              </p>
            </div>
            <div className="w-14 h-14 bg-gradient-to-br from-neon-cyan/20 to-neon-blue/10 rounded-lg flex items-center justify-center shadow-neon-cyan">
              <Shield className="w-7 h-7 text-neon-cyan" />
            </div>
          </div>
        </motion.div>

        {/* Active Scans Card */}
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="glass-panel-purple p-6 rounded-xl border-neon-purple card-hover relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-neon-purple/5 to-transparent opacity-0 hover:opacity-100 transition-opacity" />
          <div className="flex items-center justify-between relative z-10">
            <div>
              <p className="text-sm text-neon-purple/80 uppercase font-bold tracking-wider mb-2">
                Active Scans
              </p>
              <p className="text-3xl font-headline font-bold bg-gradient-to-r from-neon-purple to-accent-1 bg-clip-text text-transparent">
                0
              </p>
            </div>
            <div className="w-14 h-14 bg-gradient-to-br from-neon-purple/20 to-accent-1/10 rounded-lg flex items-center justify-center shadow-neon-purple">
              <AlertTriangle className="w-7 h-7 text-neon-purple" />
            </div>
          </div>
        </motion.div>

        {/* Vulnerabilities Fixed Card */}
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="glass-panel p-6 rounded-xl border border-neon-pink/30 hover:border-neon-pink/60 card-hover relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-neon-pink/5 to-transparent opacity-0 hover:opacity-100 transition-opacity" />
          <div className="flex items-center justify-between relative z-10">
            <div>
              <p className="text-sm text-neon-pink/80 uppercase font-bold tracking-wider mb-2">
                Fixed
              </p>
              <p className="text-3xl font-headline font-bold bg-gradient-to-r from-neon-pink to-accent-2 bg-clip-text text-transparent">
                0
              </p>
            </div>
            <div className="w-14 h-14 bg-gradient-to-br from-neon-pink/20 to-accent-2/10 rounded-lg flex items-center justify-center shadow-neon-pink">
              <CheckCircle className="w-7 h-7 text-neon-pink" />
            </div>
          </div>
        </motion.div>
      </motion.div>

      {/* Repository List */}
      <RepoList repositories={repositories} onRefresh={loadRepositories} userId={user?.id || null} />
    </div>
  );
}
