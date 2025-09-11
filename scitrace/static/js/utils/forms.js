/**
 * Form utility functions for SciTrace
 * 
 * Provides common form validation and handling patterns.
 */

class FormUtils {
    /**
     * Validate email address
     * @param {string} email - Email to validate
     * @returns {boolean} - True if valid
     */
    static validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * Validate password strength
     * @param {string} password - Password to validate
     * @returns {Object} - Validation result with score and feedback
     */
    static validatePassword(password) {
        const result = {
            isValid: false,
            score: 0,
            feedback: []
        };

        if (password.length < 8) {
            result.feedback.push('Password must be at least 8 characters long');
        } else {
            result.score += 1;
        }

        if (!/[a-z]/.test(password)) {
            result.feedback.push('Password must contain at least one lowercase letter');
        } else {
            result.score += 1;
        }

        if (!/[A-Z]/.test(password)) {
            result.feedback.push('Password must contain at least one uppercase letter');
        } else {
            result.score += 1;
        }

        if (!/\d/.test(password)) {
            result.feedback.push('Password must contain at least one number');
        } else {
            result.score += 1;
        }

        if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
            result.feedback.push('Password must contain at least one special character');
        } else {
            result.score += 1;
        }

        result.isValid = result.score >= 4;
        return result;
    }

    /**
     * Validate required fields
     * @param {Object} data - Form data object
     * @param {Array} requiredFields - Array of required field names
     * @returns {Object} - Validation result
     */
    static validateRequired(data, requiredFields) {
        const result = {
            isValid: true,
            errors: {}
        };

        requiredFields.forEach(field => {
            if (!data[field] || (typeof data[field] === 'string' && data[field].trim() === '')) {
                result.isValid = false;
                result.errors[field] = `${this.formatFieldName(field)} is required`;
            }
        });

        return result;
    }

    /**
     * Format field name for display
     * @param {string} fieldName - Field name
     * @returns {string} - Formatted field name
     */
    static formatFieldName(fieldName) {
        return fieldName
            .replace(/([A-Z])/g, ' $1')
            .replace(/^./, str => str.toUpperCase())
            .trim();
    }

    /**
     * Serialize form data
     * @param {HTMLFormElement} form - Form element
     * @returns {Object} - Serialized form data
     */
    static serializeForm(form) {
        const formData = new FormData(form);
        const data = {};

        for (let [key, value] of formData.entries()) {
            if (data[key]) {
                // Handle multiple values (e.g., checkboxes)
                if (Array.isArray(data[key])) {
                    data[key].push(value);
                } else {
                    data[key] = [data[key], value];
                }
            } else {
                data[key] = value;
            }
        }

        return data;
    }

    /**
     * Clear form validation
     * @param {HTMLFormElement} form - Form element
     */
    static clearFormValidation(form) {
        const inputs = form.querySelectorAll('.is-invalid, .is-valid');
        inputs.forEach(input => {
            input.classList.remove('is-invalid', 'is-valid');
        });

        const feedback = form.querySelectorAll('.invalid-feedback, .valid-feedback');
        feedback.forEach(fb => fb.remove());
    }

    /**
     * Show field validation error
     * @param {HTMLElement} field - Form field element
     * @param {string} message - Error message
     */
    static showFieldError(field, message) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');

        // Remove existing feedback
        const existingFeedback = field.parentNode.querySelector('.invalid-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }

        // Add new feedback
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        feedback.textContent = message;
        field.parentNode.appendChild(feedback);
    }

    /**
     * Show field validation success
     * @param {HTMLElement} field - Form field element
     * @param {string} message - Success message
     */
    static showFieldSuccess(field, message) {
        field.classList.add('is-valid');
        field.classList.remove('is-invalid');

        // Remove existing feedback
        const existingFeedback = field.parentNode.querySelector('.valid-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }

        // Add new feedback
        const feedback = document.createElement('div');
        feedback.className = 'valid-feedback';
        feedback.textContent = message;
        field.parentNode.appendChild(feedback);
    }

    /**
     * Validate and show form errors
     * @param {HTMLFormElement} form - Form element
     * @param {Object} errors - Validation errors object
     */
    static showFormErrors(form, errors) {
        this.clearFormValidation(form);

        Object.keys(errors).forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                this.showFieldError(field, errors[fieldName]);
            }
        });
    }

    /**
     * Auto-resize textarea
     * @param {HTMLTextAreaElement} textarea - Textarea element
     */
    static autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    }

    /**
     * Initialize auto-resize for all textareas
     * @param {string} selector - Textarea selector
     */
    static initAutoResizeTextareas(selector = 'textarea') {
        const textareas = document.querySelectorAll(selector);
        textareas.forEach(textarea => {
            textarea.addEventListener('input', () => {
                this.autoResizeTextarea(textarea);
            });
            
            // Initial resize
            this.autoResizeTextarea(textarea);
        });
    }

    /**
     * Format form data for API submission
     * @param {Object} data - Form data
     * @param {Object} options - Formatting options
     * @returns {Object} - Formatted data
     */
    static formatForApi(data, options = {}) {
        const formatted = { ...data };

        // Convert empty strings to null
        if (options.nullifyEmpty) {
            Object.keys(formatted).forEach(key => {
                if (formatted[key] === '') {
                    formatted[key] = null;
                }
            });
        }

        // Convert string numbers to actual numbers
        if (options.parseNumbers) {
            Object.keys(formatted).forEach(key => {
                if (typeof formatted[key] === 'string' && !isNaN(formatted[key]) && formatted[key] !== '') {
                    formatted[key] = parseFloat(formatted[key]);
                }
            });
        }

        // Convert string booleans to actual booleans
        if (options.parseBooleans) {
            Object.keys(formatted).forEach(key => {
                if (formatted[key] === 'true') {
                    formatted[key] = true;
                } else if (formatted[key] === 'false') {
                    formatted[key] = false;
                }
            });
        }

        return formatted;
    }

    /**
     * Create form validator
     * @param {Object} rules - Validation rules
     * @returns {Function} - Validator function
     */
    static createValidator(rules) {
        return (data) => {
            const result = {
                isValid: true,
                errors: {}
            };

            Object.keys(rules).forEach(field => {
                const value = data[field];
                const fieldRules = rules[field];

                // Required validation
                if (fieldRules.required && (!value || (typeof value === 'string' && value.trim() === ''))) {
                    result.isValid = false;
                    result.errors[field] = fieldRules.requiredMessage || `${this.formatFieldName(field)} is required`;
                    return;
                }

                // Skip other validations if field is empty and not required
                if (!value || (typeof value === 'string' && value.trim() === '')) {
                    return;
                }

                // Email validation
                if (fieldRules.email && !this.validateEmail(value)) {
                    result.isValid = false;
                    result.errors[field] = fieldRules.emailMessage || 'Please enter a valid email address';
                }

                // Min length validation
                if (fieldRules.minLength && value.length < fieldRules.minLength) {
                    result.isValid = false;
                    result.errors[field] = fieldRules.minLengthMessage || `${this.formatFieldName(field)} must be at least ${fieldRules.minLength} characters long`;
                }

                // Max length validation
                if (fieldRules.maxLength && value.length > fieldRules.maxLength) {
                    result.isValid = false;
                    result.errors[field] = fieldRules.maxLengthMessage || `${this.formatFieldName(field)} must be no more than ${fieldRules.maxLength} characters long`;
                }

                // Pattern validation
                if (fieldRules.pattern && !fieldRules.pattern.test(value)) {
                    result.isValid = false;
                    result.errors[field] = fieldRules.patternMessage || `${this.formatFieldName(field)} format is invalid`;
                }

                // Custom validation
                if (fieldRules.custom && typeof fieldRules.custom === 'function') {
                    const customResult = fieldRules.custom(value, data);
                    if (customResult !== true) {
                        result.isValid = false;
                        result.errors[field] = customResult || `${this.formatFieldName(field)} is invalid`;
                    }
                }
            });

            return result;
        };
    }

    /**
     * Handle form submission with validation
     * @param {HTMLFormElement} form - Form element
     * @param {Function} validator - Validator function
     * @param {Function} submitHandler - Submit handler function
     * @param {Object} options - Options
     */
    static handleFormSubmission(form, validator, submitHandler, options = {}) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = this.serializeForm(form);
            const validation = validator(formData);

            if (!validation.isValid) {
                this.showFormErrors(form, validation.errors);
                return;
            }

            // Clear previous validation
            this.clearFormValidation(form);

            // Show loading state
            const submitButton = form.querySelector('button[type="submit"]');
            const loadingState = submitButton ? UiUtils.showButtonLoading(submitButton, options.loadingText || 'Submitting...') : null;

            try {
                const formattedData = this.formatForApi(formData, options.formatOptions || {});
                await submitHandler(formattedData);
                
                if (options.successMessage) {
                    UiUtils.showAlert(options.successMessage, 'success');
                }
                
                if (options.resetOnSuccess) {
                    form.reset();
                }
                
                if (options.redirectOnSuccess) {
                    window.location.href = options.redirectOnSuccess;
                }
            } catch (error) {
                console.error('Form submission error:', error);
                
                if (error.errors) {
                    this.showFormErrors(form, error.errors);
                } else {
                    UiUtils.showAlert(error.message || 'An error occurred while submitting the form', 'error');
                }
            } finally {
                if (loadingState) {
                    loadingState.restore();
                }
            }
        });
    }
}

// Export for use in other scripts
window.FormUtils = FormUtils;
