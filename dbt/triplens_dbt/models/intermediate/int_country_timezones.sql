select distinct
    country_id,
    country_code_alpha_3,
    timezone

from {{ ref('stg_country_timezones') }}

where country_id is not null
  and timezone is not null