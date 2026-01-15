# Module 1 Homework: Docker & SQL

The code used to solve this homework is in this folder.

## Question 1. Understanding docker first run

What's the version of pip in the image?

- A: 24.3.1

```bash
# Commands executed
docker run -it --entrypoint=bash python:3.12.8
pip --version
```

## Question 2. Understanding Docker networking and docker-compose

Given the following `docker-compose.yaml`, what is the `hostname` and `port` that pgadmin should use to connect to the postgres database?

- A: postgres:5432

*The services are on the same network and the container_name is specified.*

## Question 3. Counting short trips

For the trips in November 2025 (lpep_pickup_datetime between '2025-11-01' and '2025-12-01', exclusive of the upper bound), how many trips had a `trip_distance` of less than or equal to 1 mile?

- A: 8,007

```SQL 
SELECT count(*) 
FROM tripdata_2025_11 
WHERE lpep_pickup_datetime>='2025-11-01' AND lpep_dropoff_datetime<'2025-12-01' AND trip_distance<=1;
```

## Question 4. Longest trip for each day

Which was the pick up day with the longest trip distance? Only consider trips with trip_distance less than 100 miles (to exclude data errors).

- A: 2025-11-14

```SQL
SELECT date(lpep_pickup_datetime) as longest_trip_day
FROM tripdata_2025_11 
WHERE trip_distance<100 ORDER BY trip_distance DESC limit 1;
```

## Question 5. Biggest pickup zone

Which was the pickup zone with the largest `total_amount` (sum of all trips) on November 18th, 2025?

- A: East Harlem North

```SQL
SELECT z."Zone",
ROUND(sum(t.total_amount)::numeric, 2) AS total_amount
FROM tripdata_2025_11 t 
LEFT JOIN taxi_zone_lookup z on z."LocationID"=t."PULocationID"
WHERE date(t.lpep_pickup_datetime)='2025-11-18'
GROUP BY z."Zone"
ORDER BY total_amount DESC
LIMIT 1;
```

## Question 6. Largest tip

For the passengers picked up in the zone named "East Harlem North" in November 2025, which was the drop off zone that had the largest tip?
Note: it's `tip` , not `trip`. We need the name of the zone, not the ID.

- A: Yorkville West

```SQL
SELECT 
	--t.lpep_pickup_datetime, 
	--t.lpep_dropoff_datetime, 
	--pu."Zone" as pickup_zone, 
	dr."Zone" as dropoff_zone,
	max(t.tip_amount) as max_tip_amount
FROM tripdata_2025_11 t 
LEFT JOIN taxi_zone_lookup pu on pu."LocationID"=t."PULocationID"
LEFT JOIN taxi_zone_lookup dr on dr."LocationID"=t."DOLocationID"
WHERE lpep_pickup_datetime>='2025-11-01' AND lpep_pickup_datetime<'2025-12-01' AND pu."Zone"='East Harlem North'
GROUP BY dr."Zone"
ORDER BY max_tip_amount DESC
LIMIT 1;
```

## Question 7. Terraform Workflow

Which of the following sequences, respectively, describes the workflow for:

1. Downloading the provider plugins and setting up backend,
2. Generating proposed changes and auto-executing the plan
3. Remove all resources managed by terraform`

- A: terraform init, terraform apply -auto-approve, terraform destroy