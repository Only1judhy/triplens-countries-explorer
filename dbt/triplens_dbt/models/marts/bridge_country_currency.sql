select distinct
    country.country_key,
    currency.currency_key,
    relationships.country_id,
    relationships.currency_code

from {{ ref('int_country_currencies') }} as relationships

inner join {{ ref('dim_country') }} as country
    on relationships.country_id = country.country_id

inner join {{ ref('dim_currency') }} as currency
    on relationships.currency_code = currency.currency_code