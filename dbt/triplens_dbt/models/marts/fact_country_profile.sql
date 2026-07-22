with currency_counts as (

    select
        country_key,
        count(*) as currency_count
    from {{ ref('bridge_country_currency') }}
    group by country_key

),

language_counts as (

    select
        country_key,
        count(*) as language_count
    from {{ ref('bridge_country_language') }}
    group by country_key

),

timezone_counts as (

    select
        country_key,
        count(*) as timezone_count
    from {{ ref('bridge_country_timezone') }}
    group by country_key

),

border_counts as (

    select
        country_key,
        count(*) as neighbouring_country_count
    from {{ ref('bridge_country_border') }}
    group by country_key

)

select
    country.country_key,
    country.population,
    country.area_square_km,

    case
        when country.area_square_km > 0
        then country.population / country.area_square_km
    end as population_density_per_sq_km,

    coalesce(currency_counts.currency_count, 0) as currency_count,
    coalesce(language_counts.language_count, 0) as language_count,
    coalesce(timezone_counts.timezone_count, 0) as timezone_count,
    coalesce(border_counts.neighbouring_country_count, 0)
        as neighbouring_country_count,

    country.is_landlocked,
    country.is_sovereign,
    country.is_un_member

from {{ ref('dim_country') }} as country

left join currency_counts
    on country.country_key = currency_counts.country_key

left join language_counts
    on country.country_key = language_counts.country_key

left join timezone_counts
    on country.country_key = timezone_counts.country_key

left join border_counts
    on country.country_key = border_counts.country_key