#!/usr/bin/env bash
# ── Render Build Script ──────────────────────────────────────────────────────
# Installs Python deps + builds the React dashboard into dashboard/dist/

set -o errexit  # exit on error

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📦 Installing Node.js dependencies..."
cd dashboard
npm install

echo "🔨 Building React dashboard..."
npm run build
cd ..

echo "✅ Build complete!"
