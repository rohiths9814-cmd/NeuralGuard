# ══════════════════════════════════════════════════════════════════════════════
# NeuralGuard — Multi-stage Dockerfile for Google Cloud Run
# Stage 1: Build React dashboard
# Stage 2: Serve everything with Python/FastAPI
# ══════════════════════════════════════════════════════════════════════════════

# ── Stage 1: Build the React Dashboard ───────────────────────────────────────
FROM node:20-slim AS dashboard-build

WORKDIR /app/dashboard

# Install dependencies first (cache layer)
COPY dashboard/package.json dashboard/package-lock.json ./
RUN npm ci --production=false

# Copy source and build
COPY dashboard/ ./
RUN npm run build


# ── Stage 2: Python Backend + Static Dashboard ──────────────────────────────
FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr (important for Cloud Run logs)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install Python dependencies first (cache layer)
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the backend source code
COPY server/ ./server/

# Copy the built React dashboard from Stage 1
COPY --from=dashboard-build /app/dashboard/dist ./dashboard/dist

# Copy environment example (actual env vars come from Cloud Run config)
COPY .env.example ./

# Cloud Run provides PORT env var (default 8080)
ENV PORT=8080

# Expose the port
EXPOSE 8080

# Start the server
# Cloud Run sends SIGTERM for graceful shutdown, uvicorn handles it
CMD uvicorn server.main:app --host 0.0.0.0 --port ${PORT} --workers 1
