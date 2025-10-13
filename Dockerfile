# Multi-stage build for DJI Tello Diagnostics
# Optimized for size and security

# =============================================================================
# Stage 1: Builder
# =============================================================================
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies
COPY requirements.txt /tmp/
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r /tmp/requirements.txt

# =============================================================================
# Stage 2: Runtime
# =============================================================================
FROM python:3.11-slim

# Set labels
LABEL maintainer="Daniel L. Malpica <dlmalpica@me.com>"
LABEL description="DJI Tello Diagnostics Tool - Docker Container"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN groupadd -r tello && \
    useradd -r -g tello -d /app -s /sbin/nologin tello

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=tello:tello src/ /app/src/
COPY --chown=tello:tello README.md CHANGELOG.md LICENSE /app/

# Create data directory for logs
RUN mkdir -p /app/data && \
    chown -R tello:tello /app/data

# Switch to non-root user
USER tello

# Set Python path
ENV PYTHONPATH="/app/src:${PYTHONPATH}"

# Health check (optional - will always fail without Tello connection)
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD python -c "import sys; sys.exit(0)"

# Default command shows help
CMD ["python", "-m", "tello_diagnostics.diagnostics", "--help"]

