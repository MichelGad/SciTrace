# SciTrace API Error Handling Guide

This document provides detailed information about error handling patterns, best practices, and troubleshooting for the SciTrace API.

## Table of Contents

1. [Error Response Format](#error-response-format)
2. [HTTP Status Codes](#http-status-codes)
3. [Error Codes](#error-codes)
4. [Error Handling Patterns](#error-handling-patterns)
5. [Client-Side Error Handling](#client-side-error-handling)
6. [Server-Side Error Handling](#server-side-error-handling)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Error Response Format

All API error responses follow a consistent format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Additional error details (optional)
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Error Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always `false` for error responses |
| `error` | object | Error information object |
| `error.code` | string | Machine-readable error code |
| `error.message` | string | Human-readable error message |
| `error.details` | object | Additional error details (optional) |
| `timestamp` | string | ISO 8601 timestamp of when the error occurred |

## HTTP Status Codes

SciTrace API uses standard HTTP status codes to indicate the result of API requests:

### 2xx Success

| Status Code | Description | Usage |
|-------------|-------------|-------|
| 200 | OK | Successful GET, PUT, PATCH requests |
| 201 | Created | Successful POST requests that create resources |

### 4xx Client Errors

| Status Code | Description | Usage |
|-------------|-------------|-------|
| 400 | Bad Request | Invalid request syntax or parameters |
| 401 | Unauthorized | Authentication required or failed |
| 403 | Forbidden | Authenticated but insufficient permissions |
| 404 | Not Found | Requested resource does not exist |
| 422 | Unprocessable Entity | Request is well-formed but contains validation errors |

### 5xx Server Errors

| Status Code | Description | Usage |
|-------------|-------------|-------|
| 500 | Internal Server Error | Unexpected server error |

## Error Codes

### Authentication and Authorization

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `AUTHENTICATION_ERROR` | 401 | User is not authenticated |
| `AUTHORIZATION_ERROR` | 403 | User lacks required permissions |
| `SESSION_EXPIRED` | 401 | User session has expired |

### Validation

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `VALIDATION_ERROR` | 422 | Input validation failed |
| `REQUIRED_FIELD_MISSING` | 422 | Required field is missing |
| `INVALID_FORMAT` | 422 | Field format is invalid |
| `FIELD_TOO_LONG` | 422 | Field exceeds maximum length |
| `FIELD_TOO_SHORT` | 422 | Field is below minimum length |

### Resource Management

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `NOT_FOUND_ERROR` | 404 | Requested resource not found |
| `DUPLICATE_RESOURCE` | 422 | Resource already exists |
| `RESOURCE_IN_USE` | 422 | Resource cannot be deleted because it's in use |

### File Operations

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `FILE_NOT_FOUND` | 404 | File does not exist |
| `FILE_ACCESS_DENIED` | 403 | Insufficient permissions to access file |
| `INVALID_PATH` | 422 | File path is invalid or unsafe |
| `FILE_TOO_LARGE` | 422 | File exceeds size limit |

### Network and System

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `NETWORK_ERROR` | 500 | Network connectivity issue |
| `TIMEOUT_ERROR` | 500 | Request timeout |
| `SERVER_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 500 | Service temporarily unavailable |

### DataLad Operations

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `DATALAD_ERROR` | 500 | DataLad operation failed |
| `GIT_ERROR` | 500 | Git operation failed |
| `REPOSITORY_ERROR` | 500 | Repository operation failed |

## Error Handling Patterns

### 1. Validation Errors

Validation errors occur when request data doesn't meet the required format or constraints.

**Example Request:**
```http
POST /api/projects
Content-Type: application/json

{
  "name": "",
  "description": "A project with an empty name"
}
```

**Example Response:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "fields": {
        "name": ["Name is required and cannot be empty"]
      }
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 2. Authentication Errors

Authentication errors occur when the user is not logged in or the session is invalid.

**Example Response:**
```json
{
  "success": false,
  "error": {
    "code": "AUTHENTICATION_ERROR",
    "message": "Authentication required",
    "details": {
      "login_url": "/auth/login"
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 3. Authorization Errors

Authorization errors occur when the user is authenticated but lacks the required permissions.

**Example Response:**
```json
{
  "success": false,
  "error": {
    "code": "AUTHORIZATION_ERROR",
    "message": "Insufficient permissions",
    "details": {
      "required_permission": "admin",
      "user_permissions": ["user"]
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 4. Resource Not Found Errors

Resource not found errors occur when the requested resource doesn't exist.

**Example Response:**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND_ERROR",
    "message": "Resource not found",
    "details": {
      "resource_type": "project",
      "resource_id": "999"
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 5. Server Errors

Server errors occur when there's an unexpected problem on the server side.

**Example Response:**
```json
{
  "success": false,
  "error": {
    "code": "SERVER_ERROR",
    "message": "Internal server error",
    "details": {
      "error_id": "err_123456789",
      "support_contact": "support@scitrace.com"
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Client-Side Error Handling

### JavaScript Error Handling

```javascript
async function handleApiRequest(url, options = {}) {
  try {
    const response = await fetch(url, options);
    const result = await response.json();

    if (!result.success) {
      // Handle API error
      handleApiError(result.error, response.status);
      return null;
    }

    return result.data;
  } catch (error) {
    // Handle network error
    handleNetworkError(error);
    return null;
  }
}

function handleApiError(error, status) {
  switch (error.code) {
    case 'AUTHENTICATION_ERROR':
      // Redirect to login
      window.location.href = '/auth/login';
      break;
    case 'AUTHORIZATION_ERROR':
      // Show permission denied message
      showError('You don\'t have permission to perform this action.');
      break;
    case 'VALIDATION_ERROR':
      // Show validation errors
      showValidationErrors(error.details.fields);
      break;
    case 'NOT_FOUND_ERROR':
      // Show not found message
      showError('The requested resource was not found.');
      break;
    default:
      // Show generic error message
      showError(error.message || 'An unexpected error occurred.');
  }
}

function handleNetworkError(error) {
  console.error('Network error:', error);
  showError('Network error. Please check your connection and try again.');
}
```

### Python Error Handling

```python
import requests
from requests.exceptions import RequestException

def handle_api_request(url, method='GET', data=None):
    try:
        if method.upper() == 'GET':
            response = requests.get(url)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data)
        elif method.upper() == 'DELETE':
            response = requests.delete(url)
        
        result = response.json()
        
        if not result['success']:
            handle_api_error(result['error'], response.status_code)
            return None
        
        return result['data']
        
    except RequestException as e:
        handle_network_error(e)
        return None

def handle_api_error(error, status_code):
    error_code = error['code']
    
    if error_code == 'AUTHENTICATION_ERROR':
        print('Authentication required. Please log in.')
    elif error_code == 'AUTHORIZATION_ERROR':
        print('Insufficient permissions.')
    elif error_code == 'VALIDATION_ERROR':
        print('Validation errors:', error['details']['fields'])
    elif error_code == 'NOT_FOUND_ERROR':
        print('Resource not found.')
    else:
        print('Error:', error['message'])

def handle_network_error(error):
    print('Network error:', str(error))
```

## Server-Side Error Handling

### Flask Error Handling

```python
from flask import jsonify
from scitrace.utils.response_utils import create_error_response

@app.errorhandler(400)
def bad_request(error):
    return create_error_response(
        code='BAD_REQUEST',
        message='Invalid request',
        status_code=400
    )

@app.errorhandler(401)
def unauthorized(error):
    return create_error_response(
        code='AUTHENTICATION_ERROR',
        message='Authentication required',
        status_code=401,
        details={'login_url': '/auth/login'}
    )

@app.errorhandler(403)
def forbidden(error):
    return create_error_response(
        code='AUTHORIZATION_ERROR',
        message='Insufficient permissions',
        status_code=403
    )

@app.errorhandler(404)
def not_found(error):
    return create_error_response(
        code='NOT_FOUND_ERROR',
        message='Resource not found',
        status_code=404
    )

@app.errorhandler(422)
def unprocessable_entity(error):
    return create_error_response(
        code='VALIDATION_ERROR',
        message='Validation failed',
        status_code=422,
        details={'fields': get_validation_errors(error)}
    )

@app.errorhandler(500)
def internal_server_error(error):
    return create_error_response(
        code='SERVER_ERROR',
        message='Internal server error',
        status_code=500,
        details={'error_id': generate_error_id()}
    )
```

### Custom Exception Handling

```python
from scitrace.exceptions import SciTraceException

class ValidationException(SciTraceException):
    def __init__(self, message, field_errors=None):
        super().__init__(message, 'VALIDATION_ERROR')
        self.field_errors = field_errors or {}

class AuthenticationException(SciTraceException):
    def __init__(self, message="Authentication required"):
        super().__init__(message, 'AUTHENTICATION_ERROR')

class AuthorizationException(SciTraceException):
    def __init__(self, message="Insufficient permissions"):
        super().__init__(message, 'AUTHORIZATION_ERROR')

class NotFoundException(SciTraceException):
    def __init__(self, message="Resource not found", resource_type=None, resource_id=None):
        super().__init__(message, 'NOT_FOUND_ERROR')
        self.resource_type = resource_type
        self.resource_id = resource_id

# Usage in route handlers
@app.route('/api/projects/<int:project_id>')
def get_project(project_id):
    try:
        project = project_service.get_project(project_id)
        if not project:
            raise NotFoundException(
                message="Project not found",
                resource_type="project",
                resource_id=project_id
            )
        return create_success_response(data={'project': project})
    except SciTraceException as e:
        return create_error_response(
            code=e.code,
            message=e.message,
            details=e.details
        )
```

## Troubleshooting

### Common Issues

#### 1. Authentication Errors

**Problem:** Getting 401 errors even when logged in.

**Solutions:**
- Check if the session cookie is being sent with requests
- Verify the session hasn't expired
- Ensure the user is properly logged in

#### 2. Validation Errors

**Problem:** Getting 422 errors with unclear validation messages.

**Solutions:**
- Check the `details.fields` object for specific field errors
- Verify all required fields are provided
- Check field formats and constraints

#### 3. Network Errors

**Problem:** Getting network errors or timeouts.

**Solutions:**
- Check internet connectivity
- Verify the server is running
- Check for firewall or proxy issues
- Implement retry logic with exponential backoff

#### 4. Server Errors

**Problem:** Getting 500 errors.

**Solutions:**
- Check server logs for detailed error information
- Verify all required services are running
- Check database connectivity
- Contact support with the error ID if provided

### Debugging Tips

1. **Enable detailed logging**: Set log level to DEBUG to see detailed error information.

2. **Check network tab**: Use browser developer tools to inspect request/response details.

3. **Validate request format**: Ensure requests match the expected format exactly.

4. **Test with cURL**: Use cURL to test API endpoints directly.

5. **Check server logs**: Review server logs for detailed error information.

## Best Practices

### Client-Side Best Practices

1. **Always check response status**: Don't assume requests will succeed.

2. **Handle different error types**: Implement specific handling for different error codes.

3. **Provide user feedback**: Show appropriate error messages to users.

4. **Implement retry logic**: For network errors, implement exponential backoff.

5. **Log errors**: Log errors for debugging while being mindful of sensitive information.

6. **Validate input**: Validate input on the client side before sending requests.

### Server-Side Best Practices

1. **Use consistent error formats**: All errors should follow the standard format.

2. **Provide meaningful messages**: Error messages should be helpful to both developers and users.

3. **Include error codes**: Use consistent error codes for programmatic handling.

4. **Log errors**: Log all errors with appropriate detail levels.

5. **Handle edge cases**: Consider and handle edge cases that might cause errors.

6. **Validate input**: Always validate and sanitize input data.

7. **Use appropriate status codes**: Use the correct HTTP status codes for different error types.

### Security Best Practices

1. **Don't expose sensitive information**: Error messages shouldn't reveal sensitive system information.

2. **Log security events**: Log authentication and authorization failures.

3. **Rate limit error responses**: Prevent error response abuse.

4. **Validate error details**: Ensure error details don't contain malicious content.

5. **Use HTTPS**: Always use HTTPS in production to protect error responses.

## Error Monitoring

### Client-Side Monitoring

```javascript
// Send errors to monitoring service
function reportError(error, context) {
  if (typeof window.errorReportingService !== 'undefined') {
    window.errorReportingService.report({
      error: error,
      context: context,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    });
  }
}

// Usage
try {
  // API call
} catch (error) {
  reportError(error, { endpoint: '/api/projects', method: 'POST' });
  throw error;
}
```

### Server-Side Monitoring

```python
import logging
from scitrace.utils.logging_utils import get_logger

logger = get_logger(__name__)

def log_error(error, context=None):
    logger.error(
        f"API Error: {error.code} - {error.message}",
        extra={
            'error_code': error.code,
            'error_message': error.message,
            'error_details': error.details,
            'context': context,
            'timestamp': datetime.utcnow().isoformat()
        }
    )

# Usage
try:
    # API operation
except SciTraceException as e:
    log_error(e, {'endpoint': '/api/projects', 'method': 'POST'})
    return create_error_response(e.code, e.message, e.details)
```

## Conclusion

Proper error handling is crucial for building robust and user-friendly applications. By following the patterns and best practices outlined in this guide, you can ensure that your SciTrace API integration handles errors gracefully and provides a good user experience.

For additional support or questions about error handling, please refer to the main API documentation or contact the development team.
