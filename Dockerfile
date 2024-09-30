FROM python:3.11-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files to the container
COPY . .

# Compile Python source files into byte code and then delete the original source files
RUN python -m compileall -b . && find * | grep '\.py$' | xargs rm

# Set the value env variables
ARG VERSION
ENV VERSION ${VERSION:-0.0.0-dev}
ENV PYTHONUNBUFFERED=TRUE

EXPOSE 8000

# Start the FastAPI application
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
