import os
from flask import Flask, jsonify, request
from datetime import datetime
import mysql.connector

app = Flask(__name__)

# Load DB config from environment variables
db_config = {
    'host': os.environ.get('DB_HOST'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'database': os.environ.get('DB_NAME')
}

@app.route('/log-ip', methods=['POST'])
def log_ip():
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()

    # Insert IP into MySQL
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO client_ips (ip_address) VALUES (%s)", (client_ip,))
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")

    return jsonify({
        "Client IP": client_ip
    })

# Optional: Healthcheck or default route
@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Use POST /log-ip to log your IP."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
