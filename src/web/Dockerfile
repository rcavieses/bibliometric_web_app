FROM python:3.8-slim

WORKDIR /app

# Install system dependencies
RUN apt-update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies that might not be in requirements.txt
RUN pip install --no-cache-dir \
    firebase-admin \
    streamlit \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    wordcloud \
    requests \
    anthropic \
    openpyxl \
    scholarly \
    elsapy

# Copy source code
COPY . .

# Create directories for data
RUN mkdir -p secrets figures outputs data/raw data/processed logs

# Expose the port that Streamlit runs on
EXPOSE 8501

# Set up environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the Streamlit app
CMD ["streamlit", "run", "src/web/streamlit_app_cloud.py", "--server.port=8501", "--server.address=0.0.0.0"]