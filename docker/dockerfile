# syntax=docker/dockerfile:1.4
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# AetherCore Pico Container (Minimal footprint)
FROM python:3.11-alpine
WORKDIR /app
COPY --from=builder /install /usr/local
COPY src/ ./src/

# NIST SP 800-218 Security: Run as non-root
RUN adduser -D aether
USER aether

# Expose WebSocket port for Mesh Protocol
EXPOSE 8765
CMD ["python", "-m", "src.nodes.pico_worker"]
