select *

from {{ ref('fact_country_profile') }}

where population < 0
   or area_square_km < 0
   or population_density_per_sq_km < 0