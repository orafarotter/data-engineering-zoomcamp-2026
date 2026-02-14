select 
    pickup_zone, 
    sum(revenue_monthly_total_amount) as total_revenue_green_20
from {{ ref('fct_monthly_zone_revenue') }}
where 
    service_type = 'Green' 
    and revenue_month between '2020-01-01' and '2020-12-31'
group by 1
order by total_revenue_green_20 desc