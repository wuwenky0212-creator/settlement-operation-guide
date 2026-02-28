#!/bin/bash
set -e

echo "=========================================="
echo "Starting Settlement Operation Guide"
echo "=========================================="

# Check if frontend/dist exists
if [ ! -d "frontend/dist" ]; then
    echo "Frontend dist not found, building..."
    cd frontend
    npm install
    npm run build
    cd ..
fi

# Verify dist exists
if [ -d "frontend/dist" ]; then
    echo "✓ Frontend dist found"
    echo "Files in frontend/dist:"
    ls -la frontend/dist | head -20
else
    echo "✗ Error: frontend/dist not found!"
    exit 1
fi

# Start the server
echo ""
echo "Starting Express server..."
node server.js
