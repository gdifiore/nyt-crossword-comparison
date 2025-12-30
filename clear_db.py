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


# Clear database function
def clear_database():
    """Clear all records from the puzzle completion table."""
    query = f"DELETE FROM {config.TABLE_NAME};"

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
        with conn.cursor() as cur:
            cur.execute(query)
            rows_deleted = cur.rowcount
            conn.commit()

        timestamp = datetime.now().isoformat()
        logger.info(
            f"Database table '{config.TABLE_NAME}' cleared successfully at {timestamp}. Deleted {rows_deleted} row(s)"
        )
        print(f"Database table '{config.TABLE_NAME}' cleared successfully.")
        print(f"Deleted {rows_deleted} row(s) at {timestamp}")
    except psycopg2.Error as e:
        logger.error(f"Error clearing database: {e}")
        print(f"ERROR: Error clearing database: {e}")
        sys.exit(1)
    finally:
        conn.close()
        logger.info("Database connection closed")


if __name__ == "__main__":
    clear_database()
