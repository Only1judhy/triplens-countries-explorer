with countries as (

    select
        *,
        coalesce(
            nullif(country_id, ''),
            nullif(country_code_alpha_3, ''),
            nullif(country_code_alpha_2, ''),
            country_name
        ) as country_natural_key

    from {{ ref('stg_countries') }}

)

select *

from countries

qualify row_number() over (
    partition by country_natural_key
    order by loaded_at desc
) = 1