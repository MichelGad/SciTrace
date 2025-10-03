# Frontend Development Guide

This guide covers the frontend architecture, components, and development practices for SciTrace's user interface.

## 🎨 Frontend Overview

SciTrace uses a modern, responsive frontend built with HTML5, CSS3, JavaScript, and Bootstrap 5. The frontend is designed for research workflows with an emphasis on usability and accessibility.

## 🏗️ Frontend Architecture

### Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Technology Stack              │
├─────────────────────────────────────────────────────────────┤
│  HTML5 Templates (Jinja2)                                  │
│  ├── Base Templates                                         │
│  ├── Page Templates                                         │
│  ├── Component Templates                                    │
│  └── Partial Templates                                      │
├─────────────────────────────────────────────────────────────┤
│  CSS3 Styling                                              │
│  ├── Bootstrap 5 Framework                                 │
│  ├── Custom CSS Utilities                                   │
│  ├── Component Styles                                       │
│  └── Responsive Design                                      │
├─────────────────────────────────────────────────────────────┤
│  JavaScript (ES6+)                                          │
│  ├── jQuery for DOM Manipulation                           │
│  ├── Custom JavaScript Modules                             │
│  ├── API Integration                                        │
│  └── Interactive Components                                 │
├─────────────────────────────────────────────────────────────┤
│  Third-party Libraries                                      │
│  ├── Vis.js for Data Visualization                          │
│  ├── Font Awesome for Icons                                │
│  ├── Chart.js for Charts                                   │
│  └── DataTables for Tables                                 │
└─────────────────────────────────────────────────────────────┘
```

## 📁 File Structure

### Template Organization

```
templates/
├── base.html                 # Base template with common layout
├── auth/                     # Authentication templates
│   ├── login.html
│   ├── register.html
│   └── profile.html
├── dashboard/                # Dashboard templates
│   └── index.html
├── projects/                 # Project management templates
│   ├── index.html
│   ├── create.html
│   ├── edit.html
│   ├── view.html
│   └── create_task.html
├── dataflow/                 # Dataflow templates
│   ├── index.html
│   ├── create.html
│   ├── edit.html
│   ├── view.html
│   ├── lifecycle.html
│   └── git_log.html
├── tasks/                    # Task management templates
│   ├── index.html
│   ├── create.html
│   ├── edit.html
│   └── view.html
└── partials/                 # Reusable components
    ├── _project_card.html
    ├── _stats_card.html
    ├── _status_badge.html
    ├── _priority_badge.html
    ├── _task_row.html
    ├── _demo_badge.html
    ├── _demo_info_alert.html
    ├── _empty_state.html
    ├── _empty_state_error.html
    ├── _error_boundary.html
    ├── _form_error.html
    └── _loading_error.html
```

### Static Assets Organization

```
static/
├── css/
│   └── utils/                # Custom CSS utilities
│       ├── colors.css        # Color palette
│       ├── components.css    # Component styles
│       ├── layout.css        # Layout utilities
│       ├── error-boundaries.css
│       ├── glass.css         # Glass morphism effects
│       └── scitrace-utils.css
└── js/
    └── utils/                # JavaScript modules
        ├── api.js            # API integration
        ├── error-handling.js # Error handling
        ├── forms.js          # Form utilities
        ├── scitrace-utils.js # General utilities
        ├── ui.js             # UI components
        └── visualization.js # Data visualization
```

## 🎯 Base Template System

### Base Template Structure

#### `templates/base.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}SciTrace{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    
    <!-- Custom CSS -->
    <link href="{{ url_for('static', filename='css/utils/colors.css') }}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/utils/components.css') }}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/utils/layout.css') }}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/utils/scitrace-utils.css') }}" rel="stylesheet">
    
    {% block extra_css %}{% endblock %}
</head>
<body class="{% block body_class %}{% endblock %}">
    <!-- Navigation -->
    {% include 'partials/_navigation.html' %}
    
    <!-- Main Content -->
    <main class="{% block main_class %}container-fluid{% endblock %}">
        <!-- Flash Messages -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="flash-messages">
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}
        
        <!-- Page Content -->
        {% block content %}{% endblock %}
    </main>
    
    <!-- Footer -->
    {% include 'partials/_footer.html' %}
    
    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    
    <!-- Custom JavaScript -->
    <script src="{{ url_for('static', filename='js/utils/api.js') }}"></script>
    <script src="{{ url_for('static', filename='js/utils/error-handling.js') }}"></script>
    <script src="{{ url_for('static', filename='js/utils/forms.js') }}"></script>
    <script src="{{ url_for('static', filename='js/utils/scitrace-utils.js') }}"></script>
    <script src="{{ url_for('static', filename='js/utils/ui.js') }}"></script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### Navigation Component

