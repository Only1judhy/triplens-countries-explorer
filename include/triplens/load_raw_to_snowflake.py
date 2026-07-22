import json
import os
from datetime import datetime, timezone
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv
from minio import Minio


load_dotenv()


def get_latest_minio_file() -> tuple[str, dict]:
    client = Minio(
        endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
        access_key=os.getenv("MINIO_ROOT_USER"),
        secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
        secure=False,
    )

    bucket = os.getenv("MINIO_BUCKET", "triplens-raw")

    objects = list(
        client.list_objects(
            bucket,
            prefix="rest-countries/",
            recursive=True,
        )
    )

    json_objects = [
        item for item in objects if item.object_name.endswith(".json")
    ]

    if not json_objects:
        raise FileNotFoundError("No JSON files were found in MinIO.")

    latest_object = max(
        json_objects,
        key=lambda item: item.last_modified,
    )

    response = client.get_object(bucket, latest_object.object_name)

    try:
        payload = json.loads(response.read().decode("utf-8"))
    finally:
        response.close()
        response.release_conn()

    return latest_object.object_name, payload


def load_raw_data() -> None:
    object_path, payload = get_latest_minio_file()

    metadata = payload["metadata"]
    source_file_name = Path(object_path).name
    started_at = datetime.now(timezone.utc)

    connection = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE"),
    )

    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM RAW.COUNTRY_API_RAW
            WHERE MINIO_OBJECT_PATH = %s
            """,
            (object_path,),
        )

        already_loaded = cursor.fetchone()[0]

        if already_loaded:
            print("This MinIO file has already been loaded.")
            print(f"Object path: {object_path}")
            return

        cursor.execute(
            """
            INSERT INTO RAW.COUNTRY_API_RAW (
                INGESTION_ID,
                SOURCE_NAME,
                SOURCE_FILE_NAME,
                MINIO_OBJECT_PATH,
                EXTRACTED_AT,
                RECORD_COUNT,
                RAW_PAYLOAD
            )
            SELECT
                %s,
                %s,
                %s,
                %s,
                TO_TIMESTAMP_TZ(%s),
                %s,
                PARSE_JSON(%s)
            """,
            (
                metadata["run_id"],
                metadata["source"],
                source_file_name,
                object_path,
                metadata["extracted_at_utc"],
                metadata["record_count"],
                json.dumps(payload, ensure_ascii=False),
            ),
        )

        finished_at = datetime.now(timezone.utc)

        cursor.execute(
            """
            INSERT INTO AUDIT.PIPELINE_RUNS (
                RUN_ID,
                PIPELINE_NAME,
                STATUS,
                STARTED_AT,
                FINISHED_AT,
                SOURCE_FILE_NAME,
                MINIO_OBJECT_PATH,
                RECORDS_EXTRACTED,
                RECORDS_LOADED
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                metadata["run_id"],
                "triplens_countries_pipeline",
                "SUCCESS",
                started_at,
                finished_at,
                source_file_name,
                object_path,
                metadata["record_count"],
                metadata["record_count"],
            ),
        )

        print("Snowflake load completed successfully.")
        print(f"File: {source_file_name}")
        print(f"Object path: {object_path}")
        print(f"Records in payload: {metadata['record_count']}")

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    load_raw_data()