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
        toggleVisibility('update');
    });

    // Hide the update employee form
    document.getElementById('cancel-update').addEventListener('click', function() {
        toggleVisibility('default');
    });
});

function toggleVisibility(state) {
    const elements = {
        update: ['update-employee-div', 'add-employee-div', 'add-review-div', 'deactivate-employee-div', 'employees-list-div'],
        default: ['add-employee-div', 'add-review-div', 'deactivate-employee-div', 'employees-list-div']
    };
    const display = {
        update: ['block', 'none', 'none', 'none', 'none'],
        default: ['block', 'block', 'block', 'block', 'block']
    };

    elements[state].forEach((id, index) => {
        document.getElementById(id).style.display = display[state][index];
    });
}

function loadEmployees() {
    fetch('/api/v1/employees')
        .then(response => response.json())
        .then(employees => {
            const ul = document.getElementById('employee-list-ul');
            ul.innerHTML = '';
            if (employees.data.length === 0) {
                ul.innerHTML = '<li>No employees found.</li>';
            } else {
                employees.data.forEach(employee => {
                    const li = document.createElement('li');
                    const link = document.createElement('a');
                    link.href = `/employeeDetails.html?id=${employee.id}`;
                    link.textContent = `ID: ${employee.id}, Name: ${employee.name}, Position: ${employee.position}, Department: ${employee.department}, Contact: ${employee.contact}, Active: ${employee.active}`;
                    li.appendChild(link);
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
        name: document.getElementById('name').value,
        position: document.getElementById('position').value,
        department: document.getElementById('department').value,
        contact: document.getElementById('contact').value
    };

    fetch('/api/v1/employees', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(employee)
    })
    .then(response => response.json())
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
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedEmployee)
    })
    .then(response => response.json())
    .then(() => {
        loadEmployees();
        document.getElementById('update-employee-form').reset();
        toggleVisibility('default');
    })
    .catch(error => {
        console.error('Error updating employee:', error);
        alert(`Error updating employee: ${error.message}`);
    });
}

function addPerformanceReview() {
    const employeeId = document.getElementById('review-id').value;
    const review = { review: document.getElementById('review-text').value };

    fetch(`/api/v1/employees/${employeeId}/reviews`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(review)
    })
    .then(response => response.json())
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

    fetch(`/api/v1/employees/${employeeId}/deactivate`, { method: 'PATCH' })
    .then(response => response.json())
    .then(() => {
        loadEmployees();
        document.getElementById('deactivate-employee-form').reset();
    })
    .catch(error => {
        console.error('Error deactivating employee:', error);
        alert(`Error deactivating employee: ${error.message}`);
    });
}

