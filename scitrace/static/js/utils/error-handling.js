/**
 * SciTrace Error Handling Utilities
 * 
 * Provides error boundary functionality and graceful error handling
 * for frontend components and API interactions.
 */

class SciTraceError extends Error {
    constructor(message, code = 'UNKNOWN_ERROR', details = null) {
        super(message);
        this.name = 'SciTraceError';
        this.code = code;
        this.details = details;
        this.timestamp = new Date().toISOString();
    }
}

class ErrorBoundary {
    constructor(container, options = {}) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        this.options = {
            showStackTrace: false,
            allowRetry: true,
            logErrors: true,
            fallbackMessage: 'Something went wrong. Please try again.',
            ...options
        };
        this.error = null;
        this.retryCount = 0;
        this.maxRetries = this.options.maxRetries || 3;
    }

    /**
     * Handle an error by displaying a user-friendly message
     * @param {Error} error - The error to handle
     * @param {Object} errorInfo - Additional error information
     */
    handleError(error, errorInfo = {}) {
        this.error = error;
        
        if (this.options.logErrors) {
            this.logError(error, errorInfo);
        }

        this.renderErrorUI();
    }

    /**
     * Log error details to console and potentially to server
     * @param {Error} error - The error to log
     * @param {Object} errorInfo - Additional error information
     */
    logError(error, errorInfo) {
        const errorDetails = {
            message: error.message,
            stack: error.stack,
            code: error.code || 'UNKNOWN_ERROR',
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            url: window.location.href,
            ...errorInfo
        };

        console.error('SciTrace Error:', errorDetails);

        // Send error to server if endpoint is available
        if (this.options.errorEndpoint) {
            this.sendErrorToServer(errorDetails);
        }
    }

    /**
     * Send error details to server for logging
     * @param {Object} errorDetails - Error details to send
     */
    async sendErrorToServer(errorDetails) {
        try {
            await fetch(this.options.errorEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(errorDetails)
            });
        } catch (sendError) {
            console.warn('Failed to send error to server:', sendError);
        }
    }

    /**
     * Render error UI in the container
     */
    renderErrorUI() {
        if (!this.container) return;

        const errorHTML = this.createErrorHTML();
        this.container.innerHTML = errorHTML;

        // Add event listeners
        this.addErrorEventListeners();
    }

    /**
     * Create HTML for error display
     * @returns {string} HTML string for error display
     */
    createErrorHTML() {
        const isRetryable = this.options.allowRetry && this.retryCount < this.maxRetries;
        const errorMessage = this.getUserFriendlyMessage();

        return `
            <div class="scitrace-error-boundary">
                <div class="scitrace-error-content">
                    <div class="scitrace-error-icon">
                        <i class="fas fa-exclamation-triangle text-warning"></i>
                    </div>
                    <h3 class="scitrace-error-title">Oops! Something went wrong</h3>
                    <p class="scitrace-error-message">${errorMessage}</p>
                    ${this.options.showStackTrace && this.error ? `
                        <details class="scitrace-error-details">
                            <summary>Technical Details</summary>
                            <pre class="scitrace-error-stack">${this.error.stack}</pre>
                        </details>
                    ` : ''}
                    <div class="scitrace-error-actions">
                        ${isRetryable ? `
                            <button type="button" class="scitrace-btn scitrace-btn-primary scitrace-error-retry">
                                <i class="fas fa-redo"></i> Try Again
                            </button>
                        ` : ''}
                        <button type="button" class="scitrace-btn scitrace-btn-secondary scitrace-error-reload">
                            <i class="fas fa-refresh"></i> Reload Page
                        </button>
                        <button type="button" class="scitrace-btn scitrace-btn-outline-secondary scitrace-error-home">
                            <i class="fas fa-home"></i> Go Home
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Get user-friendly error message
     * @returns {string} User-friendly error message
     */
    getUserFriendlyMessage() {
        if (!this.error) return this.options.fallbackMessage;

        // Map common error codes to user-friendly messages
        const errorMessages = {
            'NETWORK_ERROR': 'Unable to connect to the server. Please check your internet connection and try again.',
            'TIMEOUT_ERROR': 'The request took too long to complete. Please try again.',
            'VALIDATION_ERROR': 'Please check your input and try again.',
            'AUTHENTICATION_ERROR': 'You need to log in to access this feature.',
            'AUTHORIZATION_ERROR': 'You don\'t have permission to perform this action.',
            'NOT_FOUND_ERROR': 'The requested resource was not found.',
            'SERVER_ERROR': 'The server encountered an error. Please try again later.',
            'UNKNOWN_ERROR': this.options.fallbackMessage
        };

        return errorMessages[this.error.code] || this.error.message || this.options.fallbackMessage;
    }

    /**
     * Add event listeners for error actions
     */
    addErrorEventListeners() {
        const retryBtn = this.container.querySelector('.scitrace-error-retry');
        const reloadBtn = this.container.querySelector('.scitrace-error-reload');
        const homeBtn = this.container.querySelector('.scitrace-error-home');

        if (retryBtn) {
            retryBtn.addEventListener('click', () => this.retry());
        }

        if (reloadBtn) {
            reloadBtn.addEventListener('click', () => window.location.reload());
        }

        if (homeBtn) {
            homeBtn.addEventListener('click', () => window.location.href = '/');
        }
    }

    /**
     * Retry the failed operation
     */
    retry() {
        this.retryCount++;
        this.error = null;
        
        if (this.options.onRetry) {
            this.options.onRetry();
        } else {
            // Default retry behavior - reload the page
            window.location.reload();
        }
    }

    /**
     * Clear the error and restore normal content
     */
    clear() {
        this.error = null;
        this.retryCount = 0;
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

/**
 * Global error handler for unhandled JavaScript errors
 */
class GlobalErrorHandler {
    constructor(options = {}) {
        this.options = {
            logErrors: true,
            showNotifications: true,
            errorEndpoint: null,
            ...options
        };
        this.init();
    }

    init() {
        // Handle unhandled JavaScript errors
        window.addEventListener('error', (event) => {
            this.handleError(event.error, {
                type: 'javascript_error',
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno
            });
        });

        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError(event.reason, {
                type: 'unhandled_promise_rejection'
            });
        });
    }

    handleError(error, errorInfo = {}) {
        if (this.options.logErrors) {
            console.error('Global Error:', error, errorInfo);
        }

        if (this.options.showNotifications) {
            this.showErrorNotification(error);
        }

        if (this.options.errorEndpoint) {
            this.sendErrorToServer(error, errorInfo);
        }
    }

    showErrorNotification(error) {
        const message = this.getUserFriendlyMessage(error);
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'scitrace-error-notification';
        notification.innerHTML = `
            <div class="scitrace-error-notification-content">
                <i class="fas fa-exclamation-triangle"></i>
                <span>${message}</span>
                <button type="button" class="scitrace-error-notification-close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        // Add to page
        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);

        // Add close button functionality
        const closeBtn = notification.querySelector('.scitrace-error-notification-close');
        closeBtn.addEventListener('click', () => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        });
    }

    getUserFriendlyMessage(error) {
        if (error instanceof SciTraceError) {
            return error.message;
        }

        // Map common error types to user-friendly messages
        if (error.name === 'TypeError') {
            return 'A technical error occurred. Please try again.';
        }
        if (error.name === 'ReferenceError') {
            return 'A technical error occurred. Please refresh the page.';
        }
        if (error.name === 'NetworkError') {
            return 'Network error. Please check your connection.';
        }

        return 'An unexpected error occurred. Please try again.';
    }

    async sendErrorToServer(error, errorInfo) {
        try {
            const errorDetails = {
                message: error.message,
                stack: error.stack,
                name: error.name,
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent,
                url: window.location.href,
                ...errorInfo
            };

            await fetch(this.options.errorEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(errorDetails)
            });
        } catch (sendError) {
            console.warn('Failed to send error to server:', sendError);
        }
    }
}

