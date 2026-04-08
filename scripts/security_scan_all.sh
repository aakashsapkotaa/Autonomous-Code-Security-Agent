#!/bin/bash
# Run all security scans

echo "Running Bandit (Python security)..."
bandit -r backend/ mcp_agents/ -c security/bandit/bandit.yaml -f json -o reports/bandit-report.json

echo "Running Safety (Dependency check)..."
cd backend && safety check --json > ../reports/safety-report.json && cd ..

echo "Running TruffleHog (Secret detection)..."
truffleHog --json --regex --entropy=False . > reports/trufflehog-report.json

echo "All security scans complete! Reports in reports/ directory"