#### `templates/partials/_navigation.html`
```html
<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container-fluid">
        <a class="navbar-brand" href="{{ url_for('dashboard.index') }}">
            <i class="fas fa-project-diagram me-2"></i>
            SciTrace
        </a>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav me-auto">
                <li class="nav-item">
                    <a class="nav-link" href="{{ url_for('dashboard.index') }}">
                        <i class="fas fa-tachometer-alt me-1"></i>
                        Dashboard
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{{ url_for('projects.index') }}">
                        <i class="fas fa-folder me-1"></i>
                        Projects
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{{ url_for('dataflow.index') }}">
                        <i class="fas fa-sitemap me-1"></i>
                        Dataflows
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{{ url_for('tasks.index') }}">
                        <i class="fas fa-tasks me-1"></i>
                        Tasks
                    </a>
                </li>
            </ul>
            
            <ul class="navbar-nav">
                {% if current_user.is_authenticated %}
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-user me-1"></i>
                            {{ current_user.username }}
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{{ url_for('auth.profile') }}">
                                <i class="fas fa-user-circle me-2"></i>Profile
                            </a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="{{ url_for('auth.logout') }}">
                                <i class="fas fa-sign-out-alt me-2"></i>Logout
                            </a></li>
                        </ul>
                    </li>
                {% else %}
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('auth.login') }}">
                            <i class="fas fa-sign-in-alt me-1"></i>
                            Login
                        </a>
                    </li>
                {% endif %}
            </ul>
        </div>
    </div>
</nav>
```

## 🧩 Component System

### Reusable Components

#### Project Card Component

#### `templates/partials/_project_card.html`
```html
<div class="card project-card h-100">
    <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="card-title mb-0">
            <i class="fas fa-folder me-2"></i>
            {{ project.name }}
        </h5>
        <div class="dropdown">
            <button class="btn btn-sm btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                <i class="fas fa-ellipsis-v"></i>
            </button>
            <ul class="dropdown-menu">
                <li><a class="dropdown-item" href="{{ url_for('projects.view', id=project.id) }}">
                    <i class="fas fa-eye me-2"></i>View
                </a></li>
                <li><a class="dropdown-item" href="{{ url_for('projects.edit', id=project.id) }}">
                    <i class="fas fa-edit me-2"></i>Edit
                </a></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item text-danger" href="#" onclick="deleteProject({{ project.id }})">
                    <i class="fas fa-trash me-2"></i>Delete
                </a></li>
            </ul>
        </div>
    </div>
    
    <div class="card-body">
        <p class="card-text text-muted">{{ project.description or 'No description' }}</p>
        
        <div class="row g-2 mb-3">
            <div class="col-6">
                <small class="text-muted">Research Type</small>
                <div class="badge bg-{{ 'success' if project.research_type == 'environmental' else 'info' if project.research_type == 'biomedical' else 'warning' }}">
                    {{ project.research_type.title() }}
                </div>
            </div>
            <div class="col-6">
                <small class="text-muted">Created</small>
                <div class="small">{{ project.created_at.strftime('%Y-%m-%d') }}</div>
            </div>
        </div>
        
        <div class="row g-2">
            <div class="col-6">
                <div class="d-flex align-items-center">
                    <i class="fas fa-sitemap me-1 text-primary"></i>
                    <span class="small">{{ project.dataflow_count or 0 }} dataflows</span>
                </div>
            </div>
            <div class="col-6">
                <div class="d-flex align-items-center">
                    <i class="fas fa-tasks me-1 text-success"></i>
                    <span class="small">{{ project.task_count or 0 }} tasks</span>
                </div>
            </div>
        </div>
    </div>
    
    <div class="card-footer">
        <a href="{{ url_for('projects.view', id=project.id) }}" class="btn btn-primary btn-sm">
            <i class="fas fa-arrow-right me-1"></i>
            Open Project
        </a>
    </div>
</div>
```

