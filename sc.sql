-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.ai_fixes (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  vulnerability_id uuid,
  suggested_fix text,
  fixed_code text,
  ai_model text DEFAULT 'deepseek-coder'::text,
  created_at timestamp without time zone DEFAULT now(),
  confidence_score double precision,
  CONSTRAINT ai_fixes_pkey PRIMARY KEY (id),
  CONSTRAINT ai_fixes_vulnerability_id_fkey FOREIGN KEY (vulnerability_id) REFERENCES public.vulnerabilities(id)
);
CREATE TABLE public.repositories (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid,
  repo_url text NOT NULL,
  repo_name text,
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT repositories_pkey PRIMARY KEY (id),
  CONSTRAINT repositories_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.scan_logs (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  scan_id uuid,
  log_message text,
  log_level text,
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT scan_logs_pkey PRIMARY KEY (id),
  CONSTRAINT scan_logs_scan_id_fkey FOREIGN KEY (scan_id) REFERENCES public.scans(id)
);
CREATE TABLE public.scans (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  repo_id uuid,
  status text DEFAULT 'pending'::text,
  total_vulnerabilities integer DEFAULT 0,
  scan_started_at timestamp without time zone,
  scan_completed_at timestamp without time zone,
  CONSTRAINT scans_pkey PRIMARY KEY (id),
  CONSTRAINT scans_repo_id_fkey FOREIGN KEY (repo_id) REFERENCES public.repositories(id)
);
CREATE TABLE public.users (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  email text NOT NULL UNIQUE,
  name text,
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT users_pkey PRIMARY KEY (id)
);
CREATE TABLE public.vulnerabilities (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  scan_id uuid,
  file_path text,
  vulnerability_type text,
  severity text,
  description text,
  line_number integer,
  detected_at timestamp without time zone DEFAULT now(),
  tool text,
  CONSTRAINT vulnerabilities_pkey PRIMARY KEY (id),
  CONSTRAINT vulnerabilities_scan_id_fkey FOREIGN KEY (scan_id) REFERENCES public.scans(id)
);