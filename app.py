from flask import Flask, jsonify
from flask_cors import CORS
import os
import psycopg2

app = Flask(__name__, static_folder='client/build', static_url_path='/')

CORS(app)

def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database=os.environ['DATABASE'],
                            user=os.environ['DATABASE_USERNAME'],
                            password=os.environ['DATABASE_PASSWORD'])
    return conn

# Flask API endpoint
@app.route('/api/data')
def get_data():
    return {'data': 'Your data here'}

# Returning JSON data from a Flask endpoint
@app.route('/api/sendData')
def send_data():
    return jsonify({'message': 'Data sent successfully'})

# Flask error handling
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

# Serve React App
@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    sql_query = '''
    SELECT
      completion_time_in_sec,
      TO_CHAR((completion_time_in_sec / 60)::integer, 'FM999') || ':' || TO_CHAR(completion_time_in_sec % 60, 'FM00') AS formatted_time
    FROM
      puzzle_completion;
    '''
    cur.execute(sql_query)
    time = cur.fetchall()
    print(time[0][1]) # stored in an array of tuples, we want to access the second elemnt
    cur.close()
    conn.close()
    return app.send_static_file('index.html')

# Serve React build files in Flask
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return app.send_static_file( path)
    else:
        return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True)#, port=int(os.environ.get('PORT', 5000)))