-- Migration: Add confidence_score to ai_fixes table
-- Date: 2026-04-09
-- Description: Adds confidence_score column and indexes for better performance

-- Add confidence_score column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'ai_fixes' AND column_name = 'confidence_score'
    ) THEN
        ALTER TABLE ai_fixes ADD COLUMN confidence_score FLOAT DEFAULT 0.5;
    END IF;
END $$;

-- Add default value for ai_model if not set
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'ai_fixes' AND column_name = 'ai_model'
    ) THEN
        ALTER TABLE ai_fixes ALTER COLUMN ai_model SET DEFAULT 'deepseek-coder';
    END IF;
END $$;

-- Create indexes if they don't exist
CREATE INDEX IF NOT EXISTS idx_ai_fixes_vuln_id ON ai_fixes(vulnerability_id);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_scan_id ON vulnerabilities(scan_id);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_severity ON vulnerabilities(severity);
CREATE INDEX IF NOT EXISTS idx_scans_repo_id ON scans(repo_id);
CREATE INDEX IF NOT EXISTS idx_scans_status ON scans(status);
CREATE INDEX IF NOT EXISTS idx_repositories_user_id ON repositories(user_id);

-- Add tool column to vulnerabilities if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'vulnerabilities' AND column_name = 'tool'
    ) THEN
        ALTER TABLE vulnerabilities ADD COLUMN tool TEXT;
    END IF;
END $$;

-- Update existing records to have default confidence score
UPDATE ai_fixes SET confidence_score = 0.5 WHERE confidence_score IS NULL;

-- Add comment to confidence_score column
COMMENT ON COLUMN ai_fixes.confidence_score IS 'AI model confidence score (0.0 to 1.0)';

-- Verify migration
SELECT 
    'ai_fixes' as table_name,
    column_name,
    data_type,
    column_default
FROM information_schema.columns
WHERE table_name = 'ai_fixes'
ORDER BY ordinal_position;
