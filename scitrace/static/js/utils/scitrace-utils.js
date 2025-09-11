/**
 * SciTrace Utilities - Main entry point
 * 
 * This file imports and initializes all utility modules for SciTrace.
 * Include this file in your HTML to get access to all utility functions.
 */

// Import all utility modules
// Note: In a real application, you would use ES6 modules or a bundler
// For now, we'll assume all utility files are loaded separately

// Load error handling utilities
if (typeof ErrorBoundary !== 'undefined') {
    window.SciTraceErrorBoundary = ErrorBoundary;
}
if (typeof GlobalErrorHandler !== 'undefined') {
    window.SciTraceGlobalErrorHandler = GlobalErrorHandler;
}
if (typeof APIErrorHandler !== 'undefined') {
    window.SciTraceAPIErrorHandler = APIErrorHandler;
}

/**
 * Initialize SciTrace utilities
 * Call this function after all utility files are loaded
 */
function initSciTraceUtils() {
    console.log('SciTrace utilities initialized');
    
    // Initialize common functionality
    initCommonFeatures();
    
    // Set up global error handling
    setupGlobalErrorHandling();
    
    // Initialize form enhancements
    initFormEnhancements();
    
    // Initialize UI enhancements
    initUIEnhancements();
}

/**
 * Initialize common features
 */
function initCommonFeatures() {
    // Auto-resize textareas
    if (typeof FormUtils !== 'undefined') {
        FormUtils.initAutoResizeTextareas();
    }
    
    // Initialize tooltips
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Initialize popovers
    if (typeof bootstrap !== 'undefined') {
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
}

/**
 * Set up global error handling
 */
function setupGlobalErrorHandling() {
    // Initialize global error handler if available
    if (typeof GlobalErrorHandler !== 'undefined') {
        window.globalErrorHandler = new GlobalErrorHandler({
            logErrors: true,
            showNotifications: true,
            errorEndpoint: '/api/errors' // Optional: endpoint to log errors to server
        });
    }
    
    // Fallback error handling for unhandled promise rejections
    window.addEventListener('unhandledrejection', function(event) {
        console.error('Unhandled promise rejection:', event.reason);
        
        if (typeof UiUtils !== 'undefined') {
            UiUtils.showAlert(
                'An unexpected error occurred. Please try again.',
                'error',
                5000
            );
        }
    });
    
    // Fallback error handling for global JavaScript errors
    window.addEventListener('error', function(event) {
        console.error('Global error:', event.error);
        
        if (typeof UiUtils !== 'undefined') {
            UiUtils.showAlert(
                'A JavaScript error occurred. Please refresh the page.',
                'error',
                5000
            );
        }
    });
}

/**
 * Initialize form enhancements
 */
function initFormEnhancements() {
    if (typeof FormUtils === 'undefined') return;
    
    // Add real-time validation to forms
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        const validator = FormUtils.createValidator({
            email: {
                required: true,
                email: true
            },
            password: {
                required: true,
                minLength: 8
            },
            name: {
                required: true,
                minLength: 2
            }
        });
        
        // Add real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                const formData = FormUtils.serializeForm(form);
                const validation = validator(formData);
                
                if (validation.errors[input.name]) {
                    FormUtils.showFieldError(input, validation.errors[input.name]);
                } else if (input.value.trim() !== '') {
                    FormUtils.showFieldSuccess(input, 'Looks good!');
                }
            });
        });
    });
}

/**
 * Initialize UI enhancements
 */
function initUIEnhancements() {
    // Add loading states to buttons with data-loading attribute
    const loadingButtons = document.querySelectorAll('[data-loading]');
    loadingButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (typeof UiUtils !== 'undefined') {
                const loadingText = this.dataset.loading || 'Loading...';
                UiUtils.showButtonLoading(this, loadingText);
            }
        });
    });
    
    // Add copy-to-clipboard functionality to elements with data-copy attribute
    const copyElements = document.querySelectorAll('[data-copy]');
    copyElements.forEach(element => {
        element.addEventListener('click', async function() {
            const textToCopy = this.dataset.copy || this.textContent;
            
            if (typeof UiUtils !== 'undefined') {
                const success = await UiUtils.copyToClipboard(textToCopy);
                if (success) {
                    UiUtils.showAlert('Copied to clipboard!', 'success', 2000);
                } else {
                    UiUtils.showAlert('Failed to copy to clipboard', 'error', 2000);
                }
            }
        });
    });
    
    // Add smooth scrolling to anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const target = this.getAttribute('href');
            if (target && target !== '#') {
                e.preventDefault();
                if (typeof UiUtils !== 'undefined') {
                    UiUtils.smoothScrollTo(target);
                }
            }
        });
    });
}

