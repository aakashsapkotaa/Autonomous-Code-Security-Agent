# 🔒 SecureShift - AI-Powered Security Scanner

> Autonomous security vulnerability detection and AI-powered fix generation for your GitHub repositories

[![Next.js](https://img.shields.io/badge/Next.js-15.5-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Supabase-Powered-green)](https://supabase.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-blue)](https://python.org/)

## 🚀 Features

- **🔍 Multi-Tool Security Scanning**: Integrates Bandit, TruffleHog, and Safety for comprehensive vulnerability detection
- **🤖 AI-Powered Fix Generation**: Automatically generates code fixes using OpenRouter AI
- **📊 Real-time Dashboard**: Beautiful, responsive UI built with Next.js and Tailwind CSS
- **🔐 Secure Authentication**: Email/password authentication with Supabase
- **💾 Persistent Storage**: All scans, vulnerabilities, and fixes stored in Supabase PostgreSQL
- **⚡ Background Processing**: Non-blocking scan execution with FastAPI background tasks
- **🎨 Modern UI**: Cyberpunk-themed interface with particle animations and glass morphism

## 🏗️ Architecture

```
┌─────────────────┐
│  Next.js        │
│  Frontend       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI        │
│  Backend API    │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐
│ Bandit │ │Truffle │ │ Safety │ │OpenRouter│
│        │ │  Hog   │ │        │ │   AI     │
└────────┘ └────────┘ └────────┘ └──────────┘
         │
         ▼
┌─────────────────┐
│   Supabase      │
│   PostgreSQL    │
└─────────────────┘
```

## 📋 Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.12+
- **Git**
- **Supabase Account** (free tier works)
- **OpenRouter API Key** (for AI fixes)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/secureshift.git
cd secureshift
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

Edit `backend/.env`:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=nvidia/nemotron-3-super-120b-a12b:free
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.local.example .env.local
```

Edit `frontend/.env.local`:
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Database Setup

Run the SQL schema in your Supabase SQL editor:

```bash
# Copy the schema
cat infra/supabase/schema.sql
```

Paste and execute in Supabase Dashboard → SQL Editor

### 5. Install Security Tools

```bash
# Install Bandit (Python security)
pip install bandit

# Install TruffleHog (secrets detection)
# Download from: https://github.com/trufflesecurity/trufflehog/releases

# Install Safety (dependency checker)
pip install safety
```

## 🚀 Running the Application

### Start Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000
API Docs: http://localhost:8000/api/docs

### Start Frontend

```bash
cd frontend
npm run dev
```

Frontend will be available at: http://localhost:3000

## 📱 Usage

1. **Sign Up**: Create an account with email and password
2. **Add Repository**: Enter your GitHub repository URL
3. **Start Scan**: Click "Start Security Scan" to analyze the repository
4. **View Results**: See vulnerabilities with severity levels
5. **AI Fixes**: Get AI-generated fix suggestions for each vulnerability

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/signup` - Create new account
- `POST /api/auth/login` - Login

### Repositories
- `GET /api/repositories` - List repositories
- `POST /api/repositories` - Add repository
- `GET /api/repositories/{id}` - Get repository details

### Scans
- `POST /api/scans/trigger` - Start security scan
- `GET /api/scans/{id}` - Get scan status and results

### Vulnerabilities
- `GET /api/vulnerabilities/{id}` - Get vulnerability details
- `GET /api/vulnerabilities/scan/{scan_id}` - Get all vulnerabilities for a scan

### Chatbot
- `POST /api/chatbot/chat` - Ask AI assistant

## 🗄️ Database Schema

### Tables
- **users**: User accounts
- **repositories**: GitHub repositories
- **scans**: Security scan records
- **vulnerabilities**: Detected security issues
- **ai_fixes**: AI-generated fix suggestions
- **scan_logs**: Scan execution logs

## 🎨 Tech Stack

### Frontend
- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **Supabase Client** - Authentication & Database

### Backend
- **FastAPI** - Modern Python web framework
- **Supabase** - PostgreSQL database
- **Bandit** - Python security linter
- **TruffleHog** - Secret scanner
- **Safety** - Dependency vulnerability checker
- **OpenRouter** - AI API gateway

## 🔐 Security Tools

### Bandit
Analyzes Python code for common security issues:
- SQL injection
- Hardcoded passwords
- Insecure functions
- And more...

### TruffleHog
Scans for secrets and credentials:
- API keys
- Passwords
- Tokens
- Private keys

### Safety
Checks Python dependencies for known vulnerabilities using the PyUp.io database

## 🤖 AI Fix Generation

SecureShift uses OpenRouter to access powerful AI models for generating security fixes:

- **Model**: Nvidia Nemotron 3 Super 120B (free tier)
- **Confidence Scoring**: Each fix includes a confidence score
- **Context-Aware**: Fixes are generated based on vulnerability type, severity, and code context

## 📊 Features in Detail

### Responsive Design
- Mobile-first approach
- Works on phones, tablets, and desktops
- Adaptive layouts and touch-friendly controls

### Real-time Updates
- Background scan processing
- Live status updates
- Instant vulnerability detection

### User Experience
- Particle background animations
- Glass morphism UI elements
- Smooth transitions and interactions
- Cyberpunk aesthetic

## 🚧 Roadmap

- [ ] GitHub OAuth integration
- [ ] Webhook support for automatic scans
- [ ] Email notifications
- [ ] Scan scheduling
- [ ] Team collaboration features
- [ ] Custom security rules
- [ ] Export reports (PDF, JSON)
- [ ] Integration with CI/CD pipelines

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Team

Built with ❤️ for the hackathon

## 🙏 Acknowledgments

- Supabase for the amazing backend platform
- OpenRouter for AI API access
- The open-source security tools community
- Next.js and FastAPI teams

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

**Made with 🔒 by SecureShift Team**
