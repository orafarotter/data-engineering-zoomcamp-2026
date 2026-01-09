# Module 1 Homework: Docker & SQL
## Question 1. Understanding docker first run

```bash
# Commands executed
docker run -it --entrypoint=bash python:3.12.8
pip --version
```

**What's the version of pip in the image?**

> **A:** `24.3.1`

## Question 2. Understanding Docker networking and docker-compose

**Given the following `docker-compose.yaml`, what is the `hostname` and `port` that pgadmin should use to connect to the postgres database?**

> **A:** `postgres:5432`
The services are on the same network and the container_name is specified.
