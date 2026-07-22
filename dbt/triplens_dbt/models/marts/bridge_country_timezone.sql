select distinct
    country.country_key,
    timezone.timezone_key,
    relationships.country_id,
    relationships.timezone

from {{ ref('int_country_timezones') }} as relationships

inner join {{ ref('dim_country') }} as country
    on relationships.country_id = country.country_id

inner join {{ ref('dim_timezone') }} as timezone
    on relationships.timezone = timezone.timezone