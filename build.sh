#!/bin/bash
set -e

echo "=========================================="
echo "Building Settlement Operation Guide"
echo "=========================================="

echo ""
echo "Step 1: Installing root dependencies..."
npm install

echo ""
echo "Step 2: Installing frontend dependencies..."
cd frontend
npm install

echo ""
echo "Step 3: Building frontend..."
npm run build

echo ""
echo "Step 4: Verifying build..."
cd ..
if [ -d "frontend/dist" ]; then
    echo "✓ Frontend build successful!"
    echo "✓ Files in frontend/dist:"
    ls -la frontend/dist
else
    echo "✗ Frontend build failed - dist directory not found!"
    exit 1
fi

echo ""
echo "=========================================="
echo "Build completed successfully!"
echo "=========================================="
