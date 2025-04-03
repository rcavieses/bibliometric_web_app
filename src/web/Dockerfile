FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose the port that Streamlit runs on
EXPOSE 8501

# Set up environment variables
ENV PYTHONPATH=/app

# Run the Streamlit app
CMD ["streamlit", "run", "src/web/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]