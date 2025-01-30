# Use the official Python image as a parent image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app/backend

# Copy the entire backend directory into the container
COPY . /app/backend

# install gcc
RUN apt-get update && apt-get install -y \
                    gcc \
                    build-essential \
                    libfuzzy-dev \
                    libssl-dev \
                    libffi-dev \
                    libmagic-dev \
                    libmagic1

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

# Expose port 8000 for FastAPI
EXPOSE 8000

# Command to run FastAPI with Uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]