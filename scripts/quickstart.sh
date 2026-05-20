#!/bin/bash
# quickstart.sh — Sets up the full dev environment
# Run once after cloning: ./scripts/quickstart.sh

set -e

echo "🏨 Marriott Bonvoy Enhanced Experience — CodeFest 4.0 Setup"
echo "================================"

# Check prerequisites
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required. Install from https://nodejs.org"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3.11+ is required."; exit 1; }

echo ""
echo "1. Setting up frontend..."
cd frontend
if [ ! -f ".env.local" ]; then
  cp .env.example .env.local
  echo "   ✅ Created frontend/.env.local — add your NEXT_PUBLIC_MAPBOX_TOKEN"
else
  echo "   ⏭  frontend/.env.local already exists"
fi

if [ ! -d "node_modules" ]; then
  npm install
  echo "   ✅ Frontend dependencies installed"
else
  echo "   ⏭  node_modules already present"
fi
cd ..

echo ""
echo "2. Setting up backend..."
cd backend
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "   ✅ Created backend/.env — add your OPENWEATHER_API_KEY"
else
  echo "   ⏭  backend/.env already exists"
fi

if [ ! -d "venv" ]; then
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  echo "   ✅ Backend virtualenv created and dependencies installed"
else
  echo "   ⏭  venv already present"
fi
cd ..

echo ""
echo "================================"
echo "✅ Setup complete!"
echo ""
echo "To start development:"
echo "  Frontend: cd frontend && npm run dev   (http://localhost:3000)"
echo "  Backend:  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "Or use Docker: docker-compose up"
echo ""
echo "Next steps:"
echo "  1. Add your Mapbox token to frontend/.env.local"
echo "  2. Add your OpenWeatherMap key to backend/.env"
echo "  3. Read APP_PRD.md for full feature specs"
