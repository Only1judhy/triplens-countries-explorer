select distinct
    country_id,
    country_code_alpha_3,
    border_country_code_alpha_3

from {{ ref('stg_country_borders') }}

where country_id is not null
  and border_country_code_alpha_3 is not null