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

## Question 3. Counting short trips

**For the trips in November 2025 (lpep_pickup_datetime between '2025-11-01' and '2025-12-01', exclusive of the upper bound), how many trips had a `trip_distance` of less than or equal to 1 mile?**

> **A:** `8,007`

```bash
# Commands executed
SELECT count(*) 
FROM tripdata_2025_11 
WHERE lpep_pickup_datetime>='2025-11-01' AND lpep_dropoff_datetime<'2025-12-01' AND trip_distance<=1;
```

## Question 4. Longest trip for each day

**Which was the pick up day with the longest trip distance? Only consider trips with trip_distance less than 100 miles (to exclude data errors).**

> **A**: `2025-11-14`

```bash
# Commands executed
SELECT date(lpep_pickup_datetime) as longest_trip_day
FROM tripdata_2025_11 
WHERE trip_distance<100 ORDER BY trip_distance DESC limit 1;
```