#### Status Badge Component

#### `templates/partials/_status_badge.html`
```html
{% macro status_badge(status, size='sm') %}
    {% set badge_class = {
        'pending': 'bg-warning',
        'in_progress': 'bg-info',
        'completed': 'bg-success',
        'cancelled': 'bg-danger',
        'on_hold': 'bg-secondary'
    }.get(status, 'bg-secondary') %}
    
    <span class="badge {{ badge_class }} {{ 'badge-' + size if size != 'sm' else '' }}">
        {% if status == 'pending' %}
            <i class="fas fa-clock me-1"></i>Pending
        {% elif status == 'in_progress' %}
            <i class="fas fa-spinner fa-spin me-1"></i>In Progress
        {% elif status == 'completed' %}
            <i class="fas fa-check me-1"></i>Completed
        {% elif status == 'cancelled' %}
            <i class="fas fa-times me-1"></i>Cancelled
        {% elif status == 'on_hold' %}
            <i class="fas fa-pause me-1"></i>On Hold
        {% else %}
            <i class="fas fa-question me-1"></i>{{ status.title() }}
        {% endif %}
    </span>
{% endmacro %}
```

#### Priority Badge Component

#### `templates/partials/_priority_badge.html`
```html
{% macro priority_badge(priority, size='sm') %}
    {% set badge_class = {
        'low': 'bg-success',
        'medium': 'bg-warning',
        'high': 'bg-danger',
        'urgent': 'bg-dark'
    }.get(priority, 'bg-secondary') %}
    
    <span class="badge {{ badge_class }} {{ 'badge-' + size if size != 'sm' else '' }}">
        {% if priority == 'low' %}
            <i class="fas fa-arrow-down me-1"></i>Low
        {% elif priority == 'medium' %}
            <i class="fas fa-minus me-1"></i>Medium
        {% elif priority == 'high' %}
            <i class="fas fa-arrow-up me-1"></i>High
        {% elif priority == 'urgent' %}
            <i class="fas fa-exclamation-triangle me-1"></i>Urgent
        {% else %}
            <i class="fas fa-question me-1"></i>{{ priority.title() }}
        {% endif %}
    </span>
{% endmacro %}
```

## 🎨 CSS Architecture

### Custom CSS Utilities

#### `static/css/utils/colors.css`
```css
/* SciTrace Color Palette */
:root {
    /* Primary Colors */
    --scitrace-primary: #2c3e50;
    --scitrace-primary-light: #34495e;
    --scitrace-primary-dark: #1a252f;
    
    /* Secondary Colors */
    --scitrace-secondary: #3498db;
    --scitrace-secondary-light: #5dade2;
    --scitrace-secondary-dark: #2980b9;
    
    /* Accent Colors */
    --scitrace-accent: #e74c3c;
    --scitrace-accent-light: #ec7063;
    --scitrace-accent-dark: #c0392b;
    
    /* Success Colors */
    --scitrace-success: #27ae60;
    --scitrace-success-light: #58d68d;
    --scitrace-success-dark: #1e8449;
    
    /* Warning Colors */
    --scitrace-warning: #f39c12;
    --scitrace-warning-light: #f7dc6f;
    --scitrace-warning-dark: #d68910;
    
    /* Info Colors */
    --scitrace-info: #17a2b8;
    --scitrace-info-light: #5bc0de;
    --scitrace-info-dark: #138496;
    
    /* Neutral Colors */
    --scitrace-light: #f8f9fa;
    --scitrace-dark: #343a40;
    --scitrace-muted: #6c757d;
}

/* Color Utility Classes */
.bg-scitrace-primary { background-color: var(--scitrace-primary) !important; }
.text-scitrace-primary { color: var(--scitrace-primary) !important; }
.border-scitrace-primary { border-color: var(--scitrace-primary) !important; }

.bg-scitrace-secondary { background-color: var(--scitrace-secondary) !important; }
.text-scitrace-secondary { color: var(--scitrace-secondary) !important; }
.border-scitrace-secondary { border-color: var(--scitrace-secondary) !important; }

.bg-scitrace-accent { background-color: var(--scitrace-accent) !important; }
.text-scitrace-accent { color: var(--scitrace-accent) !important; }
.border-scitrace-accent { border-color: var(--scitrace-accent) !important; }
```

