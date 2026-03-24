FROM python:3.11-slim

# Install Node.js
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Install and build frontend
COPY frontend/ frontend/
RUN cd frontend && npm install && npm run build

# Copy application code
COPY living_map/ living_map/
COPY living_map.db .

# Railway sets PORT dynamically
ENV PORT=8000
EXPOSE ${PORT}

CMD uvicorn living_map.app:app --host 0.0.0.0 --port ${PORT}
