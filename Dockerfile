# Use an official Python runtime as a builder image.
FROM python:3.10-slim-bullseye AS builder

# Set the maintainer label.
LABEL repository="https://github.com/VioletCranberry/helmYAMLizer"
LABEL maintainer="VioletCranberry"

# Set up a working directory.
WORKDIR /app

# Install dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --target /app

# Use the distroless image
# See https://github.com/GoogleContainerTools/distroless
FROM gcr.io/distroless/python3-debian12

# Copy dependencies.
COPY --from=builder /app /app

# Ensure Python will find the dependencies.
ENV PYTHONPATH=/app

# Add script.
COPY helmYAMLizer.py .
ENTRYPOINT ["python3", "./helmYAMLizer.py"]
