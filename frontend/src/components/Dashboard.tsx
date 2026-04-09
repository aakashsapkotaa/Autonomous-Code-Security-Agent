'use client';

import { useEffect, useState } from 'react';
import { getRepositories } from '@/lib/database';
import { getCurrentUser, signOut } from '@/lib/auth';
import type { Repository } from '@/lib/types';
import RepoList from './RepoList';
import HelpBot from './HelpBot';
import { Shield, AlertTriangle, CheckCircle, LogOut, Bot } from 'lucide-react';

export default function Dashboard() {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<any>(null);
  const [helpBotOpen, setHelpBotOpen] = useState(false);

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
      <div className="w-full max-w-6xl mx-auto px-6 py-12">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="flex flex-col items-center gap-4">
            <div className="w-12 h-12 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
            <p className="text-on-surface-variant">Loading repositories...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full max-w-6xl mx-auto px-6 py-12">
        <div className="space-y-6">
          <div className="bg-error/10 border border-error/20 rounded-xl p-6 flex items-start gap-4">
            <AlertTriangle className="w-6 h-6 text-error flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg font-headline font-bold text-error mb-2">
                Error Loading Data
              </h3>
              <p className="text-on-surface-variant mb-2">{error}</p>
              <details className="text-sm text-on-surface-variant/70 mt-4">
                <summary className="cursor-pointer hover:text-on-surface-variant">
                  Troubleshooting Tips
                </summary>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li>Check if your .env.local file exists with correct values</li>
                  <li>Verify NEXT_PUBLIC_https://ayeoqnvldhrazjpvbrey.supabase.co is set correctly</li>
                  <li>Verify NEXT_PUBLIC_SUPABASE_ANON_KEY is a valid JWT token</li>
                  <li>Ensure the database schema has been applied in Supabase</li>
                  <li>Check if Row Level Security (RLS) policies allow anonymous access</li>
                </ul>
              </details>
              <button
                onClick={loadRepositories}
                className="mt-4 px-4 py-2 bg-error/20 hover:bg-error/30 text-error rounded-lg transition-colors"
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
    <div className="w-full max-w-6xl mx-auto px-6 py-12">
      {/* Header with Sign Out */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-headline font-bold text-on-background">
            Security Dashboard
          </h1>
          {user && (
            <p className="text-sm text-on-surface-variant mt-1">
              Welcome, {user.email}
            </p>
          )}
        </div>
        <button
          onClick={handleSignOut}
          className="flex items-center gap-2 px-4 py-2 bg-surface-container-high hover:bg-surface-bright text-on-surface rounded-lg transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Sign Out
        </button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div className="glass-panel p-6 rounded-xl border border-outline-variant/20">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
              <Shield className="w-6 h-6 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-headline font-bold text-on-background">
                {repositories.length}
              </p>
              <p className="text-sm text-on-surface-variant">Total Repositories</p>
            </div>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-xl border border-outline-variant/20">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-secondary/10 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-secondary" />
            </div>
            <div>
              <p className="text-2xl font-headline font-bold text-on-background">0</p>
              <p className="text-sm text-on-surface-variant">Active Scans</p>
            </div>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-xl border border-outline-variant/20">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-tertiary/10 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-tertiary" />
            </div>
            <div>
              <p className="text-2xl font-headline font-bold text-on-background">0</p>
              <p className="text-sm text-on-surface-variant">Vulnerabilities Fixed</p>
            </div>
          </div>
        </div>
      </div>

      {/* Repository List */}
      {user && <RepoList repositories={repositories} onRefresh={loadRepositories} userId={user.id} />}

      {/* Floating Help Bot Button */}
      <div className="fixed bottom-8 right-8 z-50">
        <div className="relative">
          <HelpBot open={helpBotOpen} onClose={() => setHelpBotOpen(false)} />
          <button
            onClick={() => setHelpBotOpen(!helpBotOpen)}
            className="flex items-center gap-3 px-6 py-4 bg-primary hover:bg-primary/90 text-on-primary rounded-full shadow-lg transition-all hover:scale-105"
            aria-label="Open SecureShift AI Bot"
          >
            <Bot className="w-5 h-5" />
            <span className="font-medium">Need Help?</span>
          </button>
        </div>
      </div>
    </div>
  );
}
