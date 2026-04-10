'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { addRepository, createScan } from '@/lib/database';
import type { Repository } from '@/lib/types';
import { GitBranch, Plus, Play, ExternalLink, Calendar, Code2 } from 'lucide-react';
import GlassFrame from './GlassFrame';

interface RepoListProps {
  repositories: Repository[];
  onRefresh: () => void;
  userId: string | null;
}

export default function RepoList({ repositories, onRefresh, userId }: RepoListProps) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [repoUrl, setRepoUrl] = useState('');
  const [repoName, setRepoName] = useState('');
  const [loading, setLoading] = useState(false);
  const [scanningRepoId, setScanningRepoId] = useState<string | null>(null);

  const handleAddRepository = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!repoUrl || !repoName) return;

    setLoading(true);
    const { error } = await addRepository(repoUrl, repoName, userId);

    if (error) {
      alert(`Error adding repository: ${error}`);
      setLoading(false);
      return;
    }

    setRepoUrl('');
    setRepoName('');
    setShowAddForm(false);
    setLoading(false);
    onRefresh();
  };

  const handleStartScan = async (repoId: string) => {
    setScanningRepoId(repoId);
    const { error } = await createScan(repoId);

    if (error) {
      alert(`Error starting scan: ${error}`);
      setScanningRepoId(null);
      return;
    }

    alert('Scan started successfully!');
    setScanningRepoId(null);
    onRefresh();
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4 sm:space-y-6"
    >
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <h2 className="text-xl sm:text-2xl lg:text-3xl font-headline font-bold bg-gradient-to-r from-neon-cyan to-neon-blue bg-clip-text text-transparent">
          📁 Your Repositories
        </h2>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setShowAddForm(!showAddForm)}
          className="flex items-center gap-2 px-4 sm:px-6 py-2 sm:py-3 text-sm sm:text-base bg-gradient-to-r from-neon-cyan/30 to-neon-blue/30 hover:from-neon-cyan/50 hover:to-neon-blue/50 text-neon-cyan border border-neon-cyan/50 rounded-lg transition-all duration-300 font-bold whitespace-nowrap"
        >
          <Plus className="w-4 h-4 sm:w-5 sm:h-5" />
          Add Repository
        </motion.button>
      </div>

      {/* Add Repository Form */}
      {showAddForm && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
        >
          <GlassFrame className="p-4 sm:p-6 lg:p-8 border border-neon-cyan/40">
            <h3 className="text-base sm:text-lg font-bold text-neon-cyan mb-4 sm:mb-6">Add New Repository</h3>
            <form onSubmit={handleAddRepository} className="space-y-4 sm:space-y-5">
              <div>
                <label className="block text-sm font-bold text-neon-cyan/90 mb-3">
                  Repository URL
                </label>
                <input
                  type="url"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  placeholder="https://github.com/username/repo"
                  className="w-full bg-card-bg border border-neon-cyan/30 hover:border-neon-cyan/60 rounded-lg py-3 px-4 text-on-background placeholder:text-outline/50 focus:border-neon-cyan focus:ring-2 focus:ring-neon-cyan/20 transition-all outline-none"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-bold text-neon-cyan/90 mb-3">
                  Repository Name
                </label>
                <input
                  type="text"
                  value={repoName}
                  onChange={(e) => setRepoName(e.target.value)}
                  placeholder="my-awesome-project"
                  className="w-full bg-card-bg border border-neon-cyan/30 hover:border-neon-cyan/60 rounded-lg py-3 px-4 text-on-background placeholder:text-outline/50 focus:border-neon-cyan focus:ring-2 focus:ring-neon-cyan/20 transition-all outline-none"
                  required
                />
              </div>
              <div className="flex flex-col sm:flex-row gap-3 pt-4">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-gradient-to-r from-neon-cyan to-neon-blue hover:from-neon-cyan/90 hover:to-neon-blue/90 text-dark-bg font-bold py-2.5 sm:py-3 text-sm sm:text-base rounded-lg transition-all duration-300 disabled:opacity-50"
                >
                  {loading ? 'Adding...' : 'Add Repository'}
                </motion.button>
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="px-4 sm:px-6 bg-surface-container-high hover:bg-surface-bright text-on-surface py-2.5 sm:py-3 text-sm sm:text-base rounded-lg transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </GlassFrame>
        </motion.div>
      )}

      {/* Repository Cards */}
      {repositories.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <GlassFrame className="p-12 text-center border border-neon-cyan/20">
            <Code2 className="w-20 h-20 text-neon-cyan/40 mx-auto mb-6" />
            <h3 className="text-2xl font-headline font-bold text-on-background mb-3">
              No Repositories Yet
            </h3>
            <p className="text-on-surface-variant mb-8">
              Add your first repository to start scanning for vulnerabilities with our AI-powered security engine
            </p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowAddForm(true)}
              className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-neon-cyan to-neon-blue text-dark-bg font-bold rounded-lg transition-all duration-300"
            >
              <Plus className="w-5 h-5" />
              Add Your First Repository
            </motion.button>
          </GlassFrame>
        </motion.div>
      ) : (
        <motion.div 
          className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ staggerChildren: 0.1 }}
        >
          {repositories.map((repo, idx) => (
            <motion.div
              key={repo.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
            >
              <GlassFrame className="p-4 sm:p-6 border-neon hover:border-neon-cyan card-hover relative overflow-hidden group">
                <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                
                <div className="flex items-start justify-between mb-4 relative z-10">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-neon-cyan/20 to-neon-blue/10 rounded-lg flex items-center justify-center group-hover:shadow-neon-cyan transition-shadow">
                      <GitBranch className="w-6 h-6 text-neon-cyan" />
                    </div>
                    <div>
                      <h3 className="font-headline font-bold text-on-background text-lg">
                        {repo.repo_name}
                      </h3>
                      <p className="text-xs text-neon-cyan/70 flex items-center gap-1 mt-1">
                        <Calendar className="w-3 h-3" />
                        {new Date(repo.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>

                <a
                  href={repo.repo_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-neon-cyan hover:text-neon-blue flex items-center gap-2 mb-5 break-all transition-colors relative z-10"
                >
                  <span className="truncate">{repo.repo_url}</span>
                  <ExternalLink className="w-3 h-3 flex-shrink-0" />
                </a>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => handleStartScan(repo.id)}
                  disabled={scanningRepoId === repo.id}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-neon-purple/30 to-neon-pink/20 hover:from-neon-purple/50 hover:to-neon-pink/40 text-neon-purple border border-neon-purple/50 rounded-lg transition-all duration-300 disabled:opacity-50 font-bold relative z-10"
                >
                  <Play className="w-4 h-4" />
                  {scanningRepoId === repo.id ? 'Starting Scan...' : 'Start Security Scan'}
                </motion.button>
              </GlassFrame>
            </motion.div>
          ))}
        </motion.div>
      )}
    </motion.div>
  );
}
