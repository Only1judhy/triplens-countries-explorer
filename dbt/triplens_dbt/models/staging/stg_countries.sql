select
    country_json:uuid::string as country_id,
    nullif(country_json:codes:alpha_2::string, '') as country_code_alpha_2,
    nullif(country_json:codes:alpha_3::string, '') as country_code_alpha_3,

    country_json:names:common::string as country_name,
    country_json:names:official::string as official_name,

    country_json:region::string as region,
    country_json:subregion::string as subregion,
    country_json:continents[0]::string as continent,

    country_json:capitals[0]:name::string as capital_name,

    country_json:population::number as population,
    country_json:area:kilometers::float as area_square_km,

    country_json:coordinates:lat::float as latitude,
    country_json:coordinates:lng::float as longitude,

    country_json:landlocked::boolean as is_landlocked,
    country_json:classification:sovereign::boolean as is_sovereign,
    country_json:classification:un_member::boolean as is_un_member,

    country_json:government_type::string as government_type,
    country_json:cars:driving_side::string as driving_side,

    country_json:flag:emoji::string as flag_emoji,
    country_json:flag:url_png::string as flag_png_url,
    country_json:flag:url_svg::string as flag_svg_url,

    country_json:tlds[0]::string as primary_top_level_domain,
    country_json:calling_codes[0]::string as primary_calling_code,

    ingestion_id,
    loaded_at

from {{ ref('stg_country_records') }}