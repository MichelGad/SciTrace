/**
 * UI utility functions for SciTrace
 * 
 * Provides common UI patterns and interactions.
 */

class UiUtils {
    /**
     * Show loading state on a button
     * @param {HTMLElement} button - Button element
     * @param {string} loadingText - Text to show while loading
     * @returns {Object} - Object with restore function
     */
    static showButtonLoading(button, loadingText = 'Loading...') {
        const originalText = button.innerHTML;
        const originalDisabled = button.disabled;
        
        button.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${loadingText}`;
        button.disabled = true;
        
        return {
            restore: () => {
                button.innerHTML = originalText;
                button.disabled = originalDisabled;
            }
        };
    }

    /**
     * Show alert message
     * @param {string} message - Alert message
     * @param {string} type - Alert type (success, error, warning, info)
     * @param {number} duration - Auto-hide duration in ms (0 = no auto-hide)
     */
    static showAlert(message, type = 'info', duration = 5000) {
        const alertId = `alert-${Date.now()}`;
        const alertHtml = `
            <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="fas fa-${this.getAlertIcon(type)} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        // Insert at the top of the container
        const container = document.querySelector('.container-fluid') || document.body;
        container.insertAdjacentHTML('afterbegin', alertHtml);
        
        // Auto-hide if duration is specified
        if (duration > 0) {
            setTimeout(() => {
                const alert = document.getElementById(alertId);
                if (alert) {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }
            }, duration);
        }
    }

    /**
     * Get icon for alert type
     * @param {string} type - Alert type
     * @returns {string} - Icon class
     */
    static getAlertIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    /**
     * Show confirmation dialog
     * @param {string} message - Confirmation message
     * @param {string} title - Dialog title
     * @returns {Promise<boolean>} - True if confirmed, false if cancelled
     */
    static async showConfirmation(message, title = 'Confirm') {
        return new Promise((resolve) => {
            const modalId = `confirm-modal-${Date.now()}`;
            const modalHtml = `
                <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}-label" aria-hidden="true">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="${modalId}-label">
                                    <i class="fas fa-question-circle me-2"></i>${title}
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <p>${message}</p>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                    <i class="fas fa-times me-1"></i>Cancel
                                </button>
                                <button type="button" class="btn btn-primary" id="${modalId}-confirm">
                                    <i class="fas fa-check me-1"></i>Confirm
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            const modal = new bootstrap.Modal(document.getElementById(modalId));
            
            const confirmBtn = document.getElementById(`${modalId}-confirm`);
            const cancelBtn = document.querySelector(`#${modalId} .btn-secondary`);
            
            const cleanup = () => {
                modal.dispose();
                document.getElementById(modalId).remove();
            };
            
            confirmBtn.addEventListener('click', () => {
                cleanup();
                resolve(true);
            });
            
            cancelBtn.addEventListener('click', () => {
                cleanup();
                resolve(false);
            });
            
            modal.show();
        });
    }

    /**
     * Show loading overlay
     * @param {string} message - Loading message
     * @returns {Object} - Object with hide function
     */
    static showLoadingOverlay(message = 'Loading...') {
        const overlayId = `loading-overlay-${Date.now()}`;
        const overlayHtml = `
            <div id="${overlayId}" class="loading-overlay">
                <div class="loading-content">
                    <div class="spinner-border text-primary mb-3" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mb-0">${message}</p>
                </div>
            </div>
        `;
        
        // Add styles if not already present
        if (!document.getElementById('loading-overlay-styles')) {
            const styles = `
                <style id="loading-overlay-styles">
                    .loading-overlay {
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        background-color: rgba(0, 0, 0, 0.5);
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        z-index: 9999;
                    }
                    .loading-content {
                        background: white;
                        padding: 2rem;
                        border-radius: 0.5rem;
                        text-align: center;
                        box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
                    }
                </style>
            `;
            document.head.insertAdjacentHTML('beforeend', styles);
        }
        
        document.body.insertAdjacentHTML('beforeend', overlayHtml);
        
        return {
            hide: () => {
                const overlay = document.getElementById(overlayId);
                if (overlay) {
                    overlay.remove();
                }
            }
        };
    }

