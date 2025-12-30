import os
import sys
import math
import logging
from datetime import datetime
from typing import List, Dict, Optional, Union
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import safe_join
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

from . import utils
from . import config

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
class Config:
    DATABASE_HOST = os.getenv("DATABASE_HOST")
    DATABASE_NAME = os.getenv("DATABASE_NAME")
    DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")


# Initialize Flask app
# Calculate path to client/build relative to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_FOLDER = os.path.join(BASE_DIR, "client", "build")
app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path="/")

# Configure CORS with specific origins
if Config.ALLOWED_ORIGINS == "*":
    CORS(app)
else:
    origins = [origin.strip() for origin in Config.ALLOWED_ORIGINS.split(",")]
    CORS(app, origins=origins)

app.config.from_object(Config)

# Initialize rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Database connection pool
try:
    db_pool = SimpleConnectionPool(
        minconn=config.DB_POOL_MIN_CONN,
        maxconn=config.DB_POOL_MAX_CONN,
        host=app.config["DATABASE_HOST"],
        database=app.config["DATABASE_NAME"],
        user=app.config["DATABASE_USERNAME"],
        password=app.config["DATABASE_PASSWORD"],
    )
    logger.info(
        f"Database connection pool created successfully (min={config.DB_POOL_MIN_CONN}, max={config.DB_POOL_MAX_CONN})"
    )

    # Test connection
    test_conn = db_pool.getconn()
    db_pool.putconn(test_conn)
    logger.info("Database connection test successful")
    logger.info(f"Application starting - Version {config.VERSION}")
except psycopg2.Error as e:
    logger.error(f"Failed to create database connection pool: {e}")
    print(f"ERROR: Failed to connect to database: {e}")
    print("Please check your database credentials and ensure PostgreSQL is running.")
    sys.exit(1)


# Database initialization
def initialize_database():
    """Initialize the database table if it doesn't exist."""
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {config.TABLE_NAME} (
        id SERIAL PRIMARY KEY,
        completion_time_in_sec INT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    try:
        conn = db_pool.getconn()
        with conn.cursor() as cur:
            cur.execute(create_table_query)
            conn.commit()
        logger.info(f"Table '{config.TABLE_NAME}' initialized successfully")
    except psycopg2.Error as e:
        logger.error(f"Error during database initialization: {e}")
        raise
    finally:
        db_pool.putconn(conn)


# Initialize database at startup
initialize_database()


# Database operations
def execute_query(query: str, params: tuple = None) -> Union[List[Dict], int]:
    """
    Execute a database query and return results or row count.

    Args:
        query: SQL query string
        params: Query parameters tuple

    Returns:
        For SELECT queries: List of dictionaries with results
        For INSERT/UPDATE/DELETE: Number of affected rows

    Raises:
        psycopg2.Error: If query execution fails
    """
    conn = db_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            if cur.description:
                # SELECT query - return results
                return cur.fetchall()
            else:
                # INSERT/UPDATE/DELETE - commit and return rowcount
                conn.commit()
                rowcount = cur.rowcount
                logger.info(f"Query executed successfully, {rowcount} row(s) affected")
                return rowcount
    except psycopg2.Error as e:
        logger.error(f"Database query failed: {e}")
        raise
    finally:
        db_pool.putconn(conn)


# API routes
@app.route("/api/data", methods=["POST"])
@limiter.limit("1 per day")  # Only 1 submission per IP per day
def insert_data():
    start_time = datetime.now()
    data = request.get_json()
    if not data or "secondsToComplete" not in data:
        logger.warning(f"Invalid request - missing data from {request.remote_addr}")
        return jsonify({"error": "Invalid data: missing secondsToComplete"}), 400

    # Validate completion time
    try:
        completion_time = int(data["secondsToComplete"])
    except (ValueError, TypeError):
        logger.warning(f"Invalid data type from {request.remote_addr}: {data}")
        return (
            jsonify({"error": "Invalid data: secondsToComplete must be an integer"}),
            400,
        )

    if completion_time < config.MIN_COMPLETION_TIME:
        logger.info(f"Time too fast from {request.remote_addr}: {completion_time}s")
        return (
            jsonify(
                {
                    "error": f"Invalid time: {completion_time} seconds is too fast. Minimum is {config.MIN_COMPLETION_TIME} seconds."
                }
            ),
            400,
        )

    if completion_time > config.MAX_COMPLETION_TIME:
        logger.info(f"Time too slow from {request.remote_addr}: {completion_time}s")
        return (
            jsonify(
                {
                    "error": f"Invalid time: {completion_time} seconds is too slow. Maximum is {config.MAX_COMPLETION_TIME} seconds (15 minutes)."
                }
            ),
            400,
        )

    # Insert data and check success
    try:
        query = f"INSERT INTO {config.TABLE_NAME} (completion_time_in_sec) VALUES (%s)"
        rows_affected = execute_query(query, (completion_time,))

        if rows_affected != 1:
            logger.warning(
                f"Expected 1 row to be inserted, but {rows_affected} were affected"
            )
            return jsonify({"error": "Failed to save data"}), 500

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Successfully inserted completion time: {completion_time}s from {request.remote_addr} (took {elapsed:.3f}s)"
        )
        return jsonify({"message": "Data received successfully"})
    except psycopg2.Error as e:
        logger.error(f"Database error while inserting data: {e}", exc_info=True)
        return jsonify({"error": "Failed to save data. Please try again."}), 500


