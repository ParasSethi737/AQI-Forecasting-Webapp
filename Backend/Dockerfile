# ---- Stage 1: Builder ----
    FROM python:3.11-slim AS builder

    # Prevent Python from writing .pyc files and buffering stdout/stderr
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1
    
    WORKDIR /app
    
    # Install only the build deps we need (e.g. gcc for C extensions)
    RUN apt-get update \
     && apt-get install -y --no-install-recommends \
          build-essential gcc \
     && rm -rf /var/lib/apt/lists/*
    
    # Copy only requirements to leverage Docker layer caching
    COPY requirements.txt .
    
    # Upgrade pip, install into a custom prefix
    RUN pip install --upgrade pip \
     && pip install --no-cache-dir --prefix=/install -r requirements.txt
    
    
    # ---- Stage 2: Runtime ----
    FROM python:3.11-slim
    
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1
    
    WORKDIR /app
    
    # Copy just the Python packages we built in the builder stage
    COPY --from=builder /install /usr/local
    
    # Copy application code
    COPY . .
    
    # Expose Flask port
    EXPOSE 5000
    
    # Run with Gunicorn
    CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]