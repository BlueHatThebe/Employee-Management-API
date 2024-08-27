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

def handle_invalid_data_response(message):
    return jsonify({"status": "error", "message": message}), 400

@app.errorhandler(500)
def handle_internal_error(error):
    return jsonify({"status": "error", "message": "An internal error occurred"}), 500

@app.route("/", defaults={"filename": ""})
@app.route("/templates/employeeDetails.html")
def home(filename):
    filename = filename or "index.html"
    return send_from_directory('templates', filename)

@app.route("/employee-details.html", methods=["GET"])
def employee_details():
    return send_from_directory("templates", "employeeDetails.html")

@app.route("/api/v1/employees", methods=["GET"])
def get_employees():
    try:
        conn = get_db_connection()
        employees = conn.execute('SELECT * FROM employees').fetchall()
        conn.close()
        return jsonify({"status": "success", "data": [dict(employee) for employee in employees]}), 200
    except Exception as e:
        return handle_internal_error(e)

@app.route("/api/v1/employees/<string:employee_id>", methods=["GET"])
def get_employee(employee_id):
    try:
        employee = get_employee_by_id(employee_id)
        if not employee:
            return jsonify({"status": "error", "message": "Employee not found"}), 404
        return jsonify({"status": "success", "data": dict(employee)}), 200
    except Exception as e:
        return handle_internal_error(e)

@app.route("/api/v1/employees", methods=["POST"])
def add_employee():
    try:
        employee = request.json
        if not validate_employee(employee):
            return handle_invalid_data_response("Invalid employee data")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(id) FROM employees')
        max_id = cursor.fetchone()[0]
        max_id = int(max_id) if max_id is not None else 0
        employee_id = max_id + 1

        cursor.execute('''
            INSERT INTO employees (id, name, position, department, contact, active, performance_reviews)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (employee_id, employee['name'], employee['position'], employee['department'], employee['contact'], True, json.dumps([])))
        
        conn.commit()
        conn.close()
        
        employee['id'] = employee_id
        return jsonify({"status": "success", "data": employee}), 201
    except Exception as e:
        return handle_internal_error(e)

@app.route("/api/v1/employees/<string:employee_id>", methods=["PUT"])
def update_employee(employee_id):
    try:
        employee = get_employee_by_id(employee_id)
        if not employee:
            return jsonify({"status": "error", "message": "Employee not found"}), 404
        
        employee_data = request.json
        if not validate_employee(employee_data):
            return handle_invalid_data_response("Invalid employee data")
        
        conn = get_db_connection()
        conn.execute('''
            UPDATE employees
            SET name = ?, position = ?, department = ?, contact = ?
            WHERE id = ?
        ''', (employee_data['name'], employee_data['position'], employee_data['department'], employee_data['contact'], employee_id))
        conn.commit()
        conn.close()
        
        employee_data['id'] = employee_id
        return jsonify({"status": "success", "data": employee_data}), 200
    except Exception as e:
        return handle_internal_error(e)

@app.route("/api/v1/employees/<string:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
    try:
        employee = get_employee_by_id(employee_id)
        if not employee:
            return jsonify({"status": "error", "message": "Employee not found"}), 404
        
        conn = get_db_connection()
        conn.execute('DELETE FROM employees WHERE id = ?', (employee_id,))
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success", "message": "Employee deleted"}), 204
    except Exception as e:
        return handle_internal_error(e)

@app.route("/api/v1/employees/<string:employee_id>/reviews", methods=["POST"])
def add_performance_review(employee_id):
    try:
        employee = get_employee_by_id(employee_id)
        if not employee:
            return jsonify({"status": "error", "message": "Employee not found"}), 404
        
        review = request.json.get('review')
        if not review:
            return handle_invalid_data_response("Review is required")
        
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
        
        return jsonify({"status": "success", "message": "Review added"}), 201
    except Exception as e:
        return handle_internal_error(e)

@app.route("/api/v1/employees/<string:employee_id>/deactivate", methods=["PATCH"])
def deactivate_employee(employee_id):
    try:
        employee = get_employee_by_id(employee_id)
        if not employee:
            return jsonify({"status": "error", "message": "Employee not found"}), 404
        
        conn = get_db_connection()
        conn.execute('''
            UPDATE employees
            SET active = ?
            WHERE id = ?
        ''', (False, employee_id))
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success", "message": "Employee deactivated"}), 200
    except Exception as e:
        return handle_internal_error(e)

if __name__ == "__main__":
    app.run(debug=True)
