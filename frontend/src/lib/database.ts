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
  userId: string | null
): Promise<DatabaseResponse<Repository>> {
  try {
    // If userId is provided, ensure user exists in users table
    if (userId) {
      const { data: existingUser } = await supabase
        .from('users')
        .select('id')
        .eq('id', userId)
        .single();

      // If user doesn't exist, create them
      if (!existingUser) {
        const { data: authUser } = await supabase.auth.getUser();
        if (authUser?.user) {
          await supabase
            .from('users')
            .insert([
              {
                id: userId,
                email: authUser.user.email || '',
                name: authUser.user.user_metadata?.full_name || authUser.user.email?.split('@')[0] || 'User',
              },
            ]);
        }
      }
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
    // First, get the repository details
    const { data: repo, error: repoError } = await supabase
      .from('repositories')
      .select('*')
      .eq('id', repoId)
      .single();

    if (repoError || !repo) {
      console.error('Error fetching repository:', repoError);
      return { data: null, error: 'Repository not found' };
    }

    // Create scan record
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

    // Trigger the actual scan by calling the backend API
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      console.log('Triggering scan via backend API:', `${apiUrl}/api/scans/trigger`);
      
      const scanResponse = await fetch(`${apiUrl}/api/scans/trigger`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          scan_id: data.id,
          repo_url: repo.repo_url,
          repo_id: repoId,
        }),
      });

      if (!scanResponse.ok) {
        console.error('Failed to trigger scan:', await scanResponse.text());
        // Update scan status to failed
        await supabase
          .from('scans')
          .update({ status: 'failed' })
          .eq('id', data.id);
        return { data: null, error: 'Failed to trigger scan execution' };
      }

      console.log('Scan triggered successfully');
    } catch (triggerError) {
      console.error('Error triggering scan:', triggerError);
      // Update scan status to failed
      await supabase
        .from('scans')
        .update({ status: 'failed' })
        .eq('id', data.id);
      return { data: null, error: 'Failed to trigger scan execution' };
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
