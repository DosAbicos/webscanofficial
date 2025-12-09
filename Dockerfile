# Multi-stage build for Railway

# Stage 1: Build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install --frozen-lockfile
COPY frontend/ ./
RUN yarn build

# Stage 2: Setup backend
FROM python:3.11-slim
WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy built frontend
COPY --from=frontend-build /app/frontend/build ./frontend/build
COPY frontend/public/sample_file.xls ./frontend/public/

# Set working directory to backend
WORKDIR /app/backend

# Railway provides PORT env variable
ENV PORT=8001

# Start backend server (Railway will set PORT dynamically)
CMD uvicorn server:app --host 0.0.0.0 --port ${PORT}
