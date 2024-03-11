from flask import Flask, jsonify
import os
from flask_cors import CORS

app = Flask(__name__, static_folder='client/build', static_url_path='/')

CORS(app)

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