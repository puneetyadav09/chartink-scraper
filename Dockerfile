# Use the official lightweight Python image
FROM python:3.11-slim

# Install Chromium and Chromium Driver (Required for Selenium)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    unzip \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Hugging Face Spaces runs as a non-root user for security
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Environment variables
# - PYTHONUNBUFFERED gives real time console output
# - PORT=7860 is the default port Hugging Face exposes
ENV PYTHONUNBUFFERED=1 \
    PORT=7860 \
    DISPLAY=:99 \
    CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Set working directory
WORKDIR $HOME/app

# Copy requirements and install
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy the rest of the application files
COPY --chown=user . .

# Start the server using gunicorn on port 7860
CMD ["gunicorn", "-b", "0.0.0.0:7860", "--workers", "1", "--threads", "4", "--timeout", "0", "app:app"]