#### `static/css/utils/components.css`
```css
/* Custom Component Styles */

/* Project Cards */
.project-card {
    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    border: 1px solid #e9ecef;
}

.project-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Status Badges */
.status-badge {
    font-size: 0.75rem;
    font-weight: 500;
    padding: 0.25rem 0.5rem;
    border-radius: 0.375rem;
}

/* Priority Badges */
.priority-badge {
    font-size: 0.75rem;
    font-weight: 500;
    padding: 0.25rem 0.5rem;
    border-radius: 0.375rem;
}

/* Data Visualization Cards */
.viz-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
}

.viz-card .card-body {
    padding: 2rem;
}

/* Glass Morphism Effects */
.glass-effect {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 1rem;
}

/* Loading States */
.loading-spinner {
    display: inline-block;
    width: 1rem;
    height: 1rem;
    border: 2px solid #f3f3f3;
    border-top: 2px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Form Enhancements */
.form-floating > .form-control:focus ~ label,
.form-floating > .form-control:not(:placeholder-shown) ~ label {
    color: var(--scitrace-primary);
}

.form-control:focus {
    border-color: var(--scitrace-primary);
    box-shadow: 0 0 0 0.2rem rgba(44, 62, 80, 0.25);
}

/* Button Enhancements */
.btn-scitrace-primary {
    background-color: var(--scitrace-primary);
    border-color: var(--scitrace-primary);
    color: white;
}

.btn-scitrace-primary:hover {
    background-color: var(--scitrace-primary-dark);
    border-color: var(--scitrace-primary-dark);
    color: white;
}

/* Table Enhancements */
.table-scitrace {
    border-collapse: separate;
    border-spacing: 0;
}

.table-scitrace th {
    background-color: var(--scitrace-light);
    border-bottom: 2px solid var(--scitrace-primary);
    font-weight: 600;
    color: var(--scitrace-primary);
}

.table-scitrace tbody tr:hover {
    background-color: rgba(44, 62, 80, 0.05);
}
```

## 📱 Responsive Design

### Mobile-First Approach

#### `static/css/utils/layout.css`
```css
/* Responsive Layout Utilities */

/* Container Adjustments */
@media (max-width: 768px) {
    .container-fluid {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}

/* Navigation Responsiveness */
@media (max-width: 991.98px) {
    .navbar-nav {
        margin-top: 1rem;
    }
    
    .navbar-nav .nav-link {
        padding: 0.5rem 0;
    }
}

/* Card Grid Responsiveness */
@media (max-width: 576px) {
    .card-columns {
        column-count: 1;
    }
}

@media (min-width: 577px) and (max-width: 768px) {
    .card-columns {
        column-count: 2;
    }
}

@media (min-width: 769px) {
    .card-columns {
        column-count: 3;
    }
}

/* Form Responsiveness */
@media (max-width: 768px) {
    .form-floating {
        margin-bottom: 1rem;
    }
    
    .btn-group-vertical .btn {
        margin-bottom: 0.5rem;
    }
}

/* Table Responsiveness */
@media (max-width: 768px) {
    .table-responsive {
        font-size: 0.875rem;
    }
    
    .table th,
    .table td {
        padding: 0.5rem 0.25rem;
    }
}

/* Dashboard Responsiveness */
@media (max-width: 768px) {
    .dashboard-stats .col-md-3 {
        margin-bottom: 1rem;
    }
    
    .dashboard-charts {
        margin-top: 2rem;
    }
}
```

## 🚀 JavaScript Architecture

### Modular JavaScript System

