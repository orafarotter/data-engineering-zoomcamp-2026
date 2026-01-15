# Use Python 3.11 slim image (lighter)
FROM python:3.11-slim

# Copy the 'uv' executable from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Set the working directory inside the container
WORKDIR /app

# Add the virtual environment to the system PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy dependency files first (optimizes Docker cache)
COPY "pyproject.toml" "uv.lock" ".python-version" ./

# Install dependencies locked in the lock file
RUN uv sync --locked

# Copy the ingestion script into the container | 1st is source, 2nd is destination
COPY ingest_data.py .

# Define the command to run when the container starts
ENTRYPOINT ["python", "ingest_data.py"]