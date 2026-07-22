select
    md5(currency_code) as currency_key,
    currency_code,
    max(currency_name) as currency_name,
    max(currency_symbol) as currency_symbol

from {{ ref('int_country_currencies') }}

group by currency_code