#!/bin/bash
# quickstart.sh — Sets up the full dev environment
# Run once after cloning: ./scripts/quickstart.sh

set -e

echo "🏨 Marriott Bonvoy Enhanced Experience — CodeFest 4.0 Setup"
echo "================================"

# Check prerequisites
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required. Install from https://nodejs.org"; exit 1; }

# Pick a Python interpreter that has pre-built pydantic-core wheels.
# Python 3.14 lacks wheels and tries to compile from source (slow + fails behind some
# corp SSL setups), so we prefer 3.12 → 3.11 → 3.13 → 3 in that order.
PYTHON_BIN=""
for cand in python3.12 python3.11 python3.13 python3; do
  if command -v "$cand" >/dev/null 2>&1; then PYTHON_BIN="$cand"; break; fi
done
if [ -z "$PYTHON_BIN" ]; then
  echo "❌ Python 3.11+ is required."; exit 1
fi
echo "Using $PYTHON_BIN ($($PYTHON_BIN --version))"

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
  "$PYTHON_BIN" -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
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
