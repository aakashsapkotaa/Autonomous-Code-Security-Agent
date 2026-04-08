# SecureShift - Autonomous Code Security Agent

<div align="center">

![SecureShift Banner](https://img.shields.io/badge/SecureShift-Autonomous%20Security-white?style=for-the-badge)

**Next-generation security analysis powered by AI agents and cloud-native tools**

[![Next.js](https://img.shields.io/badge/Next.js-15.1-black?style=flat-square&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)](https://python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8-blue?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-orange?style=flat-square)](LICENSE)

</div>

---

## 🚀 Overview

SecureShift is an autonomous code security agent that automatically detects vulnerabilities in your GitHub repositories and provides AI-powered fix suggestions. Built with a modern microservices architecture designed for scalability on AWS Free Tier.

### ✅ Implementation Status

- ✅ **Frontend** (100%) - Complete Next.js UI with authentication, dashboard, and repository management
- ✅ **Backend** (100%) - Full FastAPI implementation with all routes and services
- ✅ **Database** (100%) - Supabase integration with complete CRUD operations
- ✅ **MCP Agents** (100%) - All three agents fully implemented (Orchestrator, Fixer, Reporter)
- ✅ **Security Tools** (100%) - Bandit, TruffleHog, Safety integration complete
- ✅ **GitHub Integration** (100%) - OAuth and webhook handlers implemented
- ✅ **Celery Worker** (100%) - Background task processing ready
- ✅ **Tests** (100%) - Unit tests for core functionality

### Key Features

- 🤖 **AI-Powered Analysis** - Multi-agent system with Orchestrator, Fixer, and Reporter agents
- 🔍 **Comprehensive Security Scanning** - Integrates Bandit, TruffleHog, Safety, and NVD API
- ⚡ **Real-time Monitoring** - GitHub Actions integration for automated scanning
- 🎨 **Modern UI** - Cyberpunk-inspired design with glass-morphism effects
- 📊 **Interactive Dashboard** - View vulnerabilities, AI fixes, and scan logs
- 🔐 **Secure by Design** - Row Level Security (RLS) with Supabase
- 🌐 **Serverless Architecture** - FastAPI backend with Redis Docker and Celery Worker

---

## 📁 Project Structure

```
project-root/
├── .github/
│   └── workflows/                # GitHub Actions CI/CD
│       ├── deploy-frontend.yml
│       ├── deploy-backend.yml
│       └── security-scan.yml
│
├── frontend/                     # Next.js frontend (Vercel / AWS Amplify)
│   ├── public/
│   ├── src/
│   │   ├── app/                  # App Router
│   │   ├── components/
│   │   └── lib/                  # API client for backend
│   ├── package.json
│   └── next.config.ts
│
├── backend/                      # FastAPI backend
│   ├── app/
│   │   ├── main.py               # FastAPI entrypoint
│   │   ├── api/                  # REST endpoints
│   │   │   └── routes/
│   │   ├── core/                 # config, dependencies
│   │   ├── models/               # Pydantic / SQLModel
│   │   └── services/             # business logic, call to MCP layer
│   ├── requirements.txt
│   ├── Dockerfile
│   └── celery_worker.py
│
├── mcp_agents/                   # MCP Agent Layer
│   ├── orchestrator/
│   │   └── agent.py
│   ├── fixer/
│   │   ├── agent.py
│   │   └── deepseek_client.py    # Ollama + DeepSeek Coder
│   ├── reporter/
│   │   └── agent.py
│   ├── supabase_client.py        # MCP-based Supabase (PostgreSQL) access
│   └── requirements.txt
│
├── security/                     # Security tools configuration
│   ├── bandit/
│   │   └── bandit.yaml
│   ├── trufflehog/
│   │   └── trufflehog.yml
│   ├── safety/
│   │   └── safety-policy.yml
│   ├── nvd_api/
│   │   └── nvd_fetcher.py
│   └── ollama_sec/               # Ollama security scanning scripts
│       └── scan.py
│
├── docker/                       # Docker compose for local / EC2
│   ├── docker-compose.yml        # Redis, Celery, Backend, Agents
│   ├── Dockerfile.backend
│   └── Dockerfile.agent
│
├── infra/                        # AWS & Supabase infra as code
│   ├── terraform/                # EC2, S3, IAM
│   └── supabase/                 # schema migrations, RLS policies
│
├── scripts/                      # Utility scripts
│   ├── run_celery.sh
│   ├── start_agents.sh
│   └── security_scan_all.sh
│
├── .env.example                  # Environment variables template
├── .gitignore
└── README.md
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│  Next.js Frontend (Vercel / AWS Amplify Free Tier)            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GITHUB INTEGRATION                           │
│  GitHub Repo ──► GitHub Actions ──► Webhook Trigger           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Redis Docker │  │ Celery Worker│  │  S3 Bucket   │        │
│  │   (Queue)    │  │  (Tasks)     │  │ Reports/Logs │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MCP AGENT LAYER                              │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  Orchestrator Agent (Coordinates workflow)             │   │
│  │  Fixer Agent (Ollama + DeepSeek Coder)                │   │
│  │  Reporter Agent (Generates reports)                    │   │
│  └────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY TOOLS                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  Bandit  │  │TruffleHog│  │  Safety  │  │ NVD API  │      │
│  │  Ollama  │  (Secrets)  │  │  (Deps)  │  │  (CVEs)  │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER                               │
│  Supabase (PostgreSQL via MCP)                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📚 Documentation

- **[README.md](README.md)** - This file - Project overview and quick start
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete deployment instructions
- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Current implementation status
- **[AI_FIX_WORKFLOW.md](AI_FIX_WORKFLOW.md)** - AI fix generation workflow

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- Supabase account
- (Optional) Ollama for local LLM

### 1. Clone Repository

```bash
git clone https://github.com/aakashsapkotaa/Autonomous-Code-Security-Agent.git
cd Autonomous-Code-Security-Agent
```

### 2. Setup Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Start Services with Docker

```bash
cd docker
docker-compose up -d
```

This starts:
- Redis (port 6379)
- FastAPI Backend (port 8000)
- Celery Worker
- MCP Agents (ports 8001-8003)

### 4. Setup Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on [http://localhost:3000](http://localhost:3000)

### 5. Setup Database

```bash
# Apply schema
cd infra/supabase
# Run schema.sql in Supabase SQL Editor
```

---

## 📚 Documentation

- [Quick Start Guide](QUICK_START.md)
- [Project Status](PROJECT_STATUS.md)
- [Deployment Guide](DEPLOYMENT_READY.md)
- [Security Guide](SECURITY_FIX_GUIDE.md)

---

## 🔧 Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Run Security Scans

```bash
bash scripts/security_scan_all.sh
```

### Start MCP Agents

```bash
bash scripts/start_agents.sh
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 🚢 Deployment

### Frontend (Vercel)

```bash
cd frontend
vercel --prod
```

### Backend (AWS EC2)

```bash
# See .github/workflows/deploy-backend.yml
```

---

## 📊 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS 4 |
| Backend | FastAPI, Python 3.11 |
| Database | Supabase (PostgreSQL) |
| Task Queue | Celery + Redis |
| AI/LLM | Ollama + DeepSeek Coder |
| Security Tools | Bandit, TruffleHog, Safety, NVD API |
| Infrastructure | Docker, AWS EC2, S3 |
| CI/CD | GitHub Actions |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE) file

---

## 👥 Authors

- **Aakash Sapkota** - [@aakashsapkotaa](https://github.com/aakashsapkotaa)

---

## 🙏 Acknowledgments

- Next.js team
- FastAPI team
- Supabase team
- All open-source security tools

---

<div align="center">

**Built with ❤️ using Next.js, FastAPI, Supabase, and AI**

[Website](https://secureshift.vercel.app) • [Documentation](https://github.com/aakashsapkotaa/Autonomous-Code-Security-Agent/wiki) • [Report Bug](https://github.com/aakashsapkotaa/Autonomous-Code-Security-Agent/issues)

</div>
