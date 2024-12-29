import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
