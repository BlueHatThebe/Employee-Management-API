from flask import Flask, send_from_directory, jsonify, request, render_template
from flask_cors import CORS
import sqlite3
import json
import os


app = Flask(__name__, static_folder='static')  # Ensure Flask knows where the static folder is
CORS(app)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('employees.db')
    conn.row_factory = sqlite3.Row
    return conn

# Input validation functions
def validate_employee(employee):
    required_fields = {'name', 'position', 'department', 'contact'}
    if not all(field in employee for field in required_fields):
        return False, "Missing required fields"
    if not isinstance(employee['name'], str) or not isinstance(employee['position'], str):
        return False, "Invalid data type for 'name' or 'position'"
    if not isinstance(employee['department'], str) or not isinstance(employee['contact'], str):
        return False, "Invalid data type for 'department' or 'contact'"
    return True, None

def validate_employee_id(employee_id):
    if not employee_id.isdigit():
        return False, "Employee ID must be an integer"
    return True, None

# Utility functions
def get_employee_by_id(employee_id):
    conn = get_db_connection()
    employee = conn.execute('SELECT * FROM employees WHERE id = ?', (employee_id,)).fetchone()
    conn.close()
    return employee

def handle_invalid_data_response(message):
    return jsonify({"status": "error", "message": message}), 400

@app.errorhandler(500)
def handle_internal_error(error):
    return jsonify({"status": "error", "message": "An internal error occurred"}), 500

@app.route("/", defaults={"filename": "index.html"})
@app.route("/<path:filename>")
def serve_static(filename):
    if filename.endswith('.html'):
        return render_template(filename)
    # Flask automatically serves static files from the 'static' folder
    return send_from_directory(app.static_folder, filename)

# API endpoints
@app.route("/api/v1/employees", methods=["GET"])
def get_employees():
    try:
        conn = get_db_connection()
        employees = conn.execute('SELECT * FROM employees').fetchall()
        conn.close()
        employees_list = [dict(employee) for employee in employees]
        for employee in employees_list:
            employee['performance_reviews'] = json.loads(employee['performance_reviews'])
        return jsonify({"status": "success", "data": employees_list}), 200
    except Exception as e:
        return handle_internal_error(e)

@app.route("/api/v1/employees/<int:employeeId>", methods=["GET"])
def get_employee(employeeId):
    is_valid, error = validate_employee_id(str(employeeId))
    if not is_valid:
        return handle_invalid_data_response(error)
    
    employee = get_employee_by_id(employeeId)
    if not employee:
        return jsonify({"status": "error", "message": "Employee not found"}), 404
    
    employee_data = dict(employee)
    employee_data['performance_reviews'] = json.loads(employee_data['performance_reviews'])
    return jsonify({"status": "success", "data": employee_data}), 200

@app.route("/api/v1/employees", methods=["POST"])
def add_employee():
    employee = request.json
    is_valid, error = validate_employee(employee)
    if not is_valid:
        return handle_invalid_data_response(error)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(id) FROM employees')
        max_id = cursor.fetchone()[0]
        employee_id = (int(max_id) if max_id else 0) + 1

        cursor.execute('''
            INSERT INTO employees (id, name, position, department, contact, active, performance_reviews)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (employee_id, employee['name'], employee['position'], employee['department'], employee['contact'], True, json.dumps([])))
        
        conn.commit()
        conn.close()
        
        employee['id'] = employee_id
        employee['performance_reviews'] = []
        return jsonify({"status": "success", "data": employee}), 201
    except Exception as e:
        return handle_internal_error(e)

@app.route("/api/v1/employees/<int:employeeId>", methods=["PUT"])
def update_employee(employeeId):
    is_valid, error = validate_employee_id(str(employeeId))
    if not is_valid:
        return handle_invalid_data_response(error)
    
    employee = get_employee_by_id(employeeId)
    if not employee:
        return jsonify({"status": "error", "message": "Employee not found"}), 404

    employee_data = request.json
    is_valid, error = validate_employee(employee_data)
    if not is_valid:
        return handle_invalid_data_response(error)
    
    try:
        conn = get_db_connection()
        conn.execute('''
            UPDATE employees
            SET name = ?, position = ?, department = ?, contact = ?
            WHERE id = ?
        ''', (employee_data['name'], employee_data['position'], employee_data['department'], employee_data['contact'], employeeId))
        conn.commit()
        conn.close()
        
        employee_data['id'] = employeeId
        employee_data['performance_reviews'] = json.loads(employee['performance_reviews'])
        return jsonify({"status": "success", "data": employee_data}), 200
    except Exception as e:
        return handle_internal_error(e)

@app.route("/api/v1/employees/<int:employeeId>", methods=["DELETE"])
def delete_employee(employeeId):
    is_valid, error = validate_employee_id(str(employeeId))
    if not is_valid:
        return handle_invalid_data_response(error)
    
    employee = get_employee_by_id(employeeId)
    if not employee:
        return jsonify({"status": "error", "message": "Employee not found"}), 404
    
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM employees WHERE id = ?', (employeeId,))
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success", "message": "Employee deleted"}), 204
    except Exception as e:
        return handle_internal_error(e)

@app.route("/api/v1/employees/<int:employeeId>/reviews", methods=["POST"])
def add_performance_review(employeeId):
    is_valid, error = validate_employee_id(str(employeeId))
    if not is_valid:
        return handle_invalid_data_response(error)
    
    employee = get_employee_by_id(employeeId)
    if not employee:
        return jsonify({"status": "error", "message": "Employee not found"}), 404
    
    review = request.json.get('review')
    if not review or not isinstance(review, str):
        return handle_invalid_data_response("Review is required and must be a string")
    
    try:
        reviews = json.loads(employee['performance_reviews'])
        reviews.append(review)
        
        conn = get_db_connection()
        conn.execute('''
            UPDATE employees
            SET performance_reviews = ?
            WHERE id = ?
        ''', (json.dumps(reviews), employeeId))
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success", "message": "Review added"}), 201
    except Exception as e:
        return handle_internal_error(e)

@app.route("/api/v1/employees/<int:employeeId>/deactivate", methods=["PATCH"])
def deactivate_employee(employeeId):
    is_valid, error = validate_employee_id(str(employeeId))
    if not is_valid:
        return handle_invalid_data_response(error)
    
    employee = get_employee_by_id(employeeId)
    if not employee:
        return jsonify({"status": "error", "message": "Employee not found"}), 404
    
    try:
        conn = get_db_connection()
        conn.execute('''
            UPDATE employees
            SET active = ?
            WHERE id = ?
        ''', (False, employeeId))
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success", "message": "Employee deactivated"}), 200
    except Exception as e:
        return handle_internal_error(e)

def init_db():
    conn = sqlite3.connect('employees.db')
    cursor = conn.cursor()
    
    # Create employees table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            department TEXT NOT NULL,
            contact TEXT,
            active BOOLEAN NOT NULL,
            performance_reviews TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Initialize the database
    init_db()
    # Run the Flask app
    app.run(debug=True)
