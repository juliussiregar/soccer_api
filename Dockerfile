FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies for dlib and other packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libjpeg-dev \
    libpng-dev \
    libboost-all-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install the project dependencies except dlib
COPY requirements.txt .
RUN pip install --upgrade pip && \
    # Install dependencies excluding dlib
    sed '/dlib/d' requirements.txt > temp_requirements.txt && \
    pip install --no-cache-dir -r temp_requirements.txt && \
    rm temp_requirements.txt

# Copy the project files to the container
COPY . .

ENV PIP_DEFAULT_TIMEOUT=100

RUN pip install --no-cache-dir dlib==19.24.6

# Compile Python source files into byte code and then delete the original source files
RUN python -m compileall -b . && find * | grep '\.py$' | xargs rm

# Set the environment variables
ARG VERSION
ENV VERSION=${VERSION:-0.0.0-dev}
ENV PYTHONUNBUFFERED=TRUE

EXPOSE 8000

# Start the FastAPI application
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
