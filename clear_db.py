import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Validate required environment variables
REQUIRED_ENV_VARS = ["DATABASE_HOST", "DATABASE_NAME", "DATABASE_USERNAME", "DATABASE_PASSWORD"]
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
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
    query = "DELETE FROM puzzle_completion;"  # Wipes all rows in the table
    conn = psycopg2.connect(
        host=DATABASE_HOST,
        database=DATABASE_NAME,
        user=DATABASE_USERNAME,
        password=DATABASE_PASSWORD,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            conn.commit()
        print("Database table 'puzzle_completion' cleared successfully.")
    except psycopg2.Error as e:
        print(f"Error clearing database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    clear_database()
