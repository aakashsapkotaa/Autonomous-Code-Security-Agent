<div align="center">

# 🔒 SecureShift

**AI-Powered Autonomous Code Security SaaS**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![SvelteKit](https://img.shields.io/badge/SvelteKit-2.0-FF3E00?style=flat-square&logo=svelte)](https://kit.svelte.dev)
[![Supabase](https://img.shields.io/badge/Supabase-2.9-3ECF8E?style=flat-square&logo=supabase)](https://supabase.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat-square&logo=typescript)](https://typescriptlang.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

SecureShift automatically scans your GitHub repositories for security vulnerabilities, generates AI-powered fix suggestions, and creates pull requests — all in one click.

[Features](#features) · [Quick Start](#quick-start) · [Architecture](#architecture) · [API Docs](#api) · [Contributing](#contributing)

</div>

---

## ✨ Features

- **🔍 Automated Security Scanning** — Runs Bandit, Safety, and CVE lookups on every repository
- **🤖 AI Fix Generation** — Uses LLMs via OpenRouter to generate context-aware code fixes
- **🔀 One-Click PR Creation** — Automatically applies fixes and opens a GitHub Draft PR
- **📊 Admin Dashboard** — Full platform management with analytics, audit logs, and user management
- **🔐 Role-Based Access Control** — User, Admin, Super Admin, and Enterprise Manager roles
- **🌐 CVE Integration** — Real-time CVE lookup via NVD API
- **⚡ Real-time Updates** — Live scan status via Supabase Realtime

## 🏗️ Project Structure

```
secureshift/
│
├── frontend/                    # SvelteKit frontend
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/      # Reusable UI components
│   │   │   │   └── admin/       # Admin-specific components
│   │   │   ├── api.ts           # API client helpers
│   │   │   ├── adminApi.ts      # Admin API client
│   │   │   └── supabaseClient.ts
│   │   └── routes/
│   │       ├── +page.svelte     # Landing page
│   │       ├── admin/           # Admin dashboard
│   │       ├── dashboard/       # User dashboard
│   │       └── auth/            # Auth callbacks
│   ├── package.json
│   └── .env.example
│
├── backend/                     # FastAPI backend
│   ├── app/
│   │   ├── api/routes/          # API route handlers
│   │   ├── core/                # Config, auth, DB, RBAC
│   │   ├── models/              # Pydantic models
│   │   ├── services/            # Business logic
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── infra/
│   ├── supabase/migrations/     # Database migrations
│   └── terraform/               # Infrastructure as code
│
├── mcp_agents/                  # MCP AI agents
│   └── fixer/
│
├── docs/                        # Documentation
│   ├── architecture.md
│   ├── api.md
│   ├── deployment.md
│   └── admin-dashboard.md
│
├── .github/workflows/           # CI/CD pipelines
├── README.md
├── LICENSE
└── .gitignore
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- A [Supabase](https://supabase.com) project

### 1. Clone the repository
```bash
git clone https://github.com/your-username/secureshift.git
cd secureshift
```

### 2. Backend setup
```bash
cd backend
cp .env.example .env
# Fill in your credentials in .env

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload
# Backend running at http://localhost:8000
```

### 3. Frontend setup
```bash
cd frontend
cp .env.example .env
# Fill in your Supabase credentials

npm install
npm run dev
# Frontend running at http://localhost:5173
```

### 4. Access the app
- **App**: http://localhost:5173
- **API Docs**: http://localhost:8000/api/docs
- **Admin**: http://localhost:5173/admin *(requires admin role)*

## ⚙️ Configuration

### Backend environment variables
| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | ✅ | Your Supabase project URL |
| `SUPABASE_KEY` | ✅ | Supabase anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ | Supabase service role key |
| `OPENROUTER_API_KEY` | ✅ | OpenRouter API key for AI fixes |
| `GITHUB_TOKEN` | ⚠️ | GitHub token for PR creation |
| `NVD_API_KEY` | ⚠️ | NVD API key for CVE lookup |

### Frontend environment variables
| Variable | Required | Description |
|----------|----------|-------------|
| `PUBLIC_SUPABASE_URL` | ✅ | Supabase project URL |
| `PUBLIC_SUPABASE_ANON_KEY` | ✅ | Supabase anon key |
| `PUBLIC_API_URL` | ✅ | Backend API URL |

## 📖 API

Interactive API documentation is available at `/api/docs` when the backend is running.

See [docs/api.md](docs/api.md) for the full API reference.

## 🏛️ Architecture

See [docs/architecture.md](docs/architecture.md) for the full architecture overview.

## 🚢 Deployment

See [docs/deployment.md](docs/deployment.md) for deployment instructions.

## 🔐 Security

- All API keys and secrets must be stored in `.env` files (never committed)
- Admin endpoints are protected by RBAC middleware
- All admin actions are logged in the audit trail
- Supabase RLS policies protect data at the database level

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'feat: add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
Built with ❤️ by the SecureShift team
</div>
