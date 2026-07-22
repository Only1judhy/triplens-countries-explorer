with record_counts as (

    select
        (select count(*) from {{ ref('dim_country') }}) as dimension_count,
        (select count(*) from {{ ref('fact_country_profile') }}) as fact_count

)

select *

from record_counts

where dimension_count <> fact_count