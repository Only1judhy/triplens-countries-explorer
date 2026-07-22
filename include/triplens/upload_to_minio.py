import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from minio import Minio


load_dotenv()

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "triplens-raw")

RAW_DATA_DIR = Path("include/data/raw")


def get_latest_json_file() -> Path:
    files = list(RAW_DATA_DIR.glob("countries_*.json"))

    if not files:
        raise FileNotFoundError("No extracted country JSON file was found.")

    return max(files, key=lambda file: file.stat().st_mtime)


def upload_latest_file() -> str:
    if not MINIO_ROOT_USER or not MINIO_ROOT_PASSWORD:
        raise ValueError("MinIO credentials are missing from the .env file.")

    client = Minio(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ROOT_USER,
        secret_key=MINIO_ROOT_PASSWORD,
        secure=False,
    )

    if not client.bucket_exists(MINIO_BUCKET):
        client.make_bucket(MINIO_BUCKET)
        print(f"Created bucket: {MINIO_BUCKET}")
    else:
        print(f"Bucket already exists: {MINIO_BUCKET}")

    source_file = get_latest_json_file()

    with source_file.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    extracted_at = payload["metadata"]["extracted_at_utc"]
    extraction_date = datetime.fromisoformat(extracted_at)

    object_name = (
        f"rest-countries/"
        f"year={extraction_date:%Y}/"
        f"month={extraction_date:%m}/"
        f"day={extraction_date:%d}/"
        f"{source_file.name}"
    )

    client.fput_object(
        bucket_name=MINIO_BUCKET,
        object_name=object_name,
        file_path=str(source_file),
        content_type="application/json",
        metadata={
            "run-id": payload["metadata"]["run_id"],
            "source": payload["metadata"]["source"],
            "record-count": str(payload["metadata"]["record_count"]),
        },
    )

    print("Upload completed successfully.")
    print(f"Local file: {source_file}")
    print(f"Bucket: {MINIO_BUCKET}")
    print(f"Object path: {object_name}")

    return object_name


if __name__ == "__main__":
    upload_latest_file()