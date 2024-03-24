import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2

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
