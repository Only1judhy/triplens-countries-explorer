import os

import snowflake.connector
from dotenv import load_dotenv


load_dotenv()


def test_connection() -> None:
    connection = None

    try:
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
        cursor.execute(
            """
            SELECT
                CURRENT_ACCOUNT(),
                CURRENT_USER(),
                CURRENT_DATABASE(),
                CURRENT_SCHEMA(),
                CURRENT_WAREHOUSE()
            """
        )

        result = cursor.fetchone()

        print("Snowflake connection successful.")
        print(f"Account: {result[0]}")
        print(f"User: {result[1]}")
        print(f"Database: {result[2]}")
        print(f"Schema: {result[3]}")
        print(f"Warehouse: {result[4]}")

        cursor.close()

    except Exception as error:
        print(f"Snowflake connection failed: {error}")
        raise

    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    test_connection()