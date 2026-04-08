export interface User {
  id: string;
  email: string;
  name?: string;
  created_at: string;
}

export interface Repository {
  id: string;
  user_id?: string;
  repo_url: string;
  repo_name?: string;
  created_at: string;
}

export interface Scan {
  id: string;
  repo_id: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  total_vulnerabilities: number;
  scan_started_at?: string;
  scan_completed_at?: string;
}

export interface Vulnerability {
  id: string;
  scan_id: string;
  file_path?: string;
  vulnerability_type?: string;
  severity?: 'low' | 'medium' | 'high' | 'critical';
  description?: string;
  line_number?: number;
  detected_at: string;
}

export interface AiFix {
  id: string;
  vulnerability_id: string;
  suggested_fix?: string;
  fixed_code?: string;
  ai_model?: string;
  created_at: string;
}

export interface ScanLog {
  id: string;
  scan_id: string;
  log_message?: string;
  log_level?: 'info' | 'warning' | 'error';
  created_at: string;
}

export interface DatabaseResponse<T> {
  data: T | null;
  error: string | null;
}
