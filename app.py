import os
import math
from typing import List, Dict
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

import utils

# Load environment variables
load_dotenv()

# Configuration
class Config:
    DATABASE_HOST = os.getenv("DATABASE_HOST")
    DATABASE_NAME = os.getenv("DATABASE_NAME")
    DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")

# Initialize Flask app
app = Flask(__name__, static_folder="client/build", static_url_path="/")
CORS(app)
app.config.from_object(Config)

# Database connection pool
db_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host=app.config["DATABASE_HOST"],
    database=app.config["DATABASE_NAME"],
    user=app.config["DATABASE_USERNAME"],
    password=app.config["DATABASE_PASSWORD"],
)

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
def insert_data():
    data = request.get_json()
    if not data or "secondsToComplete" not in data:
        return jsonify({"error": "Invalid data"}), 400

    query = "INSERT INTO puzzle_completion (completion_time_in_sec) VALUES (%s)"
    execute_query(query, (data["secondsToComplete"],))
    return jsonify({"message": "Data received successfully"})

@app.route("/api/chartData", methods=["GET"])
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
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
