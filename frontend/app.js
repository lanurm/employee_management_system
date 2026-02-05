/**
 * Employee Management System - Frontend Application
 * Handles all API interactions and UI updates
 */

// Dynamic API URL based on environment
const API_BASE_URL = (() => {
    const protocol = window.location.protocol;
    const hostname = window.location.hostname;
    const port = window.location.port;
    
    // In Docker: frontend runs on port 3000, API proxied through /api/
    if (port === '3000' || hostname === 'localhost' || hostname === '127.0.0.1') {
        // Use relative URL that will be proxied by Nginx
        return `${protocol}//${hostname}${port ? ':' + port : ''}/api`;
    }
    
    // Fallback to direct backend connection
    return `${protocol}//${hostname}:8000`;
})();

// State
let employees = [];
let editingId = null;
let deleteId = null;

// DOM Elements
const elements = {
    connectionStatus: document.getElementById('connectionStatus'),
    addEmployeeBtn: document.getElementById('addEmployeeBtn'),
    addFirstEmployee: document.getElementById('addFirstEmployee'),
    refreshBtn: document.getElementById('refreshBtn'),
    searchInput: document.getElementById('searchInput'),
    departmentFilter: document.getElementById('departmentFilter'),
    employeeTableBody: document.getElementById('employeeTableBody'),
    emptyState: document.getElementById('emptyState'),
    loadingState: document.getElementById('loadingState'),
    employeeModal: document.getElementById('employeeModal'),
    deleteModal: document.getElementById('deleteModal'),
    employeeForm: document.getElementById('employeeForm'),
    modalTitle: document.getElementById('modalTitle'),
    closeModal: document.getElementById('closeModal'),
    cancelBtn: document.getElementById('cancelBtn'),
    submitBtn: document.getElementById('submitBtn'),
    closeDeleteModal: document.getElementById('closeDeleteModal'),
    cancelDeleteBtn: document.getElementById('cancelDeleteBtn'),
    confirmDeleteBtn: document.getElementById('confirmDeleteBtn'),
    deleteEmployeeName: document.getElementById('deleteEmployeeName'),
    toastContainer: document.getElementById('toastContainer'),
    // Form fields
    employeeId: document.getElementById('employeeId'),
    employeeName: document.getElementById('employeeName'),
    employeeEmail: document.getElementById('employeeEmail'),
    employeeDepartment: document.getElementById('employeeDepartment'),
    employeeSalary: document.getElementById('employeeSalary'),
    // Stats
    totalEmployees: document.getElementById('totalEmployees'),
    departmentCount: document.getElementById('departmentCount'),
    avgSalary: document.getElementById('avgSalary'),
    totalPayroll: document.getElementById('totalPayroll'),
};

// Initialize app
document.addEventListener('DOMContentLoaded', init);

function init() {
    checkConnection();
    loadEmployees();
    setupEventListeners();
}

function setupEventListeners() {
    elements.addEmployeeBtn.addEventListener('click', () => openModal());
    elements.addFirstEmployee.addEventListener('click', () => openModal());
    elements.refreshBtn.addEventListener('click', loadEmployees);
    elements.closeModal.addEventListener('click', closeModal);
    elements.cancelBtn.addEventListener('click', closeModal);
    elements.closeDeleteModal.addEventListener('click', closeDeleteModal);
    elements.cancelDeleteBtn.addEventListener('click', closeDeleteModal);
    elements.confirmDeleteBtn.addEventListener('click', confirmDelete);
    elements.employeeForm.addEventListener('submit', handleSubmit);
    elements.searchInput.addEventListener('input', filterEmployees);
    elements.departmentFilter.addEventListener('change', filterEmployees);
    
    // Close modals on overlay click
    elements.employeeModal.addEventListener('click', (e) => {
        if (e.target === elements.employeeModal) closeModal();
    });
    elements.deleteModal.addEventListener('click', (e) => {
        if (e.target === elements.deleteModal) closeDeleteModal();
    });
}

