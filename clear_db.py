import os
import sys
import logging
from datetime import datetime
import psycopg2
from dotenv import load_dotenv

import config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Validate required environment variables
REQUIRED_ENV_VARS = [
    "DATABASE_HOST",
    "DATABASE_NAME",
    "DATABASE_USERNAME",
    "DATABASE_PASSWORD",
]
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
    print("Please create a .env file with the following variables:")
    for var in REQUIRED_ENV_VARS:
        print(f"  {var}=<value>")
    sys.exit(1)

# Configuration
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")


# Archive table name
ARCHIVE_TABLE_NAME = f"{config.TABLE_NAME}_archive"


def create_archive_table(conn):
    """Create archive table if it doesn't exist."""
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {ARCHIVE_TABLE_NAME} (
        id SERIAL PRIMARY KEY,
        completion_time_in_sec INT,
        timestamp TIMESTAMP,
        archived_date DATE DEFAULT CURRENT_DATE
    );

    CREATE INDEX IF NOT EXISTS idx_archived_date
    ON {ARCHIVE_TABLE_NAME}(archived_date);
    """
    try:
        with conn.cursor() as cur:
            cur.execute(create_table_query)
            conn.commit()
        logger.info(f"Archive table '{ARCHIVE_TABLE_NAME}' ready")
    except psycopg2.Error as e:
        logger.error(f"Error creating archive table: {e}")
        raise


def archive_data(conn):
    """Archive current data before clearing."""
    archive_query = f"""
    INSERT INTO {ARCHIVE_TABLE_NAME}
        (completion_time_in_sec, timestamp, archived_date)
    SELECT completion_time_in_sec, timestamp, CURRENT_DATE
    FROM {config.TABLE_NAME};
    """
    try:
        with conn.cursor() as cur:
            cur.execute(archive_query)
            rows_archived = cur.rowcount
            conn.commit()
        logger.info(f"Archived {rows_archived} row(s) to '{ARCHIVE_TABLE_NAME}'")
        return rows_archived
    except psycopg2.Error as e:
        logger.error(f"Error archiving data: {e}")
        raise


# Clear database function
def clear_database():
    """Archive existing data and clear all records from the puzzle completion table."""
    logger.info(f"Starting database clear operation for table '{config.TABLE_NAME}'")

    try:
        conn = psycopg2.connect(
            host=DATABASE_HOST,
            database=DATABASE_NAME,
            user=DATABASE_USERNAME,
            password=DATABASE_PASSWORD,
        )
        logger.info("Database connection established")
    except psycopg2.Error as e:
        logger.error(f"Failed to connect to database: {e}")
        print(f"ERROR: Failed to connect to database: {e}")
        sys.exit(1)

    try:
        # Create archive table if it doesn't exist
        create_archive_table(conn)

        # Archive current data
        rows_archived = archive_data(conn)
        print(f"Archived {rows_archived} row(s) to '{ARCHIVE_TABLE_NAME}'")

        # Clear current data
        delete_query = f"DELETE FROM {config.TABLE_NAME};"
        with conn.cursor() as cur:
            cur.execute(delete_query)
            rows_deleted = cur.rowcount
            conn.commit()

        timestamp = datetime.now().isoformat()
        logger.info(
            f"Database table '{config.TABLE_NAME}' cleared successfully at {timestamp}. "
            f"Archived {rows_archived} row(s), deleted {rows_deleted} row(s)"
        )
        print(f"Database table '{config.TABLE_NAME}' cleared successfully.")
        print(
            f"Archived {rows_archived} row(s), deleted {rows_deleted} row(s) at {timestamp}"
        )
    except psycopg2.Error as e:
        logger.error(f"Error during database operation: {e}")
        print(f"ERROR: Error during database operation: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()
        logger.info("Database connection closed")


if __name__ == "__main__":
    clear_database()