/**
 * Demo project utilities
 */
const DemoProjectUtils = {
    /**
     * Load demo projects with enhanced error handling
     */
    async loadDemoProjects() {
        if (typeof DemoUtils === 'undefined') {
            throw new Error('DemoUtils not loaded');
        }
        
        try {
            const result = await DemoUtils.loadDemoProjects();
            
            if (typeof UiUtils !== 'undefined') {
                UiUtils.showAlert(result.message, 'success');
            }
            
            // Redirect to projects page after a short delay
            setTimeout(() => {
                window.location.href = '/projects';
            }, 1500);
            
            return result;
        } catch (error) {
            console.error('Demo project loading failed:', error);
            
            if (typeof UiUtils !== 'undefined') {
                let errorMessage = 'Failed to load demo projects';
                
                if (error.status === 403) {
                    errorMessage = 'Access denied. You need admin privileges to load demo projects.';
                } else if (error.status === 500) {
                    errorMessage = 'Server error occurred during demo setup. Please check the server logs.';
                } else if (error.message.includes('Network error')) {
                    errorMessage = 'Network error: Could not connect to the server.';
                } else if (error.message.includes('timeout')) {
                    errorMessage = 'Request timed out. The demo setup is taking longer than expected.';
                } else {
                    errorMessage = error.message || errorMessage;
                }
                
                UiUtils.showAlert(errorMessage, 'error');
            }
            
            throw error;
        }
    }
};

/**
 * Dataflow utilities
 */
const DataflowProjectUtils = {
    /**
     * Regenerate dataflow with enhanced error handling
     */
    async regenerateDataflow(dataflowId) {
        if (typeof DataflowUtils === 'undefined') {
            throw new Error('DataflowUtils not loaded');
        }
        
        try {
            const result = await DataflowUtils.regenerateDataflow(dataflowId);
            
            if (typeof UiUtils !== 'undefined') {
                UiUtils.showAlert('Dataflow regenerated successfully!', 'success');
            }
            
            // Reload the page to show updated dataflow
            setTimeout(() => {
                window.location.reload();
            }, 1000);
            
            return result;
        } catch (error) {
            console.error('Dataflow regeneration failed:', error);
            
            if (typeof UiUtils !== 'undefined') {
                UiUtils.showAlert(
                    error.message || 'Failed to regenerate dataflow',
                    'error'
                );
            }
            
            throw error;
        }
    }
};

/**
 * Project management utilities
 */
const ProjectManagementUtils = {
    /**
     * Reset projects with confirmation
     */
    async resetProjects() {
        if (typeof ProjectUtils === 'undefined') {
            throw new Error('ProjectUtils not loaded');
        }
        
        if (typeof UiUtils !== 'undefined') {
            const confirmed = await UiUtils.showConfirmation(
                'This will permanently delete ALL your projects and their associated dataflows. This action cannot be undone. Are you sure you want to continue?',
                'Confirm Reset'
            );
            
            if (!confirmed) {
                return;
            }
        }
        
        try {
            const result = await ProjectUtils.resetProjects();
            
            if (typeof UiUtils !== 'undefined') {
                UiUtils.showAlert('Projects reset successfully!', 'success');
            }
            
            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1500);
            
            return result;
        } catch (error) {
            console.error('Project reset failed:', error);
            
            if (typeof UiUtils !== 'undefined') {
                UiUtils.showAlert(
                    error.message || 'Failed to reset projects',
                    'error'
                );
            }
            
            throw error;
        }
    }
};

// Export utilities to global scope
window.SciTraceUtils = {
    init: initSciTraceUtils,
    Demo: DemoProjectUtils,
    Dataflow: DataflowProjectUtils,
    Project: ProjectManagementUtils
};

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSciTraceUtils);
} else {
    initSciTraceUtils();
}
