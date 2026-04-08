#!/bin/bash

# SecureShift Setup Script
# Automates initial setup for development environment

set -e

echo "🚀 SecureShift Setup Script"
echo "============================"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed. Aborting."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed. Aborting."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting."; exit 1; }

echo "✅ All prerequisites met!"
echo ""

# Setup environment file
echo "🔧 Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo "⚠️  Please edit .env with your credentials before continuing"
    echo ""
    read -p "Press Enter after editing .env file..."
else
    echo "✅ .env file already exists"
fi
echo ""

# Install backend dependencies
echo "🐍 Installing backend dependencies..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Created Python virtual environment"
fi

source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
pip install -r requirements.txt
echo "✅ Backend dependencies installed"
cd ..
echo ""

# Install MCP agents dependencies
echo "🤖 Installing MCP agents dependencies..."
cd mcp_agents
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Created Python virtual environment for agents"
fi

source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
pip install -r requirements.txt
echo "✅ MCP agents dependencies installed"
cd ..
echo ""

# Install frontend dependencies
echo "⚛️  Installing frontend dependencies..."
cd frontend
npm install
echo "✅ Frontend dependencies installed"
cd ..
echo ""

# Start Docker services
echo "🐳 Starting Docker services..."
cd docker
docker-compose up -d
echo "✅ Docker services started"
cd ..
echo ""

# Check Ollama
echo "🤖 Checking Ollama installation..."
if command -v ollama >/dev/null 2>&1; then
    echo "✅ Ollama is installed"
    echo "📥 Pulling DeepSeek Coder model (this may take a while)..."
    ollama pull deepseek-coder:6.7b || echo "⚠️  Failed to pull model. You can do this manually later."
else
    echo "⚠️  Ollama not found. Install from https://ollama.com"
    echo "   After installation, run: ollama pull deepseek-coder:6.7b"
fi
echo ""

# Summary
echo "✅ Setup Complete!"
echo ""
echo "📝 Next Steps:"
echo "1. Ensure your .env file has correct Supabase credentials"
echo "2. Apply database schema from infra/supabase/schema.sql to Supabase"
echo "3. Start the backend:"
echo "   cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "4. Start MCP agents:"
echo "   bash scripts/start_agents.sh"
echo "5. Start the frontend:"
echo "   cd frontend && npm run dev"
echo ""
echo "🌐 Access points:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/api/docs"
echo "   Orchestrator: http://localhost:8001"
echo "   Fixer: http://localhost:8002"
echo "   Reporter: http://localhost:8003"
echo ""
echo "📚 Documentation:"
echo "   README.md - Project overview"
echo "   DEPLOYMENT_GUIDE.md - Deployment instructions"
echo ""
echo "Happy coding! 🎉"
