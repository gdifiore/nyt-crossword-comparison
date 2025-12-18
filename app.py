import os
import sys
import math
from typing import List, Dict
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import safe_join
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

import utils

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
class Config:
    DATABASE_HOST = os.getenv("DATABASE_HOST")
    DATABASE_NAME = os.getenv("DATABASE_NAME")
    DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")

# Time validation constants (in seconds)
MIN_COMPLETION_TIME = 10  # 10 seconds minimum
MAX_COMPLETION_TIME = 900  # 15 minutes maximum

# Initialize Flask app
app = Flask(__name__, static_folder="client/build", static_url_path="/")

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
    storage_uri="memory://"
)

# Database connection pool
db_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host=app.config["DATABASE_HOST"],
    database=app.config["DATABASE_NAME"],
    user=app.config["DATABASE_USERNAME"],
    password=app.config["DATABASE_PASSWORD"],
)

# Database initialization
def initialize_database():
    table_name = "puzzle_completion"
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
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
        print(f"Table '{table_name}' initialized successfully.")
    except psycopg2.Error as e:
        print(f"Error during database initialization: {e}")
    finally:
        db_pool.putconn(conn)

# Initialize database at startup
initialize_database()

# Database operations
def execute_query(query: str, params: tuple = None) -> List[Dict]:
    conn = db_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            if cur.description:
                return cur.fetchall()
            conn.commit()
    finally:
        db_pool.putconn(conn)

# API routes
@app.route("/api/data", methods=["POST"])
@limiter.limit("1 per day")  # Only 1 submission per IP per day
def insert_data():
    data = request.get_json()
    if not data or "secondsToComplete" not in data:
        return jsonify({"error": "Invalid data: missing secondsToComplete"}), 400

    # Validate completion time
    try:
        completion_time = int(data["secondsToComplete"])
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid data: secondsToComplete must be an integer"}), 400

    if completion_time < MIN_COMPLETION_TIME:
        return jsonify({
            "error": f"Invalid time: {completion_time} seconds is too fast. Minimum is {MIN_COMPLETION_TIME} seconds."
        }), 400

    if completion_time > MAX_COMPLETION_TIME:
        return jsonify({
            "error": f"Invalid time: {completion_time} seconds is too slow. Maximum is {MAX_COMPLETION_TIME} seconds (15 minutes)."
        }), 400

    query = "INSERT INTO puzzle_completion (completion_time_in_sec) VALUES (%s)"
    execute_query(query, (completion_time,))
    return jsonify({"message": "Data received successfully"})

@app.route("/api/chartData", methods=["GET"])
@limiter.limit("10 per minute")  # Limit chart data fetches
def get_chart_data():
    query = """
    SELECT completion_time_in_sec
    FROM puzzle_completion
    """
    result = execute_query(query)
    data = [row["completion_time_in_sec"] for row in result]

    bins = calculate_bins(data)
    return jsonify({"data": bins})

# Helper functions
def calculate_bins(data: List[int]) -> List[Dict]:
    if not data:
        return []

    num_bins = utils.calculate_num_bins(data)
    min_val, max_val = min(data), max(data)
    bin_width = (max_val - min_val) / num_bins

    bins = [
        {
            "range": f"{math.floor(min_val + i*bin_width)}-{math.ceil(min_val + (i+1)*bin_width)}",
            "count": 0,
        }
        for i in range(num_bins)
    ]

    for value in data:
        for b in bins:
            low, high = map(float, b["range"].split("-"))
            if low <= value <= high:
                b["count"] += 1
                break

    for b in bins:
        low, high = map(int, b["range"].split("-"))
        b["range"] = f"{low//60}:{low%60:02d}-{high//60}:{high%60:02d}"

    return bins

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_server_error(error):
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
