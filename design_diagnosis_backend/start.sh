#!/bin/bash

###############################################################################
# Design Diagnosis Backend — Startup Script
# 
# Usage:
#   ./start.sh          # Start backend on port 8000
#   ./start.sh 9000     # Start backend on port 9000
#
###############################################################################

# Configuration
PORT=${1:-8000}
LOG_FILE="backend.log"

echo "🚀 Design Diagnosis Backend (Phase 2)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

echo "✅ Python $(python3 --version | awk '{print $2}')"

# Check dependencies
echo "📦 Checking dependencies..."
python3 -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Dependencies not installed. Installing..."
    pip install -r requirements.txt
fi

echo "✅ Dependencies ready"
echo ""

# Create report directory
mkdir -p ../design-diagnosis-app/reports

echo "📝 Logs: $LOG_FILE"
echo "🌐 URL: http://localhost:$PORT"
echo "📋 Health: http://localhost:$PORT/health"
echo "🎯 Form: http://localhost:$PORT/form.html"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start backend
python3 -m uvicorn main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --reload \
    --log-level info \
    2>&1 | tee $LOG_FILE
