# Module 4 Homework: Analytics Engineering with dbt

The code used to solve this homework is in this folder.

## Question 1. dbt Lineage and Execution

Given a dbt project with the following structure:

```
models/
├── staging/
│   ├── stg_green_tripdata.SQL
│   └── stg_yellow_tripdata.SQL
└── intermediate/
    └── int_trips_unioned.SQL (depends on stg_green_tripdata & stg_yellow_tripdata)
```

If you run `dbt run --select int_trips_unioned`, what models will be built?

- A: int_trips_unioned only

## Question 2. dbt Tests

You've configured a generic test like this in your `schema.yml`:

```yaml
columns:
  - name: payment_type
    data_tests:
      - accepted_values:
          arguments:
            values: [1, 2, 3, 4, 5]
            quote: false
```

Your model `fct_trips` has been running successfully for months. A new value `6` now appears in the source data.

What happens when you run `dbt test --select fct_trips`?

- A: dbt will fail the test, returning a non-zero exit code

## Question 3. Counting Records in `fct_monthly_zone_revenue`

After running your dbt project, query the `fct_monthly_zone_revenue` model.

What is the count of records in the `fct_monthly_zone_revenue` model?

- A: 12,184

```SQL
select count(*) from {{ ref('fct_monthly_zone_revenue')}}
```

## Question 4. Best Performing Zone for Green Taxis (2020)

Using the `fct_monthly_zone_revenue` table, find the pickup zone with the **highest total revenue** (`revenue_monthly_total_amount`) for **Green** taxi trips in 2020.

Which zone had the highest revenue?

- A: East Harlem North

```SQL
select 
    pickup_zone, 
    sum(revenue_monthly_total_amount) as total_revenue_green_20
from {{ ref('fct_monthly_zone_revenue') }}
where 
    service_type = 'Green' 
    and revenue_month between '2020-01-01' and '2020-12-31'
group by 1
order by total_revenue_green_20 desc
```

## Question 5. Green Taxi Trip Counts (October 2019)

Using the `fct_monthly_zone_revenue` table, what is the **total number of trips** (`total_monthly_trips`) for Green taxis in October 2019?

- A: 384,624

```SQL
select sum(total_monthly_trips)
from {{ ref ('fct_monthly_zone_revenue')}}
where service_type = 'Green' and
revenue_month = '2019-10-01'
```

## Question 6. Build a Staging Model for FHV Data

What is the count of records in `stg_fhv_tripdata`?

- A: 43,244,693

```SQL
SELECT count(*) from {{ ref('stg_fhv_tripdata')}}
```

```SQL
--Staging model: stg_fhv_tripdata
SELECT
    -- Identifiers
	dispatching_base_num,
	cast(PULocationID as int) as pickup_location_id,
	cast(DOLocationID as int) as dropoff_location_id,
	Affiliated_base_number as affiliated_base_number,
	-- Timestamps
	cast(pickup_datetime as timestamp) as pickup_datetime,
	cast(dropOff_datetime as timestamp) as dropoff_datetime,
	-- Flags
	SR_Flag as sr_flag
FROM 
{{ source('raw_data','fhv_tripdata')}}
where dispatching_base_num IS NOT NULL
```