@app.route("/api/chartData", methods=["GET"])
@limiter.limit("10 per minute")  # Limit chart data fetches
def get_chart_data():
    start_time = datetime.now()
    try:
        query = f"""
        SELECT completion_time_in_sec
        FROM {config.TABLE_NAME}
        """
        result = execute_query(query)
        data = [row["completion_time_in_sec"] for row in result]

        bins = calculate_bins(data)
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Chart data generated: {len(data)} data points, {len(bins)} bins (took {elapsed:.3f}s)"
        )
        return jsonify({"data": bins})
    except Exception as e:
        logger.error(f"Error generating chart data: {e}", exc_info=True)
        return jsonify({"error": "Failed to load chart data"}), 500


# Helper functions
def calculate_bins(data: List[int]) -> List[Dict]:
    """
    Calculate histogram bins for completion time data.

    Args:
        data: List of completion times in seconds

    Returns:
        List of bins with time ranges and counts

    Edge cases handled:
        - Empty data: returns empty list
        - Single value: returns one bin with all data
        - All same values: returns one bin with all data
    """
    if not data:
        return []

    min_val, max_val = min(data), max(data)

    # Handle case where all values are the same (would cause division by zero)
    if min_val == max_val:
        time_str = f"{min_val//60}:{min_val%60:02d}"
        return [{"range": f"{time_str}-{time_str}", "count": len(data)}]

    num_bins = utils.calculate_num_bins(data)
    bin_width = (max_val - min_val) / num_bins

    bins = [
        {
            "range": f"{math.floor(min_val + i*bin_width)}-{math.ceil(min_val + (i+1)*bin_width)}",
            "count": 0,
        }
        for i in range(num_bins)
    ]

    # Assign values to bins using exclusive upper bound to prevent double-counting
    for value in data:
        for i, b in enumerate(bins):
            low, high = map(float, b["range"].split("-"))
            # Use exclusive upper bound for all bins except the last one
            if i == len(bins) - 1:
                # Last bin includes upper boundary
                if low <= value <= high:
                    b["count"] += 1
                    break
            else:
                # Other bins exclude upper boundary
                if low <= value < high:
                    b["count"] += 1
                    break

    # Format time ranges as MM:SS
    for b in bins:
        low, high = map(int, b["range"].split("-"))
        b["range"] = f"{low//60}:{low%60:02d}-{high//60}:{high%60:02d}"

    # Filter out empty bins to avoid cluttering the chart
    bins = [b for b in bins if b["count"] > 0]

    return bins


# Analytics endpoint
@app.route("/api/stats")
def get_stats():
    """
    Get analytics and statistics from archived data.
    Returns daily metrics and historical trends.
    """
    try:
        # Get today's stats from current table
        today_query = f"""
        SELECT
            COUNT(*) as count,
            AVG(completion_time_in_sec) as avg_time,
            MIN(completion_time_in_sec) as min_time,
            MAX(completion_time_in_sec) as max_time
        FROM {config.TABLE_NAME}
        """
        today_result = execute_query(today_query)
        today_stats = dict(today_result[0]) if today_result else {}

        # Get historical stats from archive table
        archive_query = f"""
        SELECT
            archived_date,
            COUNT(*) as count,
            AVG(completion_time_in_sec) as avg_time,
            MIN(completion_time_in_sec) as min_time,
            MAX(completion_time_in_sec) as max_time
        FROM {config.TABLE_NAME}_archive
        GROUP BY archived_date
        ORDER BY archived_date DESC
        LIMIT 30
        """
        try:
            archive_results = execute_query(archive_query)
            historical_stats = [
                {
                    "date": str(row["archived_date"]),
                    "count": row["count"],
                    "avg_time": float(row["avg_time"]) if row["avg_time"] else 0,
                    "min_time": row["min_time"],
                    "max_time": row["max_time"],
                }
                for row in archive_results
            ]
        except psycopg2.Error:
            # Archive table might not exist yet
            historical_stats = []

        stats = {
            "today": {
                "count": today_stats.get("count", 0),
                "avg_time": (
                    float(today_stats["avg_time"]) if today_stats.get("avg_time") else 0
                ),
                "min_time": today_stats.get("min_time", 0),
                "max_time": today_stats.get("max_time", 0),
            },
            "historical": historical_stats,
        }

        logger.info(
            f"Stats generated: {stats['today']['count']} today, "
            f"{len(historical_stats)} historical days"
        )
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error generating stats: {e}", exc_info=True)
        return jsonify({"error": "Failed to load statistics"}), 500


# Health check endpoint
@app.route("/api/health")
def health_check():
    """
    Health check endpoint for monitoring.
    Returns service status and version information.
    """
    health_status = {
        "status": "healthy",
        "service": "nyt-crossword-comparison",
        "version": config.VERSION,
        "timestamp": datetime.now().isoformat(),
    }

    # Test database connection
    try:
        conn = db_pool.getconn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        db_pool.putconn(conn)
        health_status["database"] = "connected"

        # Get pool stats
        pool_stats = {
            "min_connections": config.DB_POOL_MIN_CONN,
            "max_connections": config.DB_POOL_MAX_CONN,
        }
        health_status["database_pool"] = pool_stats

    except Exception as e:
        logger.error(f"Health check database error: {e}")
        health_status["status"] = "unhealthy"
        health_status["database"] = "disconnected"
        health_status["error"] = str(e)
        return jsonify(health_status), 503

    return jsonify(health_status), 200


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_server_error(error):
    logger.error(f"Internal server error: {error}", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500


# Frontend routes
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    # Serve static files or fall back to index.html
    # Use safe_join to prevent path traversal attacks
    if path:
        safe_path = safe_join(app.static_folder, path)
        if safe_path and os.path.exists(safe_path):
            return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
