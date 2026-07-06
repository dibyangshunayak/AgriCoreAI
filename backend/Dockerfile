# Stage 1: Build dependencies and install packages
FROM python:3.10-slim AS builder

WORKDIR /build

# Install build dependencies required for compiling some packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Stage 2: Final production image
FROM python:3.10-slim AS final

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Expose production port
EXPOSE 8000

# Set production environment variables
ENV PYTHONPATH=/app
ENV PORT=8000
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create non-root system user and configure data/upload folder permissions
RUN useradd -u 1001 -m appuser \
    && mkdir -p /app/data /app/uploads \
    && chown -R appuser:appuser /app

USER appuser

# Run Gunicorn with multi-threaded gthread workers to support streaming SSE connections efficiently
CMD ["gunicorn", "--workers", "2", "--threads", "8", "--worker-class", "gthread", "-b", "0.0.0.0:8000", "app.main:app"]
