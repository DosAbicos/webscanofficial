#!/bin/bash
set -e

echo "Installing backend dependencies..."
pip install -r backend/requirements.txt

echo "Installing frontend dependencies..."
cd frontend
npm install --legacy-peer-deps

echo "Building frontend..."
npm run build

echo "Build complete!"
