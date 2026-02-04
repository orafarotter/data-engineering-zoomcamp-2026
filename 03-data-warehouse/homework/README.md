# Module 3 Homework: Data Warehousing & BigQuery

The code used to solve this homework is in this folder.

## BigQuery Setup

Create a dataset in BigQuery 

```bash
bq mk --dataset --location=us-east1 zoomcamp_dataset_dw
```

Create an external table using the Yellow Taxi Trip Records.

```SQL 
CREATE OR REPLACE EXTERNAL TABLE `zoomcamp_dataset_dw.external_yellow_tripdata`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://zoomcamp-bucket-dw/yellow/yellow_tripdata_2024-*.parquet']
);
```

Create a (regular/materialized) table in BQ using the Yellow Taxi Trip Records (do not partition or cluster this table).

```SQL 
CREATE OR REPLACE TABLE zoomcamp_dataset_dw.regular_yellow_tripdata AS
SELECT * FROM zoomcamp_dataset_dw.external_yellow_tripdata;
```

## Question 1. Counting records

What is count of records for the 2024 Yellow Taxi Data?

- A: 20,332,093

```SQL 
SELECT count(*) FROM `zoomcamp_dataset_dw.regular_yellow_tripdata`;
```

## Question 2. Data read estimation

Write a query to count the distinct number of PULocationIDs for the entire dataset on both the tables.

```SQL 
SELECT COUNT(DISTINCT PULocationID) FROM `zoomcamp_dataset_dw.external_yellow_tripdata`
--This query will process 0 B when run.
```

```SQL 
SELECT COUNT(DISTINCT PULocationID) FROM `zoomcamp_dataset_dw.regular_yellow_tripdata`
--This query will process 155.12 MB when run.
```

What is the estimated amount of data that will be read when this query is executed on the External Table and the Table?

- A: 0 MB for the External Table and 155.12 MB for the Materialized Table


## Question 3. Understanding columnar storage

Write a query to retrieve the PULocationID from the table (not the external table) in BigQuery.

```SQL 
SELECT PULocationID FROM `zoomcamp_dataset_dw.regular_yellow_tripdata`;
--This query will process 155.12 MB when run.
```

Now write a query to retrieve the PULocationID and DOLocationID on the same table.

```SQL 
SELECT PULocationID, DOLocationID FROM `zoomcamp_dataset_dw.regular_yellow_tripdata`;
--This query will process 310.24 MB when run.
```

Why are the estimated number of Bytes different?

- A: BigQuery is a columnar database, and it only scans the specific columns requested in the query. Querying two columns (PULocationID, DOLocationID) requires reading more data than querying one column (PULocationID), leading to a higher estimated number of bytes processed.


## Question 4. Counting zero fare trips

How many records have a fare_amount of 0?

- A: 8,333

```SQL
SELECT count(*) FROM `zoomcamp_dataset_dw.regular_yellow_tripdata` where fare_amount=0;
```

## Question 5. Partitioning and clustering

What is the best strategy to make an optimized table in Big Query if your query will always filter based on tpep_dropoff_datetime and order the results by VendorID (Create a new table with this strategy)

- A: Partition by tpep_dropoff_datetime and Cluster on VendorID

```SQL
CREATE OR REPLACE TABLE zoomcamp_dataset_dw.partitioned_clustered_yellow_tripdata
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID AS
SELECT * FROM zoomcamp_dataset_dw.external_yellow_tripdata;
```

## Question 6. Partition benefits

Write a query to retrieve the distinct VendorIDs between tpep_dropoff_datetime 2024-03-01 and 2024-03-15 (inclusive). Use the materialized table you created earlier in your from clause and note the estimated bytes.

```SQL
SELECT DISTINCT VendorID 
FROM `zoomcamp_dataset_dw.regular_yellow_tripdata` 
WHERE tpep_dropoff_datetime >= '2024-03-01'
  AND tpep_dropoff_datetime <  '2024-03-16';
--This query will process 310.24 MB when run.
```

Now change the table in the from clause to the partitioned table you created for question 5 and note the estimated bytes processed. What are these values?

```SQL
SELECT DISTINCT VendorID 
FROM `zoomcamp_dataset_dw.partitioned_clustered_yellow_tripdata`
WHERE tpep_dropoff_datetime >= '2024-03-01'
  AND tpep_dropoff_datetime <  '2024-03-16'
--This query will process 26.84 MB when run.
```

Choose the answer which most closely matches.

- A: 310.24 MB for non-partitioned table and 26.84 MB for the partitioned table


## Question 7. External table storage

Where is the data stored in the External Table you created?

- A: GCP Bucket


## Question 8. Clustering best practices

It is best practice in Big Query to always cluster your data:

- A: False

Clustering is not always necessary. If your table is small or your queries don't use consistent filters, it will provide negligible benefits.


## Question 9. Understanding table scans

Write a SELECT count(*) query FROM the materialized table you created. 

How many bytes does it estimate will be read?

- A: This query will process 0 B when run.

Why?

- A: BigQuery caches query results to improve performance and reduce costs. When you run a query in BigQuery — as I did in [Question 1](#question-1-counting-records) — the results are cached for 24 hours by default. Running the same query again makes BigQuery retrieve the results from the cache instead of reprocessing the entire query.

*Reference: https://rafaelrampineli.medium.com/understanding-google-bigquery-tables-caching-partitioning-and-clustering-03444a9238a7*