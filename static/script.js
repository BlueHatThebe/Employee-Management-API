document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');
    loadEmployees();

    document.getElementById('add-employee-form').addEventListener('submit', function(event) {
        event.preventDefault();
        addEmployee();
    });

    document.getElementById('update-employee-form').addEventListener('submit', function(event) {
        event.preventDefault();
        updateEmployee();
    });

    document.getElementById('add-review-form').addEventListener('submit', function(event) {
        event.preventDefault();
        addPerformanceReview();
    });

    document.getElementById('deactivate-employee-form').addEventListener('submit', function(event) {
        event.preventDefault();
        deactivateEmployee();
    });

    // Toggle the visibility of the update employee form
    document.getElementById('show-update-form').addEventListener('click', function() {
        document.getElementById('update-employee-div').style.display = 'block';
        document.getElementById('add-employee-div').style.display = 'none';
        document.getElementById('add-review-div').style.display = 'none';
        document.getElementById('deactivate-employee-div').style.display = 'none';
        document.getElementById('employees-list-div').style.display = 'none';
    });

    // Hide the update employee form
    document.getElementById('cancel-update').addEventListener('click', function() {
        document.getElementById('update-employee-div').style.display = 'none';
        document.getElementById('add-employee-div').style.display = 'block';
        document.getElementById('add-review-div').style.display = 'block';
        document.getElementById('deactivate-employee-div').style.display = 'block';
        document.getElementById('employees-list-div').style.display = 'block';
    });
});

function loadEmployees() {
    fetch('/api/v1/employees')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(employees => {
            const ul = document.getElementById('employee-list-ul');
            ul.innerHTML = ''; // Clear the list before adding new items
            if (employees.length === 0) {
                ul.innerHTML = '<li>No employees found.</li>';
            } else {
                employees.forEach(employee => {
                    const li = document.createElement('li');
                    li.textContent = `ID: ${employee.id}, Name: ${employee.name}, Position: ${employee.position}, Department: ${employee.department}, Contact: ${employee.contact}, Active: ${employee.active}`;
                    ul.appendChild(li);
                });
            }
        })
        .catch(error => {
            console.error('Error loading employees:', error);
            const ul = document.getElementById('employee-list-ul');
            ul.innerHTML = '<li>Error loading employees.</li>';
        });
}

function addEmployee() {
    const employee = {
        id: document.getElementById('id').value,
        name: document.getElementById('name').value,
        position: document.getElementById('position').value,
        department: document.getElementById('department').value,
        contact: document.getElementById('contact').value,
    };

    fetch('/api/v1/employees', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(employee)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.error || 'Unknown error occurred');
            });
        }
        return response.json();
    })
    .then(() => {
        loadEmployees();
        document.getElementById('add-employee-form').reset();
    })
    .catch(error => {
        console.error('Error adding employee:', error);
        alert(`Error adding employee: ${error.message}`);
    });
}

function updateEmployee() {
    const employeeId = document.getElementById('update-id').value;
    const updatedEmployee = {
        name: document.getElementById('update-name').value,
        position: document.getElementById('update-position').value,
        department: document.getElementById('update-department').value,
        contact: document.getElementById('update-contact').value
    };

    fetch(`/api/v1/employees/${employeeId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(updatedEmployee)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.error || 'Unknown error occurred');
            });
        }
        return response.json();
    })
    .then(() => {
        loadEmployees();
        document.getElementById('update-employee-form').reset();
        document.getElementById('update-employee-div').style.display = 'none';
        document.getElementById('add-employee-div').style.display = 'block';
    })
    .catch(error => {
        console.error('Error updating employee:', error);
        alert(`Error updating employee: ${error.message}`);
    });
}

function addPerformanceReview() {
    const employeeId = document.getElementById('review-id').value;
    const review = {
        review: document.getElementById('review-text').value
    };

    fetch(`/api/v1/employees/${employeeId}/reviews`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(review)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.error || 'Unknown error occurred');
            });
        }
        return response.json();
    })
    .then(() => {
        document.getElementById('add-review-form').reset();
    })
    .catch(error => {
        console.error('Error adding performance review:', error);
        alert(`Error adding performance review: ${error.message}`);
    });
}

function deactivateEmployee() {
    const employeeId = document.getElementById('deactivate-id').value;

    fetch(`/api/v1/employees/${employeeId}/deactivate`, {
        method: 'POST'
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.error || 'Unknown error occurred');
            });
        }
        return response.json();
    })
    .then(() => {
        loadEmployees();
        document.getElementById('deactivate-employee-form').reset();
    })
    .catch(error => {
        console.error('Error deactivating employee:', error);
        alert(`Error deactivating employee: ${error.message}`);
    });
}
