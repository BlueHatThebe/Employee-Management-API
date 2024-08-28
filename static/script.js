document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');
    loadEmployees();

    // Form Element Setup
    const addEmployeeForm = document.getElementById('add-employee-form');
    const updateEmployeeForm = document.getElementById('update-employee-form');
    const addReviewForm = document.getElementById('add-review-form');
    const deactivateEmployeeForm = document.getElementById('deactivate-employee-form');

    // Form Submission Handlers
    if (addEmployeeForm) {
        addEmployeeForm.querySelector('form').addEventListener('submit', function(event) {
            event.preventDefault();
            addEmployee();
        });
    }

    if (updateEmployeeForm) {
        updateEmployeeForm.querySelector('form').addEventListener('submit', function(event) {
            event.preventDefault();
            updateEmployee();
        });
    }

    if (addReviewForm) {
        addReviewForm.querySelector('form').addEventListener('submit', function(event) {
            event.preventDefault();
            addPerformanceReview();
        });
    }

    if (deactivateEmployeeForm) {
        deactivateEmployeeForm.querySelector('form').addEventListener('submit', function(event) {
            event.preventDefault();
            deactivateEmployee();
        });
    }

    // Toggle Form Visibility
    document.getElementById('show-add-employee-form')?.addEventListener('click', function() {
        toggleVisibility('add');
    });

    document.getElementById('show-update-form')?.addEventListener('click', function() {
        toggleVisibility('update');
    });

    document.getElementById('show-review-form')?.addEventListener('click', function() {
        toggleVisibility('review');
    });

    document.getElementById('show-deactivate-form')?.addEventListener('click', function() {
        toggleVisibility('deactivate');
    });
});

function toggleVisibility(formType) {
    const forms = {
        add: document.getElementById('add-employee-form'),
        update: document.getElementById('update-employee-form'),
        review: document.getElementById('add-review-form'),
        deactivate: document.getElementById('deactivate-employee-form')
    };
    Object.keys(forms).forEach(type => {
        const form = forms[type];
        if (form) {
            form.classList.toggle('hidden', type !== formType);
        }
    });
}

async function loadEmployees() {
    try {
        const response = await fetch('/api/v1/employees');
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        const ul = document.getElementById('employee-list-ul');
        if (ul) {
            ul.innerHTML = '';
            data.data.forEach(employee => {
                const li = document.createElement('li');
                li.className = 'employee-item';
                li.textContent = `ID: ${employee.id}, Name: ${employee.name}, Position: ${employee.position}, Department: ${employee.department}, Contact: ${employee.contact}`;
                li.addEventListener('click', () => {
                    window.location.href = `/employeeDetails.html?id=${employee.id}`;
                });
                ul.appendChild(li);
            });
        }
    } catch (error) {
        console.error('Error loading employees:', error);
        const ul = document.getElementById('employee-list-ul');
        if (ul) {
            ul.innerHTML = `<li>Error loading employees: ${error.message}</li>`;
        }
    }
}

async function addEmployee() {
    const name = document.getElementById('name')?.value;
    const position = document.getElementById('position')?.value;
    const department = document.getElementById('department')?.value;
    const contact = document.getElementById('contact')?.value;

    try {
        const response = await fetch('/api/v1/employees', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, position, department, contact })
        });
        const result = await response.json();
        if (response.ok) {
            loadEmployees();
            clearForm('add');
        } else {
            alert(`Error: ${result.message}`);
        }
    } catch (error) {
        console.error('Error adding employee:', error);
    }
}

async function updateEmployee() {
    const id = document.getElementById('update-id')?.value;
    const name = document.getElementById('update-name')?.value;
    const position = document.getElementById('update-position')?.value;
    const department = document.getElementById('update-department')?.value;
    const contact = document.getElementById('update-contact')?.value;

    try {
        const response = await fetch(`/api/v1/employees/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, position, department, contact })
        });
        const result = await response.json();
        if (response.ok) {
            loadEmployees();
            clearForm('update');
        } else {
            alert(`Error: ${result.message}`);
        }
    } catch (error) {
        console.error('Error updating employee:', error);
    }
}

async function addPerformanceReview() {
    const id = document.getElementById('review-id')?.value;
    const reviewText = document.getElementById('review-text')?.value;

    try {
        const response = await fetch(`/api/v1/employees/${id}/reviews`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ review: reviewText })
        });
        const result = await response.json();
        if (response.ok) {
            loadEmployees();
            clearForm('review');
        } else {
            alert(`Error: ${result.message}`);
        }
    } catch (error) {
        console.error('Error adding performance review:', error);
    }
}

async function deactivateEmployee() {
    const id = document.getElementById('deactivate-id')?.value;

    try {
        const response = await fetch(`/api/v1/employees/${id}/deactivate`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const result = await response.json();
        if (response.ok) {
            loadEmployees();
            clearForm('deactivate');
        } else {
            alert(`Error: ${result.message}`);
        }
    } catch (error) {
        console.error('Error deactivating employee:', error);
    }
}

function clearForm(formType) {
    const forms = {
        add: document.getElementById('add-employee-form'),
        update: document.getElementById('update-employee-form'),
        review: document.getElementById('add-review-form'),
        deactivate: document.getElementById('deactivate-employee-form')
    };
    const form = forms[formType];
    if (form) {
        form.querySelectorAll('input, textarea').forEach(input => input.value = '');
    }
}
