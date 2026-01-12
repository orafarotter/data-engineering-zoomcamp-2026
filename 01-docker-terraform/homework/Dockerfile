# base Docker image that we will build on
FROM python:3.11-slim

# Copy uv binary from official uv image (multi-stage build pattern)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# set up the working directory inside the container
WORKDIR /app

# set up our image by installing prerequisites; pandas in this case
RUN pip install pandas pyarrow


# copy the script to the container. 1st name is source file, 2nd is destination
COPY ingest_data.py .

# define what to do first when the container runs
# in this example, we will just run the script
ENTRYPOINT ["python", "ingest_data.py"]