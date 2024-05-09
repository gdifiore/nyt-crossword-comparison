import os
import math
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2

import utils

app = Flask(__name__, static_folder="client/build", static_url_path="/")

CORS(app)

def get_db_connection():
    """
    Establishes a connection to the database.

    Returns:
        psycopg2.extensions.connection: The database connection object.
    """
    conn = psycopg2.connect(
        host="localhost",
        database=os.environ["DATABASE"],
        user=os.environ["DATABASE_USERNAME"],
        password=os.environ["DATABASE_PASSWORD"],
    )
    return conn


# Flask API endpoint
@app.route("/api/data", methods=["GET", "POST"])
def insert_data():
    """
    Insert puzzle completion data into the database.

    This function receives puzzle completion data in JSON format and inserts it into the database.
    The completion time in seconds is extracted from the JSON data and stored in the 'puzzle_completion' table.

    Returns:
        A JSON response indicating the success of the data insertion.
    """
    data = request.get_json()

    conn = get_db_connection()
    cur = conn.cursor()
    sql_query = """
    INSERT INTO puzzle_completion (completion_time_in_sec)
        VALUES (%s)
    """
    cur.execute(sql_query, (data["secondsToComplete"],))
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"message": "Data received successfully"})

@app.route("/api/chartData", methods=["GET"])
def get_chart_data():
    """
    Retrieves puzzle completion data from the database, calculates the bin counts,
    and returns the data in JSON format.

    Returns:
        A JSON response containing the bin counts of puzzle completion times.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    sql_query = """
    SELECT
        completion_time_in_sec,
        TO_CHAR((completion_time_in_sec / 60)::integer, 'FM999') || ':' || TO_CHAR(completion_time_in_sec % 60, 'FM00') AS formatted_time
    FROM
        puzzle_completion;
                """
    cur.execute(sql_query)
    data = [x[0] for x in cur.fetchall()]
    conn.close()

    num_bins = utils.calculate_num_bins(data)
    min_val = min(data)
    max_val = max(data)
    bin_width = (max_val - min_val) / num_bins

    # initialize a list of dictionaries to hold the counts of values in each bin
    # this is copilot voodoo
    bins = [
        {
            "range": f"{math.floor(min_val + i*bin_width)}-{math.ceil(min_val + (i+1)*bin_width)}",
            "count": 0,
        }
        for i in range(num_bins)
    ]

    # iterate over the data and increment the count for the appropriate bin
    for value in data:
        for b in bins:
            low, high = map(float, b["range"].split("-"))
            if low <= value <= high:
                b["count"] += 1
                break

    # convert the range of each bin from seconds to "mm:ss"
    for b in bins:
        low, high = map(int, b["range"].split("-"))
        b["range"] = f"{low//60}:{low%60:02d}-{high//60}:{high%60:02d}"

    return jsonify({"data": bins})


# Flask error handling
@app.errorhandler(404)
def not_found(error):
    """
    Handles the 404 error.

    Returns:
    - A JSON response with an error message and a status code of 404.
    """
    return jsonify({"error": "Not found"}), 404


# Serve React App
@app.route("/")
def index():
    """
    This function handles the root route of the application.
    It returns the contents of the "index.html" file as the response.
    """
    return app.send_static_file("index.html")


# Serve React build files in Flask
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    """
    Serve static files or return index.html for all routes.

    Parameters:
    - path (str): The path of the requested file.

    Returns:
    - The requested static file if it exists, otherwise returns index.html.
    """
    if path != "" and os.path.exists(app.static_folder + "/" + path):
        return app.send_static_file(path)

    return app.send_static_file("index.html")


if __name__ == "__main__":
    app.run(debug=True)  # , port=int(os.environ.get('PORT', 5000)))
