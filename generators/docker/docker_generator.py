"""
Docker & Docker Compose Generator
Generates Dockerfiles for Frontend and Backend, docker-compose.yml for local multi-service testing,
and environment templates.
"""

import os
from typing import Dict, Any

def get_frontend_dockerfile() -> str:
    return """# Build stage for React Frontend
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage using lightweight Nginx
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
"""

def get_backend_dockerfile() -> str:
    return """# Production Python FastAPI Container
FROM python:3.11-slim
WORKDIR /app

# Prevent Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

def get_docker_compose() -> str:
    return """version: '3.8'

services:
  database:
    image: postgres:15-alpine
    container_name: cloud_postgres_db
    restart: always
    environment:
      POSTGRES_USER: clouduser
      POSTGRES_PASSWORD: cloudpassword123!
      POSTGRES_DB: cloud_product_db
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ../database/schema.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U clouduser -d cloud_product_db"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile
    container_name: cloud_backend_api
    restart: always
    environment:
      DATABASE_URL: postgresql://clouduser:cloudpassword123!@database:5432/cloud_product_db
      JWT_SECRET: supersecretjwtkey9876543210
      AWS_REGION: us-east-1
      S3_BUCKET_NAME: ai-product-storage-bucket
    ports:
      - "8000:8000"
    depends_on:
      database:
        condition: service_healthy

  frontend:
    build:
      context: ../frontend
      dockerfile: Dockerfile
    container_name: cloud_frontend_ui
    restart: always
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  pgdata:
"""

def generate_docker_files(output_dir: str, spec: Dict[str, Any] = None) -> Dict[str, str]:
    os.makedirs(output_dir, exist_ok=True)
    
    files = {
        "Dockerfile.frontend": get_frontend_dockerfile(),
        "Dockerfile.backend": get_backend_dockerfile(),
        "docker-compose.yml": get_docker_compose(),
        ".dockerignore": "node_modules\n.git\n__pycache__\n.venv\n*.log\n",
        ".env.example": "DATABASE_URL=postgresql://clouduser:cloudpassword123!@localhost:5432/cloud_product_db\nJWT_SECRET=replace_with_secure_random_key\nAWS_REGION=us-east-1\n"
    }
    
    generated = {}
    for filename, content in files.items():
        path = os.path.join(output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        generated[filename] = path
        
    return generated

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "./output/docker"
    res = generate_docker_files(target)
    print(f"Docker files generated at: {res}")
