import os
import psycopg2
from dotenv import load_dotenv

def get_db_connection():
    """Establish a database connection."""
    load_dotenv()
    return psycopg2.connect(
        host=os.getenv("DATABASE_HOST"),
        database=os.getenv("DATABASE"),
        user=os.getenv("DATABASE_USERNAME"),
        password=os.getenv("DATABASE_PASSWORD"),
    )

def setup_database(table_name="puzzle_completion"):
    """Set up the database table."""
    create_table_query = f"""
    CREATE TABLE {table_name} (
        id SERIAL PRIMARY KEY,
        completion_time_in_sec INT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"DROP TABLE IF EXISTS {table_name};")
                cur.execute(create_table_query)
                conn.commit()
        print(f"Table '{table_name}' created successfully.")
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    setup_database()

# Example of how to insert data (uncomment to use):
# def insert_sample_data(table_name="puzzle_completion"):
#     try:
#         with get_db_connection() as conn:
#             with conn.cursor() as cur:
#                 cur.execute(f"INSERT INTO {table_name} (completion_time_in_sec) VALUES (%s)", (103,))
#                 conn.commit()
#         print("Sample data inserted successfully.")
#     except psycopg2.Error as e:
#         print(f"An error occurred: {e}")
#
# insert_sample_data()

# SQL query to format time (for reference):
#SELECT
#  completion_time_in_sec,
#  TO_CHAR((completion_time_in_sec / 60)::integer, 'FM999') || ':' || TO_CHAR(completion_time_in_sec % 60, 'FM00') AS formatted_time
#FROM
#  puzzle_completion;

