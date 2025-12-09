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

# Copy start script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Start backend server
CMD ["/app/start.sh"]
