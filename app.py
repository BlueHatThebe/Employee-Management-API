from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import sqlite3
import json

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = sqlite3.connect('employees.db')
    conn.row_factory = sqlite3.Row
    return conn

def validate_employee(employee):
    required_fields = {'name', 'position', 'department', 'contact'}
    return all(field in employee for field in required_fields)

def get_employee_by_id(employee_id):
    conn = get_db_connection()
    employee = conn.execute('SELECT * FROM employees WHERE id = ?', (employee_id,)).fetchone()
    conn.close()
    return employee

@app.route("/", defaults={"filename": ""})
@app.route("/<path:filename>")
def home(filename):
    if filename == "":
        filename = "index.html"
    return send_from_directory('templates', filename)

@app.route("/api/v1/employees", methods=["GET"])
def get_employees():
    conn = get_db_connection()
    employees = conn.execute('SELECT * FROM employees').fetchall()
    conn.close()
    return jsonify([dict(employee) for employee in employees]), 200

@app.route("/api/v1/employees/<string:employee_id>", methods=["GET"])
def get_employee(employee_id):
    employee = get_employee_by_id(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    return jsonify(dict(employee)), 200

@app.route("/api/v1/employees", methods=["POST"])
def add_employee():
    employee = request.json
    if not validate_employee(employee):
        return jsonify({"error": "Invalid employee data"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Automatically generate a new unique ID for the employee
    cursor.execute('SELECT MAX(id) FROM employees')
    max_id = cursor.fetchone()[0]
    employee_id = (max_id + 1) if max_id else 1

    cursor.execute('''
        INSERT INTO employees (id, name, position, department, contact, active, performance_reviews)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (employee_id, employee['name'], employee['position'], employee['department'], employee['contact'], True, json.dumps([])))
    
    conn.commit()
    conn.close()
    
    employee['id'] = employee_id
    return jsonify(employee), 201

@app.route("/api/v1/employees/<string:employee_id>", methods=["PUT"])
def update_employee(employee_id):
    employee = get_employee_by_id(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    employee_data = request.json
    if not validate_employee(employee_data):
        return jsonify({"error": "Invalid employee data"}), 400
    conn = get_db_connection()
    conn.execute('''
        UPDATE employees
        SET name = ?, position = ?, department = ?, contact = ?
        WHERE id = ?
    ''', (employee_data['name'], employee_data['position'], employee_data['department'], employee_data['contact'], employee_id))
    conn.commit()
    conn.close()
    employee_data['id'] = employee_id
    return jsonify(employee_data), 200

@app.route("/api/v1/employees/<string:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
    employee = get_employee_by_id(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    conn = get_db_connection()
    conn.execute('DELETE FROM employees WHERE id = ?', (employee_id,))
    conn.commit()
    conn.close()
    return '', 204

@app.route("/api/v1/employees/<string:employee_id>/reviews", methods=["POST"])
def add_performance_review(employee_id):
    employee = get_employee_by_id(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    review = request.json.get('review')
    if not review:
        return jsonify({"error": "Review is required"}), 400
    reviews = json.loads(employee['performance_reviews'])
    reviews.append(review)
    conn = get_db_connection()
    conn.execute('''
        UPDATE employees
        SET performance_reviews = ?
        WHERE id = ?
    ''', (json.dumps(reviews), employee_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Review added"}), 201

@app.route("/api/v1/employees/<string:employee_id>/deactivate", methods=["PATCH"])
def deactivate_employee(employee_id):
    employee = get_employee_by_id(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    conn = get_db_connection()
    conn.execute('''
        UPDATE employees
        SET active = ?
        WHERE id = ?
    ''', (False, employee_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Employee deactivated"}), 200

if __name__ == "__main__":
    app.run(debug=True)
