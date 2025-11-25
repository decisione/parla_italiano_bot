# Use Python 3.12-slim-bullseye as the base image
FROM python:3.12-slim-bullseye

# Set the working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (not needed for Telegram bot)
#EXPOSE 8080

# Set the entrypoint
ENTRYPOINT ["python", "parla_italiano_bot.py"]