#### `static/js/utils/api.js`
```javascript
/**
 * API Integration Module
 * Handles all API communication with the backend
 */
class ApiClient {
    constructor() {
        this.baseUrl = '/api';
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        };
    }
    
    /**
     * Make API request with error handling
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };
        
        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new ApiError(
                    errorData.error || 'API request failed',
                    response.status,
                    errorData
                );
            }
            
            return await response.json();
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError('Network error', 0, { originalError: error });
        }
    }
    
    /**
     * GET request
     */
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(url, { method: 'GET' });
    }
    
    /**
     * POST request
     */
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    /**
     * PUT request
     */
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    
    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

/**
 * API Error class
 */
class ApiError extends Error {
    constructor(message, status, details = {}) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.details = details;
    }
}

// Global API client instance
const api = new ApiClient();

// Export for use in other modules
window.ApiClient = ApiClient;
window.ApiError = ApiError;
window.api = api;
```

#### `static/js/utils/error-handling.js`
```javascript
/**
 * Error Handling Module
 * Provides centralized error handling and user feedback
 */
class ErrorHandler {
    constructor() {
        this.errorContainer = '.error-container';
        this.setupGlobalErrorHandlers();
    }
    
    /**
     * Setup global error handlers
     */
    setupGlobalErrorHandlers() {
        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.displayError('An unexpected error occurred. Please try again.');
        });
        
        // Handle global JavaScript errors
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            this.displayError('A JavaScript error occurred. Please refresh the page.');
        });
    }
    
    /**
     * Display error message to user
     */
    displayError(message, container = null) {
        const targetContainer = container || this.errorContainer;
        const errorDiv = document.querySelector(targetContainer);
        
        if (errorDiv) {
            errorDiv.innerHTML = `
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Error:</strong> ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            errorDiv.style.display = 'block';
        }
    }
    
    /**
     * Display success message to user
     */
    displaySuccess(message, container = null) {
        const targetContainer = container || this.errorContainer;
        const successDiv = document.querySelector(targetContainer);
        
        if (successDiv) {
            successDiv.innerHTML = `
                <div class="alert alert-success alert-dismissible fade show" role="alert">
                    <i class="fas fa-check-circle me-2"></i>
                    <strong>Success:</strong> ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            successDiv.style.display = 'block';
        }
    }
    
    /**
     * Clear all messages
     */
    clearMessages(container = null) {
        const targetContainer = container || this.errorContainer;
        const messageDiv = document.querySelector(targetContainer);
        
        if (messageDiv) {
            messageDiv.innerHTML = '';
            messageDiv.style.display = 'none';
        }
    }
    
    /**
     * Handle API errors
     */
    handleApiError(error) {
        if (error instanceof ApiError) {
            switch (error.status) {
                case 401:
                    this.displayError('Please log in to continue.');
                    setTimeout(() => window.location.href = '/auth/login', 2000);
                    break;
                case 403:
                    this.displayError('You do not have permission to perform this action.');
                    break;
                case 404:
                    this.displayError('The requested resource was not found.');
                    break;
                case 422:
                    this.displayError('Please check your input and try again.');
                    break;
                case 500:
                    this.displayError('A server error occurred. Please try again later.');
                    break;
                default:
                    this.displayError(error.message || 'An unexpected error occurred.');
            }
        } else {
            this.displayError('An unexpected error occurred. Please try again.');
        }
    }
}

// Global error handler instance
const errorHandler = new ErrorHandler();

// Export for use in other modules
window.ErrorHandler = ErrorHandler;
window.errorHandler = errorHandler;
```

#### `static/js/utils/forms.js`
```javascript
/**
 * Form Utilities Module
 * Provides form validation and submission utilities
 */
class FormHandler {
    constructor() {
        this.setupFormHandlers();
    }
    
    /**
     * Setup form event handlers
     */
    setupFormHandlers() {
        // Handle form submissions
        document.addEventListener('submit', (event) => {
            const form = event.target;
            if (form.dataset.ajax === 'true') {
                event.preventDefault();
                this.handleAjaxForm(form);
            }
        });
        
        // Handle form validation
        document.addEventListener('input', (event) => {
            if (event.target.form && event.target.form.dataset.validate === 'true') {
                this.validateField(event.target);
            }
        });
    }
    
    /**
     * Handle AJAX form submission
     */
    async handleAjaxForm(form) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        const action = form.action || form.dataset.action;
        const method = form.method || 'POST';
        
        try {
            // Show loading state
            this.setFormLoading(form, true);
            
            // Clear previous errors
            this.clearFormErrors(form);
            
            // Submit form
            let response;
            if (method.toUpperCase() === 'GET') {
                response = await api.get(action, data);
            } else {
                response = await api.post(action, data);
            }
            
            // Handle success
            if (response.success) {
                errorHandler.displaySuccess(response.message || 'Operation completed successfully');
                
                // Redirect if specified
                if (response.redirect) {
                    window.location.href = response.redirect;
                } else if (form.dataset.reload === 'true') {
                    window.location.reload();
                }
            } else {
                errorHandler.displayError(response.error || 'Form submission failed');
            }
        } catch (error) {
            errorHandler.handleApiError(error);
        } finally {
            this.setFormLoading(form, false);
        }
    }
    
    /**
     * Validate form field
     */
    validateField(field) {
        const value = field.value.trim();
        const fieldType = field.type;
        const required = field.hasAttribute('required');
        const minLength = field.getAttribute('minlength');
        const maxLength = field.getAttribute('maxlength');
        const pattern = field.getAttribute('pattern');
        
        let isValid = true;
        let errorMessage = '';
        
        // Required field validation
        if (required && !value) {
            isValid = false;
            errorMessage = 'This field is required';
        }
        
        // Length validation
        if (value && minLength && value.length < parseInt(minLength)) {
            isValid = false;
            errorMessage = `Minimum length is ${minLength} characters`;
        }
        
        if (value && maxLength && value.length > parseInt(maxLength)) {
            isValid = false;
            errorMessage = `Maximum length is ${maxLength} characters`;
        }
        
        // Pattern validation
        if (value && pattern && !new RegExp(pattern).test(value)) {
            isValid = false;
            errorMessage = 'Invalid format';
        }
        
        // Email validation
        if (fieldType === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Invalid email address';
            }
        }
        
        // Update field state
        this.updateFieldState(field, isValid, errorMessage);
        
        return isValid;
    }
    
    /**
     * Update field validation state
     */
    updateFieldState(field, isValid, errorMessage) {
        const feedback = field.parentNode.querySelector('.invalid-feedback');
        
        if (isValid) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            if (feedback) feedback.textContent = '';
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
            if (feedback) feedback.textContent = errorMessage;
        }
    }
    
    /**
     * Set form loading state
     */
    setFormLoading(form, loading) {
        const submitButton = form.querySelector('button[type="submit"]');
        const inputs = form.querySelectorAll('input, select, textarea');
        
        if (loading) {
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
            }
            inputs.forEach(input => input.disabled = true);
        } else {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.innerHTML = submitButton.dataset.originalText || 'Submit';
            }
            inputs.forEach(input => input.disabled = false);
        }
    }
    
    /**
     * Clear form errors
     */
    clearFormErrors(form) {
        const invalidFields = form.querySelectorAll('.is-invalid');
        invalidFields.forEach(field => {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        });
        
        const feedbacks = form.querySelectorAll('.invalid-feedback');
        feedbacks.forEach(feedback => feedback.textContent = '');
    }
}

// Initialize form handler
const formHandler = new FormHandler();

// Export for use in other modules
window.FormHandler = FormHandler;
window.formHandler = formHandler;
```

## 📊 Data Visualization

### Visualization Components

#### `static/js/utils/visualization.js`
```javascript
/**
 * Data Visualization Module
 * Handles charts, graphs, and data visualization components
 */
class DataVisualizer {
    constructor() {
        this.charts = new Map();
        this.setupVisualizationHandlers();
    }
    
    /**
     * Setup visualization event handlers
     */
    setupVisualizationHandlers() {
        // Handle window resize for responsive charts
        window.addEventListener('resize', () => {
            this.charts.forEach(chart => {
                if (chart.resize) chart.resize();
            });
        });
    }
    
    /**
     * Create project statistics chart
     */
    createProjectStatsChart(containerId, data) {
        const container = document.getElementById(containerId);
        if (!container) return null;
        
        const ctx = container.getContext('2d');
        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Environmental', 'Biomedical', 'Computational'],
                datasets: [{
                    data: [
                        data.environmental || 0,
                        data.biomedical || 0,
                        data.computational || 0
                    ],
                    backgroundColor: [
                        '#27ae60',
                        '#3498db',
                        '#f39c12'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
        
        this.charts.set(containerId, chart);
        return chart;
    }
    
    /**
     * Create task status chart
     */
    createTaskStatusChart(containerId, data) {
        const container = document.getElementById(containerId);
        if (!container) return null;
        
        const ctx = container.getContext('2d');
        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Pending', 'In Progress', 'Completed', 'Cancelled'],
                datasets: [{
                    label: 'Tasks',
                    data: [
                        data.pending || 0,
                        data.in_progress || 0,
                        data.completed || 0,
                        data.cancelled || 0
                    ],
                    backgroundColor: [
                        '#f39c12',
                        '#3498db',
                        '#27ae60',
                        '#e74c3c'
                    ],
                    borderWidth: 1,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
        
        this.charts.set(containerId, chart);
        return chart;
    }
    
    /**
     * Create dataflow network visualization
     */
    createDataflowNetwork(containerId, data) {
        const container = document.getElementById(containerId);
        if (!container) return null;
        
        // Create nodes and edges from data
        const nodes = data.nodes || [];
        const edges = data.edges || [];
        
        const network = new vis.Network(container, {
            nodes: nodes,
            edges: edges
        }, {
            nodes: {
                shape: 'dot',
                size: 20,
                font: {
                    size: 14,
                    color: '#333'
                },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                width: 2,
                color: {
                    color: '#848484',
                    highlight: '#848484'
                },
                smooth: {
                    type: 'continuous'
                }
            },
            physics: {
                enabled: true,
                stabilization: {
                    iterations: 100
                }
            },
            interaction: {
                hover: true,
                tooltipDelay: 200
            }
        });
        
        this.charts.set(containerId, network);
        return network;
    }
    
    /**
     * Update chart data
     */
    updateChart(containerId, newData) {
        const chart = this.charts.get(containerId);
        if (chart && chart.data) {
            chart.data = newData;
            chart.update();
        }
    }
    
    /**
     * Destroy chart
     */
    destroyChart(containerId) {
        const chart = this.charts.get(containerId);
        if (chart && chart.destroy) {
            chart.destroy();
        }
        this.charts.delete(containerId);
    }
}

// Global visualizer instance
const dataVisualizer = new DataVisualizer();

// Export for use in other modules
window.DataVisualizer = DataVisualizer;
window.dataVisualizer = dataVisualizer;
```

## 🎯 Best Practices

### Development Guidelines

#### Code Organization
1. **Modular JavaScript**: Keep JavaScript code organized in focused modules
2. **Template Inheritance**: Use Jinja2 template inheritance for consistent layouts
3. **Component Reusability**: Create reusable components for common UI patterns
4. **Responsive Design**: Ensure all components work on mobile and desktop
5. **Accessibility**: Follow WCAG guidelines for accessibility

#### Performance Optimization
1. **Lazy Loading**: Load JavaScript modules only when needed
2. **Image Optimization**: Use appropriate image formats and sizes
3. **CSS Minification**: Minify CSS files for production
4. **Caching**: Implement proper caching strategies for static assets
5. **Bundle Optimization**: Minimize JavaScript bundle sizes

#### Security Considerations
1. **Input Sanitization**: Sanitize all user inputs
2. **XSS Prevention**: Escape all dynamic content
3. **CSRF Protection**: Implement CSRF tokens for forms
4. **Content Security Policy**: Use CSP headers for additional security
5. **Secure Headers**: Implement security headers

## 📋 Frontend Checklist

### Development Checklist

- [ ] Responsive design implemented
- [ ] Cross-browser compatibility tested
- [ ] Accessibility guidelines followed
- [ ] JavaScript modules organized
- [ ] CSS architecture established
- [ ] Component system created
- [ ] Error handling implemented
- [ ] Form validation added
- [ ] API integration completed
- [ ] Performance optimized

### Production Checklist

- [ ] Assets minified and compressed
- [ ] CDN configured for static assets
- [ ] Caching headers set
- [ ] Security headers implemented
- [ ] Error monitoring configured
- [ ] Performance monitoring active
- [ ] User experience tested
- [ ] Mobile responsiveness verified
- [ ] Accessibility compliance confirmed
- [ ] Documentation updated

---

**Need help with frontend development?** Check out the [Developer Guide](README.md) for more technical details, or explore the [User Guide](../user-guide/README.md) for user interface documentation.
