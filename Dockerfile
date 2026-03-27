# Multi-stage build — much smaller final image
FROM python:3.10-slim AS builder
WORKDIR /build
COPY . .
RUN pip install --user --no-cache-dir .

# Final stage — no build tools in production
FROM python:3.10-slim
WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Security: run as non-root user
RUN groupadd -r medibot && useradd -r -g medibot medibot

COPY --from=builder /root/.local /home/medibot/.local
COPY --chown=medibot:medibot . .

# Update path to include local python packages
ENV PATH=/home/medibot/.local/bin:$PATH

USER medibot

# Health check built into image
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080

# uvicorn for production ASGI serving
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2", "--no-access-log"]