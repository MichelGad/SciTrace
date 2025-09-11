/**
 * API utility functions for SciTrace
 * 
 * Provides common API request patterns and error handling.
 */

class ApiUtils {
    /**
     * Default API configuration
     */
    static config = {
        baseUrl: '/api',
        timeout: 30000,
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    };

    /**
     * Make a GET request
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise} - Response promise
     */
    static async get(endpoint, options = {}) {
        return this.request('GET', endpoint, null, options);
    }

    /**
     * Make a POST request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request data
     * @param {Object} options - Request options
     * @returns {Promise} - Response promise
     */
    static async post(endpoint, data = null, options = {}) {
        return this.request('POST', endpoint, data, options);
    }

    /**
     * Make a PUT request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request data
     * @param {Object} options - Request options
     * @returns {Promise} - Response promise
     */
    static async put(endpoint, data = null, options = {}) {
        return this.request('PUT', endpoint, data, options);
    }

    /**
     * Make a DELETE request
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise} - Response promise
     */
    static async delete(endpoint, options = {}) {
        return this.request('DELETE', endpoint, null, options);
    }

    /**
     * Make an API request
     * @param {string} method - HTTP method
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request data
     * @param {Object} options - Request options
     * @returns {Promise} - Response promise
     */
    static async request(method, endpoint, data = null, options = {}) {
        const url = endpoint.startsWith('http') ? endpoint : `${this.config.baseUrl}${endpoint}`;
        
        const requestOptions = {
            method: method.toUpperCase(),
            headers: { ...this.config.headers, ...options.headers },
            timeout: options.timeout || this.config.timeout,
            ...options
        };

        if (data && ['POST', 'PUT', 'PATCH'].includes(method.toUpperCase())) {
            requestOptions.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, requestOptions);
            const responseData = await response.json();

            if (!response.ok) {
                throw new ApiError(
                    responseData.error || `HTTP ${response.status}: ${response.statusText}`,
                    response.status,
                    responseData
                );
            }

            return responseData;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            
            // Handle network errors
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new ApiError('Network error: Could not connect to the server', 0, null);
            }
            
            // Handle timeout errors
            if (error.name === 'AbortError') {
                throw new ApiError('Request timeout: The server took too long to respond', 408, null);
            }
            
            throw new ApiError(`Request failed: ${error.message}`, 0, null);
        }
    }

    /**
     * Upload a file
     * @param {string} endpoint - API endpoint
     * @param {File} file - File to upload
     * @param {Object} options - Upload options
     * @returns {Promise} - Response promise
     */
    static async uploadFile(endpoint, file, options = {}) {
        const formData = new FormData();
        formData.append('file', file);

        if (options.additionalData) {
            Object.keys(options.additionalData).forEach(key => {
                formData.append(key, options.additionalData[key]);
            });
        }

        const url = endpoint.startsWith('http') ? endpoint : `${this.config.baseUrl}${endpoint}`;
        
        const requestOptions = {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                ...options.headers
            },
            timeout: options.timeout || this.config.timeout,
            ...options
        };

        // Remove Content-Type header to let browser set it with boundary
        delete requestOptions.headers['Content-Type'];

        try {
            const response = await fetch(url, requestOptions);
            const responseData = await response.json();

            if (!response.ok) {
                throw new ApiError(
                    responseData.error || `HTTP ${response.status}: ${response.statusText}`,
                    response.status,
                    responseData
                );
            }

            return responseData;
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(`Upload failed: ${error.message}`, 0, null);
        }
    }

    /**
     * Set default headers
     * @param {Object} headers - Headers to set
     */
    static setHeaders(headers) {
        this.config.headers = { ...this.config.headers, ...headers };
    }

    /**
     * Set base URL
     * @param {string} baseUrl - Base URL
     */
    static setBaseUrl(baseUrl) {
        this.config.baseUrl = baseUrl;
    }

    /**
     * Set timeout
     * @param {number} timeout - Timeout in milliseconds
     */
    static setTimeout(timeout) {
        this.config.timeout = timeout;
    }
}

/**
 * Custom API error class
 */
class ApiError extends Error {
    constructor(message, status, data) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.data = data;
    }
}

/**
 * Demo project utilities
 */
class DemoUtils {
    /**
     * Load demo projects
     * @returns {Promise} - Response promise
     */
    static async loadDemoProjects() {
        try {
            // Check prerequisites first
            await ApiUtils.post('/check-prerequisites');
            
            // Setup demo projects
            const response = await ApiUtils.post('/setup-demo');
            
            if (response.success) {
                return {
                    success: true,
                    message: response.message || 'Demo projects loaded successfully!'
                };
            } else {
                throw new ApiError(response.error || 'Failed to load demo projects', 500, response);
            }
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            throw new ApiError(`Demo setup failed: ${error.message}`, 0, null);
        }
    }

    /**
     * Check prerequisites
     * @returns {Promise} - Response promise
     */
    static async checkPrerequisites() {
        return ApiUtils.post('/check-prerequisites');
    }
}

/**
 * Dataflow utilities
 */
class DataflowUtils {
    /**
     * Regenerate dataflow
     * @param {number} dataflowId - Dataflow ID
     * @returns {Promise} - Response promise
     */
    static async regenerateDataflow(dataflowId) {
        return ApiUtils.post(`/dataflows/${dataflowId}/regenerate`);
    }

    /**
     * Get dataflow stage files
     * @param {number} dataflowId - Dataflow ID
     * @param {string} stageName - Stage name
     * @returns {Promise} - Response promise
     */
    static async getStageFiles(dataflowId, stageName) {
        return ApiUtils.get(`/dataflows/${dataflowId}/stage/${stageName}`);
    }

    /**
     * Get dataset info
     * @param {number} projectId - Project ID
     * @returns {Promise} - Response promise
     */
    static async getDatasetInfo(projectId) {
        return ApiUtils.get(`/projects/${projectId}/dataset-info`);
    }

    /**
     * Get file tree
     * @param {number} projectId - Project ID
     * @returns {Promise} - Response promise
     */
    static async getFileTree(projectId) {
        return ApiUtils.get(`/projects/${projectId}/file-tree`);
    }
}

/**
 * Project utilities
 */
class ProjectUtils {
    /**
     * Reset projects
     * @returns {Promise} - Response promise
     */
    static async resetProjects() {
        return ApiUtils.post('/reset-projects');
    }

    /**
     * Reset tasks
     * @returns {Promise} - Response promise
     */
    static async resetTasks() {
        return ApiUtils.post('/reset-tasks');
    }

    /**
     * Reset all data
     * @returns {Promise} - Response promise
     */
    static async resetAllData() {
        return ApiUtils.post('/reset-data');
    }
}

/**
 * Task utilities
 */
class TaskUtils {
    /**
     * Update task status
     * @param {number} taskId - Task ID
     * @param {string} status - New status
     * @returns {Promise} - Response promise
     */
    static async updateTaskStatus(taskId, status) {
        return ApiUtils.post(`/tasks/${taskId}/update-status`, { status });
    }

    /**
     * Delete task
     * @param {number} taskId - Task ID
     * @returns {Promise} - Response promise
     */
    static async deleteTask(taskId) {
        return ApiUtils.delete(`/tasks/${taskId}`);
    }
}

// Export for use in other scripts
window.ApiUtils = ApiUtils;
window.ApiError = ApiError;
window.DemoUtils = DemoUtils;
window.DataflowUtils = DataflowUtils;
window.ProjectUtils = ProjectUtils;
window.TaskUtils = TaskUtils;
