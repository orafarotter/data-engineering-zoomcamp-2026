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