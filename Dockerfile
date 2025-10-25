# ===== Stage 1: Build =====
FROM python:3.12.10-slim AS builder

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --prefix=/install -r requirements.txt

# ===== Stage 2: Final image =====
FROM python:3.12.10-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Expose port if needed (not required for worker)
# EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app

# Entrypoint
CMD ["python", "main.py"]