// API Functions
async function checkConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            elements.connectionStatus.classList.add('connected');
            elements.connectionStatus.classList.remove('disconnected');
            elements.connectionStatus.querySelector('.status-text').textContent = 'Connected';
        } else {
            throw new Error('API not healthy');
        }
    } catch (error) {
        elements.connectionStatus.classList.add('disconnected');
        elements.connectionStatus.classList.remove('connected');
        elements.connectionStatus.querySelector('.status-text').textContent = 'Disconnected';
    }
}

async function loadEmployees() {
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE_URL}/employees`);
        if (!response.ok) throw new Error('Failed to load employees');
        employees = await response.json();
        updateStats();
        updateDepartmentFilter();
        renderEmployees();
        showToast('Employees loaded successfully', 'success');
    } catch (error) {
        console.error('Error loading employees:', error);
        showToast('Failed to load employees. Is the server running?', 'error');
        employees = [];
        renderEmployees();
    } finally {
        showLoading(false);
    }
}

async function createEmployee(data) {
    const response = await fetch(`${API_BASE_URL}/employees`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create employee');
    }
    return response.json();
}

async function updateEmployee(id, data) {
    const response = await fetch(`${API_BASE_URL}/employees/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update employee');
    }
    return response.json();
}

async function deleteEmployee(id) {
    const response = await fetch(`${API_BASE_URL}/employees/${id}`, {
        method: 'DELETE',
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete employee');
    }
    return response.json();
}

// UI Functions
function renderEmployees() {
    const filtered = getFilteredEmployees();
    
    if (filtered.length === 0) {
        elements.employeeTableBody.innerHTML = '';
        elements.emptyState.classList.add('visible');
        return;
    }
    
    elements.emptyState.classList.remove('visible');
    elements.employeeTableBody.innerHTML = filtered.map(emp => `
        <tr data-id="${emp.id}">
            <td><span style="color: var(--color-text-muted)">#${emp.id}</span></td>
            <td>
                <div class="employee-info">
                    <div class="employee-avatar">${getInitials(emp.name)}</div>
                    <span class="employee-name">${escapeHtml(emp.name)}</span>
                </div>
            </td>
            <td>${escapeHtml(emp.email)}</td>
            <td><span class="department-badge">${escapeHtml(emp.department)}</span></td>
            <td><span class="salary-amount">$${formatNumber(emp.salary)}</span></td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-icon edit" onclick="editEmployee(${emp.id})" title="Edit">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                        </svg>
                    </button>
                    <button class="btn btn-icon delete" onclick="promptDelete(${emp.id}, '${escapeHtml(emp.name)}')" title="Delete">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="3 6 5 6 21 6"/>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                        </svg>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function updateStats() {
    const total = employees.length;
    const departments = [...new Set(employees.map(e => e.department))];
    const totalSalary = employees.reduce((sum, e) => sum + e.salary, 0);
    const avgSalary = total > 0 ? totalSalary / total : 0;
    
    elements.totalEmployees.querySelector('.stat-value').textContent = total;
    elements.departmentCount.querySelector('.stat-value').textContent = departments.length;
    elements.avgSalary.querySelector('.stat-value').textContent = '$' + formatNumber(avgSalary);
    elements.totalPayroll.querySelector('.stat-value').textContent = '$' + formatNumber(totalSalary);
}

function updateDepartmentFilter() {
    const departments = [...new Set(employees.map(e => e.department))].sort();
    const currentValue = elements.departmentFilter.value;
    
    elements.departmentFilter.innerHTML = '<option value="">All Departments</option>' +
        departments.map(d => `<option value="${escapeHtml(d)}">${escapeHtml(d)}</option>`).join('');
    
    if (departments.includes(currentValue)) {
        elements.departmentFilter.value = currentValue;
    }
}

function getFilteredEmployees() {
    const search = elements.searchInput.value.toLowerCase();
    const department = elements.departmentFilter.value;
    
    return employees.filter(emp => {
        const matchesSearch = !search || 
            emp.name.toLowerCase().includes(search) || 
            emp.email.toLowerCase().includes(search);
        const matchesDept = !department || emp.department === department;
        return matchesSearch && matchesDept;
    });
}

function filterEmployees() {
    renderEmployees();
}

// Modal Functions
function openModal(employee = null) {
    editingId = employee?.id || null;
    elements.modalTitle.textContent = employee ? 'Edit Employee' : 'Add New Employee';
    elements.submitBtn.querySelector('.btn-text').textContent = employee ? 'Update Employee' : 'Save Employee';
    
    if (employee) {
        elements.employeeName.value = employee.name;
        elements.employeeEmail.value = employee.email;
        elements.employeeDepartment.value = employee.department;
        elements.employeeSalary.value = employee.salary;
    } else {
        elements.employeeForm.reset();
    }
    
    clearFormErrors();
    elements.employeeModal.classList.add('visible');
}

function closeModal() {
    elements.employeeModal.classList.remove('visible');
    editingId = null;
    elements.employeeForm.reset();
    clearFormErrors();
}

function promptDelete(id, name) {
    deleteId = id;
    elements.deleteEmployeeName.textContent = name;
    elements.deleteModal.classList.add('visible');
}

function closeDeleteModal() {
    elements.deleteModal.classList.remove('visible');
    deleteId = null;
}

// Form Handling
async function handleSubmit(e) {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    const data = {
        name: elements.employeeName.value.trim(),
        email: elements.employeeEmail.value.trim(),
        department: elements.employeeDepartment.value.trim(),
        salary: parseFloat(elements.employeeSalary.value),
    };
    
    elements.submitBtn.classList.add('loading');
    
    try {
        if (editingId) {
            await updateEmployee(editingId, data);
            showToast('Employee updated successfully', 'success');
        } else {
            await createEmployee(data);
            showToast('Employee created successfully', 'success');
        }
        closeModal();
        loadEmployees();
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        elements.submitBtn.classList.remove('loading');
    }
}

async function confirmDelete() {
    if (!deleteId) return;
    
    elements.confirmDeleteBtn.classList.add('loading');
    
    try {
        await deleteEmployee(deleteId);
        showToast('Employee deleted successfully', 'success');
        closeDeleteModal();
        loadEmployees();
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        elements.confirmDeleteBtn.classList.remove('loading');
    }
}

function validateForm() {
    let valid = true;
    clearFormErrors();
    
    if (!elements.employeeName.value.trim()) {
        showFieldError('name', 'Name is required');
        valid = false;
    }
    
    const email = elements.employeeEmail.value.trim();
    if (!email) {
        showFieldError('email', 'Email is required');
        valid = false;
    } else if (!isValidEmail(email)) {
        showFieldError('email', 'Please enter a valid email');
        valid = false;
    }
    
    if (!elements.employeeDepartment.value.trim()) {
        showFieldError('department', 'Department is required');
        valid = false;
    }
    
    const salary = parseFloat(elements.employeeSalary.value);
    if (isNaN(salary) || salary < 0) {
        showFieldError('salary', 'Please enter a valid salary');
        valid = false;
    }
    
    return valid;
}

function showFieldError(field, message) {
    const input = document.getElementById(`employee${capitalize(field)}`);
    const error = document.getElementById(`${field}Error`);
    if (input) input.classList.add('error');
    if (error) error.textContent = message;
}

function clearFormErrors() {
    document.querySelectorAll('.form-group input').forEach(input => {
        input.classList.remove('error');
    });
    document.querySelectorAll('.error-message').forEach(el => {
        el.textContent = '';
    });
}

// Global functions for onclick handlers
window.editEmployee = function(id) {
    const employee = employees.find(e => e.id === id);
    if (employee) openModal(employee);
};

window.promptDelete = promptDelete;

// Utility Functions
function showLoading(show) {
    if (show) {
        elements.loadingState.classList.add('visible');
        elements.emptyState.classList.remove('visible');
    } else {
        elements.loadingState.classList.remove('visible');
    }
}

function showToast(message, type = 'info') {
    const icons = {
        success: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
        error: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
        info: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
    };
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${icons[type]}</span>
        <span class="toast-message">${escapeHtml(message)}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
        </button>
    `;
    
    elements.toastContainer.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}

function getInitials(name) {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
}

function formatNumber(num) {
    return Number(num).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
