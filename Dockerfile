# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-tk \
    tk-dev \
    python3-pip \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# Install additional Python packages for mapping
RUN pip install folium

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
COPY visualization_requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r visualization_requirements.txt

# Create necessary directories
RUN mkdir -p /app/TrafficData/SingleModelScats/model \
    && mkdir -p /app/TrafficData/SingleModelScats/data

# Copy the rest of the application
COPY . .

# Create empty files for compatibility
RUN touch /app/TrafficData/SingleModelScats/data/train-data.csv \
    && touch /app/TrafficData/SingleModelScats/data/test-data.csv

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Run app.py when the container launches
CMD ["python", "app.py"]