/**
 * API error handler for handling API response errors
 */
class APIErrorHandler {
    constructor(options = {}) {
        this.options = {
            showNotifications: true,
            logErrors: true,
            ...options
        };
    }

    /**
     * Handle API error response
     * @param {Response} response - Fetch response object
     * @param {Object} requestInfo - Information about the original request
     * @returns {Promise<SciTraceError>} Error object
     */
    async handleResponse(response, requestInfo = {}) {
        let errorData = null;
        
        try {
            errorData = await response.json();
        } catch (e) {
            // If response is not JSON, create a generic error
            errorData = {
                message: `HTTP ${response.status}: ${response.statusText}`,
                code: `HTTP_${response.status}`
            };
        }

        const error = new SciTraceError(
            errorData.message || 'An API error occurred',
            errorData.code || `HTTP_${response.status}`,
            {
                status: response.status,
                statusText: response.statusText,
                url: response.url,
                ...requestInfo
            }
        );

        if (this.options.logErrors) {
            console.error('API Error:', error);
        }

        if (this.options.showNotifications) {
            this.showErrorNotification(error);
        }

        return error;
    }

    showErrorNotification(error) {
        const message = this.getUserFriendlyMessage(error);
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'scitrace-error-notification scitrace-error-notification-api';
        notification.innerHTML = `
            <div class="scitrace-error-notification-content">
                <i class="fas fa-exclamation-triangle"></i>
                <span>${message}</span>
                <button type="button" class="scitrace-error-notification-close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        // Add to page
        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);

        // Add close button functionality
        const closeBtn = notification.querySelector('.scitrace-error-notification-close');
        closeBtn.addEventListener('click', () => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        });
    }

    getUserFriendlyMessage(error) {
        const status = error.details?.status;

        if (status === 401) {
            return 'You need to log in to access this feature.';
        }
        if (status === 403) {
            return 'You don\'t have permission to perform this action.';
        }
        if (status === 404) {
            return 'The requested resource was not found.';
        }
        if (status === 422) {
            return 'Please check your input and try again.';
        }
        if (status >= 500) {
            return 'The server encountered an error. Please try again later.';
        }

        return error.message || 'An API error occurred.';
    }
}

// Export classes for use in other modules
window.SciTraceError = SciTraceError;
window.ErrorBoundary = ErrorBoundary;
window.GlobalErrorHandler = GlobalErrorHandler;
window.APIErrorHandler = APIErrorHandler;
