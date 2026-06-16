FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Create directories that will be written to at runtime
RUN mkdir -p data vector_store

# Make startup script executable
RUN chmod +x start.sh

# Railway sets PORT dynamically — Streamlit will bind to it
EXPOSE 8501

CMD ["./start.sh"]
