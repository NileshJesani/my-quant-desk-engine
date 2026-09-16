FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (if any) - none needed for now
# RUN apt-get update && apt-get install -y ... && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY src/ ./src/
COPY tests/ ./tests/

# Expose port
EXPOSE 8000

# Run the FastAPI app
CMD ["python", "-m", "src.api.app"]