    /**
     * Format file size
     * @param {number} bytes - File size in bytes
     * @returns {string} - Formatted file size
     */
    static formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    /**
     * Format date
     * @param {Date|string} date - Date to format
     * @param {Object} options - Formatting options
     * @returns {string} - Formatted date
     */
    static formatDate(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        
        const formatOptions = { ...defaultOptions, ...options };
        return new Date(date).toLocaleDateString('en-US', formatOptions);
    }

    /**
     * Format relative time
     * @param {Date|string} date - Date to format
     * @returns {string} - Relative time string
     */
    static formatRelativeTime(date) {
        const now = new Date();
        const targetDate = new Date(date);
        const diffMs = now - targetDate;
        const diffSeconds = Math.floor(diffMs / 1000);
        const diffMinutes = Math.floor(diffSeconds / 60);
        const diffHours = Math.floor(diffMinutes / 60);
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffSeconds < 60) {
            return 'just now';
        } else if (diffMinutes < 60) {
            return `${diffMinutes} minute${diffMinutes !== 1 ? 's' : ''} ago`;
        } else if (diffHours < 24) {
            return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
        } else if (diffDays < 7) {
            return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
        } else {
            return this.formatDate(date, { year: 'numeric', month: 'short', day: 'numeric' });
        }
    }

    /**
     * Copy text to clipboard
     * @param {string} text - Text to copy
     * @returns {Promise<boolean>} - True if successful
     */
    static async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
                document.body.removeChild(textArea);
                return true;
            } catch (err) {
                document.body.removeChild(textArea);
                return false;
            }
        }
    }

    /**
     * Debounce function
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @returns {Function} - Debounced function
     */
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Throttle function
     * @param {Function} func - Function to throttle
     * @param {number} limit - Time limit in milliseconds
     * @returns {Function} - Throttled function
     */
    static throttle(func, limit) {
        let inThrottle;
        return function executedFunction(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    /**
     * Smooth scroll to element
     * @param {string|HTMLElement} target - Target element or selector
     * @param {Object} options - Scroll options
     */
    static smoothScrollTo(target, options = {}) {
        const element = typeof target === 'string' ? document.querySelector(target) : target;
        if (element) {
            element.scrollIntoView({
                behavior: 'smooth',
                block: 'start',
                ...options
            });
        }
    }

    /**
     * Toggle element visibility
     * @param {string|HTMLElement} target - Target element or selector
     * @param {boolean} show - Whether to show or hide
     */
    static toggleVisibility(target, show = null) {
        const element = typeof target === 'string' ? document.querySelector(target) : target;
        if (element) {
            if (show === null) {
                element.style.display = element.style.display === 'none' ? '' : 'none';
            } else {
                element.style.display = show ? '' : 'none';
            }
        }
    }

    /**
     * Add loading class to element
     * @param {string|HTMLElement} target - Target element or selector
     * @param {boolean} loading - Whether to add or remove loading class
     */
    static setLoading(target, loading = true) {
        const element = typeof target === 'string' ? document.querySelector(target) : target;
        if (element) {
            if (loading) {
                element.classList.add('loading');
            } else {
                element.classList.remove('loading');
            }
        }
    }

    /**
     * Show tooltip
     * @param {string|HTMLElement} target - Target element or selector
     * @param {string} title - Tooltip title
     * @param {Object} options - Tooltip options
     */
    static showTooltip(target, title, options = {}) {
        const element = typeof target === 'string' ? document.querySelector(target) : target;
        if (element && typeof bootstrap !== 'undefined') {
            const tooltip = new bootstrap.Tooltip(element, {
                title: title,
                ...options
            });
            tooltip.show();
        }
    }

    /**
     * Hide tooltip
     * @param {string|HTMLElement} target - Target element or selector
     */
    static hideTooltip(target) {
        const element = typeof target === 'string' ? document.querySelector(target) : target;
        if (element && typeof bootstrap !== 'undefined') {
            const tooltip = bootstrap.Tooltip.getInstance(element);
            if (tooltip) {
                tooltip.hide();
            }
        }
    }
}

// Export for use in other scripts
window.UiUtils = UiUtils;
