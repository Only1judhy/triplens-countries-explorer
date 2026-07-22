select distinct
    country_id,
    country_code_alpha_3,
    currency_code,
    currency_name,
    currency_symbol

from {{ ref('stg_country_currencies') }}

where country_id is not null
  and currency_code is not null