import { supabase } from './supabaseClient';
import type { Repository, Scan, Vulnerability, AiFix, DatabaseResponse } from './types';

/**
 * Fetch all repositories
 */
export async function getRepositories(): Promise<DatabaseResponse<Repository[]>> {
  try {
    const { data, error } = await supabase
      .from('repositories')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error fetching repositories:', error);
      return { data: null, error: error.message || 'Failed to fetch repositories' };
    }

    return { data: data || [], error: null };
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    console.error('Exception fetching repositories:', message);
    return { data: null, error: message };
  }
}

/**
 * Add a new repository
 */
export async function addRepository(
  repoUrl: string,
  repoName: string,
  userId: string
): Promise<DatabaseResponse<Repository>> {
  try {
    if (!userId) {
      return { data: null, error: 'User ID is required' };
    }

    const { data, error } = await supabase
      .from('repositories')
      .insert([
        {
          repo_url: repoUrl,
          repo_name: repoName,
          user_id: userId,
        },
      ])
      .select()
      .single();

    if (error) {
      console.error('Error adding repository:', error);
      console.error('Error details:', JSON.stringify(error, null, 2));
      return { data: null, error: error.message || error.hint || 'Failed to add repository' };
    }

    return { data, error: null };
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    console.error('Exception adding repository:', message);
    return { data: null, error: message };
  }
}

/**
 * Create a new scan for a repository
 */
export async function createScan(repoId: string): Promise<DatabaseResponse<Scan>> {
  try {
    const { data, error } = await supabase
      .from('scans')
      .insert([
        {
          repo_id: repoId,
          status: 'pending',
          scan_started_at: new Date().toISOString(),
        },
      ])
      .select()
      .single();

    if (error) {
      console.error('Error creating scan:', error);
      return { data: null, error: error.message };
    }

    return { data, error: null };
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    console.error('Exception creating scan:', message);
    return { data: null, error: message };
  }
}

/**
 * Fetch vulnerabilities for a specific scan
 */
export async function getVulnerabilities(
  scanId: string
): Promise<DatabaseResponse<Vulnerability[]>> {
  try {
    const { data, error } = await supabase
      .from('vulnerabilities')
      .select('*')
      .eq('scan_id', scanId)
      .order('severity', { ascending: false });

    if (error) {
      console.error('Error fetching vulnerabilities:', error);
      return { data: null, error: error.message };
    }

    return { data: data || [], error: null };
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    console.error('Exception fetching vulnerabilities:', message);
    return { data: null, error: message };
  }
}

/**
 * Fetch AI fixes for a specific vulnerability
 */
export async function getAiFixes(
  vulnerabilityId: string
): Promise<DatabaseResponse<AiFix[]>> {
  try {
    const { data, error } = await supabase
      .from('ai_fixes')
      .select('*')
      .eq('vulnerability_id', vulnerabilityId)
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error fetching AI fixes:', error);
      return { data: null, error: error.message };
    }

    return { data: data || [], error: null };
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    console.error('Exception fetching AI fixes:', message);
    return { data: null, error: message };
  }
}

/**
 * Fetch scans for a specific repository
 */
export async function getScans(repoId: string): Promise<DatabaseResponse<Scan[]>> {
  try {
    const { data, error } = await supabase
      .from('scans')
      .select('*')
      .eq('repo_id', repoId)
      .order('scan_started_at', { ascending: false });

    if (error) {
      console.error('Error fetching scans:', error);
      return { data: null, error: error.message };
    }

    return { data: data || [], error: null };
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    console.error('Exception fetching scans:', message);
    return { data: null, error: message };
  }
}

/**
 * Get repository with its latest scan
 */
export async function getRepositoryWithLatestScan(
  repoId: string
): Promise<DatabaseResponse<Repository & { latest_scan?: Scan }>> {
  try {
    const { data: repo, error: repoError } = await supabase
      .from('repositories')
      .select('*')
      .eq('id', repoId)
      .single();

    if (repoError) {
      return { data: null, error: repoError.message };
    }

    const { data: scans, error: scanError } = await supabase
      .from('scans')
      .select('*')
      .eq('repo_id', repoId)
      .order('scan_started_at', { ascending: false })
      .limit(1);

    if (scanError) {
      return { data: repo, error: null };
    }

    return {
      data: {
        ...repo,
        latest_scan: scans?.[0] || undefined,
      },
      error: null,
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    return { data: null, error: message };
  }
}
