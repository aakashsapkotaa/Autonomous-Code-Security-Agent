#!/bin/bash

# SecureShift Setup Script

echo "🔒 Setting up SecureShift..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Backend setup
echo "📦 Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
echo "✅ Backend setup complete"

# Frontend setup
echo "📦 Setting up frontend..."
cd ../frontend
npm install
cp .env.local.example .env.local
echo "✅ Frontend setup complete"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your Supabase and OpenRouter credentials"
echo "2. Edit frontend/.env.local with your Supabase URL and keys"
echo "3. Run the database schema in Supabase (infra/supabase/schema.sql)"
echo "4. Start backend: cd backend && python -m uvicorn app.main:app --reload"
echo "5. Start frontend: cd frontend && npm run dev"
echo ""
echo "📚 See README.md for detailed instructions"
