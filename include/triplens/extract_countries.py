import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("REST_COUNTRIES_API_KEY")
BASE_URL = os.getenv(
    "REST_COUNTRIES_BASE_URL",
    "https://api.restcountries.com/countries/v5",
)

OUTPUT_DIR = Path("include/data/raw")
PAGE_LIMIT = 100
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3


def fetch_page(offset: int) -> list[dict]:
    """Retrieve one page of countries from the REST Countries API."""

    if not API_KEY:
        raise ValueError("REST_COUNTRIES_API_KEY is missing from the environment.")

    headers = {"Authorization": f"Bearer {API_KEY}"}

    params = {
        "limit": PAGE_LIMIT,
        "offset": offset,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                BASE_URL,
                headers=headers,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()

            payload = response.json()
            return payload.get("data", {}).get("objects", [])

        except requests.RequestException as error:
            if attempt == MAX_RETRIES:
                raise RuntimeError(
                    f"API request failed after {MAX_RETRIES} attempts: {error}"
                ) from error

            print(f"Request failed. Retrying attempt {attempt + 1}...")
            time.sleep(2 * attempt)

    return []


def extract_all_countries() -> Path:
    """Extract all available countries and save them as timestamped JSON."""

    countries: list[dict] = []
    offset = 0

    while True:
        page = fetch_page(offset)

        if not page:
            break

        countries.extend(page)
        print(f"Retrieved {len(page)} records. Total: {len(countries)}")

        if len(page) < PAGE_LIMIT:
            break

        offset += PAGE_LIMIT

    if not countries:
        raise ValueError("The API returned no country records.")

    run_id = str(uuid.uuid4())
    extracted_at = datetime.now(timezone.utc)
    timestamp = extracted_at.strftime("%Y%m%d_%H%M%S")

    output = {
        "metadata": {
            "run_id": run_id,
            "source": "REST Countries API",
            "api_version": "v5",
            "extracted_at_utc": extracted_at.isoformat(),
            "record_count": len(countries),
        },
        "countries": countries,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / f"countries_{timestamp}.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False, indent=2)

    print(f"Extraction completed successfully.")
    print(f"Records extracted: {len(countries)}")
    print(f"File created: {output_file}")

    return output_file


if __name__ == "__main__":
    extract_all_countries()