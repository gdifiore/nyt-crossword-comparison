import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2

import math

import utils

app = Flask(__name__, static_folder="client/build", static_url_path="/")

CORS(app)


def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database=os.environ["DATABASE"],
        user=os.environ["DATABASE_USERNAME"],
        password=os.environ["DATABASE_PASSWORD"],
    )
    return conn

# Flask API endpoint
@app.route("/api/data", methods=["GET", "POST"])
def get_data():
    data = request.get_json()
    print(data)

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


# Returning JSON data from a Flask endpoint
@app.route("/api/sendData", methods=["GET", "POST"])
def send_data():
    return jsonify({"message": "Data sent successfully"})


# Print table contents for testing
@app.route("/printDB", methods=["GET"])
def print_db():
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
    time = cur.fetchall()
    formatted_times = [(index, x[0]) for index, x in enumerate(time)]
    cur.close()
    conn.close()
    return jsonify({"times": formatted_times})

@app.route('/api/chartData', methods=['GET'])
def get_chart_data():
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
    bins = [{"range": f"{math.floor(min_val + i*bin_width)}-{math.ceil(min_val + (i+1)*bin_width)}", "count": 0} for i in range(num_bins)]

    # iterate over the data and increment the count for the appropriate bin
    for value in data:
        for b in bins:
            low, high = map(float, b["range"].split('-'))
            if low <= value <= high:
                b["count"] += 1
                break

    # convert the range of each bin from seconds to "mm:ss"
    for b in bins:
        low, high = map(int, b["range"].split('-'))
        b["range"] = f"{low//60}:{low%60:02d}-{high//60}:{high%60:02d}"

    return jsonify({"data": bins})

# Flask error handling
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


# Serve React App
@app.route("/")
def index():
    return app.send_static_file("index.html")


# Serve React build files in Flask
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    if path != "" and os.path.exists(app.static_folder + "/" + path):
        return app.send_static_file(path)
    else:
        return app.send_static_file("index.html")


if __name__ == "__main__":
    app.run(debug=True)  # , port=int(os.environ.get('PORT', 5000)))
