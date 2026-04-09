'use client';

import { useState } from 'react';
import { addRepository, createScan } from '@/lib/database';
import type { Repository } from '@/lib/types';
import { GitBranch, Plus, Play, ExternalLink, Calendar } from 'lucide-react';
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

  const handleAddRepository = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!repoUrl || !repoName) return;

    setLoading(true);
    const { data, error } = await addRepository(repoUrl, repoName, userId);

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
    const { data, error } = await createScan(repoId);

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
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-headline font-bold text-on-background">
          Repositories
        </h2>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="flex items-center gap-2 px-4 py-2 bg-primary/10 hover:bg-primary/20 text-primary rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Repository
        </button>
      </div>

      {/* Add Repository Form */}
      {showAddForm && (
        <GlassFrame className="p-6">
          <form onSubmit={handleAddRepository} className="space-y-4">
            <div>
              <label className="block text-sm font-bold text-on-surface-variant mb-2">
                Repository URL
              </label>
              <input
                type="url"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                placeholder="https://github.com/username/repo"
                className="w-full bg-surface-container-low border border-outline-variant/20 rounded-lg py-3 px-4 text-on-background placeholder:text-outline/50 focus:ring-2 focus:ring-primary/50 transition-all outline-none"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-on-surface-variant mb-2">
                Repository Name
              </label>
              <input
                type="text"
                value={repoName}
                onChange={(e) => setRepoName(e.target.value)}
                placeholder="my-awesome-project"
                className="w-full bg-surface-container-low border border-outline-variant/20 rounded-lg py-3 px-4 text-on-background placeholder:text-outline/50 focus:ring-2 focus:ring-primary/50 transition-all outline-none"
                required
              />
            </div>
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-primary hover:bg-primary-container text-on-primary-container font-bold py-3 rounded-lg transition-colors disabled:opacity-50"
              >
                {loading ? 'Adding...' : 'Add Repository'}
              </button>
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="px-6 bg-surface-container-high hover:bg-surface-bright text-on-surface py-3 rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </GlassFrame>
      )}

      {/* Repository Cards */}
      {repositories.length === 0 ? (
        <GlassFrame className="p-12 text-center">
          <GitBranch className="w-16 h-16 text-on-surface-variant/30 mx-auto mb-4" />
          <h3 className="text-xl font-headline font-bold text-on-background mb-2">
            No Repositories Yet
          </h3>
          <p className="text-on-surface-variant mb-6">
            Add your first repository to start scanning for vulnerabilities
          </p>
          <button
            onClick={() => setShowAddForm(true)}
            className="inline-flex items-center gap-2 px-6 py-3 bg-primary hover:bg-primary-container text-on-primary-container font-bold rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add Your First Repository
          </button>
        </GlassFrame>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {repositories.map((repo) => (
            <GlassFrame key={repo.id} className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                    <GitBranch className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-headline font-bold text-on-background">
                      {repo.repo_name}
                    </h3>
                    <p className="text-xs text-on-surface-variant flex items-center gap-1 mt-1">
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
                className="text-sm text-primary hover:text-primary-container flex items-center gap-1 mb-4 break-all"
              >
                {repo.repo_url}
                <ExternalLink className="w-3 h-3 flex-shrink-0" />
              </a>

              <div className="flex gap-3 mt-4">
                <button
                  onClick={() => handleStartScan(repo.id)}
                  disabled={scanningRepoId === repo.id}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-secondary/10 hover:bg-secondary/20 text-secondary rounded-lg transition-colors disabled:opacity-50"
                >
                  <Play className="w-4 h-4" />
                  {scanningRepoId === repo.id ? 'Starting...' : 'Start Scan'}
                </button>
              </div>
            </GlassFrame>
          ))}
        </div>
      )}
    </div>
  );
}
