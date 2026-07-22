select
    md5(timezone) as timezone_key,
    timezone

from {{ ref('int_country_timezones') }}

group by timezone