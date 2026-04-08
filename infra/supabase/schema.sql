-- USERS TABLE
create table users (
  id uuid primary key default gen_random_uuid(),
  email text unique not null,
  name text,
  created_at timestamp default now()
);

-- REPOSITORIES TABLE
create table repositories (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  repo_url text not null,
  repo_name text,
  created_at timestamp default now()
);

-- SCANS TABLE
create table scans (
  id uuid primary key default gen_random_uuid(),
  repo_id uuid references repositories(id) on delete cascade,
  status text default 'pending',
  total_vulnerabilities integer default 0,
  scan_started_at timestamp,
  scan_completed_at timestamp
);

-- VULNERABILITIES TABLE
create table vulnerabilities (
  id uuid primary key default gen_random_uuid(),
  scan_id uuid references scans(id) on delete cascade,
  file_path text,
  vulnerability_type text,
  severity text,
  description text,
  line_number integer,
  detected_at timestamp default now()
);

-- AI FIXES TABLE
create table ai_fixes (
  id uuid primary key default gen_random_uuid(),
  vulnerability_id uuid references vulnerabilities(id) on delete cascade,
  suggested_fix text,
  fixed_code text,
  ai_model text default 'deepseek-coder',
  confidence_score float default 0.5,
  created_at timestamp default now()
);

-- Index for faster lookups
create index idx_ai_fixes_vuln_id on ai_fixes(vulnerability_id);

-- SCAN LOGS TABLE
create table scan_logs (
  id uuid primary key default gen_random_uuid(),
  scan_id uuid references scans(id) on delete cascade,
  log_message text,
  log_level text,
  created_at timestamp default now()
);

-- Additional indexes for performance
create index idx_vulnerabilities_scan_id on vulnerabilities(scan_id);
create index idx_vulnerabilities_severity on vulnerabilities(severity);
create index idx_scans_repo_id on scans(repo_id);
create index idx_scans_status on scans(status);
create index idx_repositories_user_id on repositories(user_id);