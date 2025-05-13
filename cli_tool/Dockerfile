FROM python:3.9-slim

# Install system dependencies for OpenCV and libgthread
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Default command
ENTRYPOINT ["python", "stitcher.py"]
