from flask import Flask, jsonify, request
from flask_cors import CORS
from connection_config import *
import pyodbc

app = Flask(__name__)
CORS(app)

conn_string = f"Driver={driver};Server=tcp:{server},1433;Database={database};Uid={username};Pwd={password};"

def get_db_connection():
    print(conn_string)
    try:
        conn = pyodbc.connect(conn_string)
        
        return conn
    except Exception as e:
        print("Database connection error:", e)
        return None

# Route to fetch data from Company_DIM
@app.route('/api/company', methods=['GET'])
def get_company_data():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Failed to connect to database"}), 500
        
        cursor = conn.cursor()
        query = "SELECT * FROM dbo.Company_DIM"
        cursor.execute(query)

        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify(results), 200
    except Exception as e:
        print("Error fetching data:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
