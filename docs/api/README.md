# API Reference

SciTrace provides a comprehensive RESTful API for programmatic access to all features. This documentation covers all available endpoints, request/response formats, and authentication.

## 🔗 Base URL

All API endpoints are prefixed with `/api/`:

```
http://localhost:5001/api/
```

## 🔐 Authentication

SciTrace uses session-based authentication. All API endpoints require authentication unless otherwise specified.

### Authentication Methods

#### Session Authentication (Default)
- **Login**: `POST /auth/login`
- **Logout**: `POST /auth/logout`
- **Session**: Maintained via cookies

#### API Key Authentication (Future)
- **Header**: `Authorization: Bearer <api_key>`
- **Usage**: For external integrations

## 📊 Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    // Additional error details
  }
}
```

### HTTP Status Codes
- **200**: Success
- **201**: Created
- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **500**: Internal Server Error

## 🏗️ API Endpoints

### Authentication API

#### Login
```http
POST /auth/login
```

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@scitrace.org",
    "role": "admin"
  }
}
```

#### Logout
```http
POST /auth/logout
```

**Response:**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

#### Register
```http
POST /auth/register
```

**Request Body:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "name": "New User"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Registration successful",
  "user": {
    "id": 2,
    "username": "newuser",
    "email": "user@example.com",
    "role": "user"
  }
}
```

### Project API

#### List Projects
```http
GET /api/projects
```

**Response:**
```json
{
  "success": true,
  "projects": [
    {
      "id": 1,
      "name": "Environmental Research",
      "description": "Water quality analysis project",
      "research_type": "environmental",
      "created_at": "2025-09-11T00:00:00Z",
      "user_id": 1,
      "dataflow_count": 2,
      "task_count": 5
    }
  ]
}
```

#### Create Project
```http
POST /api/projects
```

**Request Body:**
```json
{
  "name": "New Project",
  "description": "Project description",
  "research_type": "environmental",
  "collaborators": ["user1", "user2"]
}
```

**Response:**
```json
{
  "success": true,
  "project": {
    "id": 2,
    "name": "New Project",
    "description": "Project description",
    "research_type": "environmental",
    "created_at": "2025-09-11T00:00:00Z",
    "user_id": 1
  }
}
```

#### Get Project
```http
GET /api/projects/{project_id}
```

**Response:**
```json
{
  "success": true,
  "project": {
    "id": 1,
    "name": "Environmental Research",
    "description": "Water quality analysis project",
    "research_type": "environmental",
    "created_at": "2025-09-11T00:00:00Z",
    "user_id": 1,
    "dataflows": [
      {
        "id": 1,
        "name": "Water Quality Analysis",
        "path": "/path/to/dataset",
        "created_at": "2025-09-11T00:00:00Z"
      }
    ],
    "tasks": [
      {
        "id": 1,
        "title": "Data Collection",
        "description": "Collect water samples",
        "status": "in_progress",
        "priority": "high",
        "deadline": "2025-09-15T00:00:00Z"
      }
    ]
  }
}
```

#### Update Project
```http
PUT /api/projects/{project_id}
```

**Request Body:**
```json
{
  "name": "Updated Project Name",
  "description": "Updated description",
  "research_type": "biomedical"
}
```

**Response:**
```json
{
  "success": true,
  "project": {
    "id": 1,
    "name": "Updated Project Name",
    "description": "Updated description",
    "research_type": "biomedical",
    "updated_at": "2025-09-11T00:00:00Z"
  }
}
```

#### Delete Project
```http
DELETE /api/projects/{project_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Project deleted successfully"
}
```

### Dataflow API

#### List Dataflows
```http
GET /api/dataflows
```

**Query Parameters:**
- `project_id` (optional): Filter by project ID

**Response:**
```json
{
  "success": true,
  "dataflows": [
    {
      "id": 1,
      "name": "Water Quality Analysis",
      "project_id": 1,
      "path": "/path/to/dataset",
      "created_at": "2025-09-11T00:00:00Z",
      "file_count": 15,
      "last_commit": "2025-09-11T00:00:00Z"
    }
  ]
}
```

#### Create Dataflow
```http
POST /api/dataflows
```

**Request Body:**
```json
{
  "name": "New Dataflow",
  "project_id": 1,
  "storage_location": "/path/to/storage",
  "research_type": "environmental"
}
```

**Response:**
```json
{
  "success": true,
  "dataflow": {
    "id": 2,
    "name": "New Dataflow",
    "project_id": 1,
    "path": "/path/to/storage/new_dataflow",
    "created_at": "2025-09-11T00:00:00Z"
  }
}
```

#### Get Dataflow
```http
GET /api/dataflows/{dataflow_id}
```

**Response:**
```json
{
  "success": true,
  "dataflow": {
    "id": 1,
    "name": "Water Quality Analysis",
    "project_id": 1,
    "path": "/path/to/dataset",
    "created_at": "2025-09-11T00:00:00Z",
    "files": [
      {
        "name": "data.csv",
        "path": "raw_data/data.csv",
        "size": 1024,
        "modified": "2025-09-11T00:00:00Z",
        "status": "tracked"
      }
    ],
    "structure": {
      "raw_data": ["data.csv", "metadata.json"],
      "scripts": ["analysis.py", "visualization.R"],
      "results": ["output.csv"],
      "plots": ["chart.png"]
    }
  }
}
```

#### Update Dataflow
```http
PUT /api/dataflows/{dataflow_id}
```

**Request Body:**
```json
{
  "name": "Updated Dataflow Name"
}
```

**Response:**
```json
{
  "success": true,
  "dataflow": {
    "id": 1,
    "name": "Updated Dataflow Name",
    "updated_at": "2025-09-11T00:00:00Z"
  }
}
```

#### Delete Dataflow
```http
DELETE /api/dataflows/{dataflow_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Dataflow deleted successfully"
}
```

### File API

#### List Files
```http
GET /api/dataflows/{dataflow_id}/files
```

**Query Parameters:**
- `path` (optional): Directory path to list
- `recursive` (optional): Include subdirectories

**Response:**
```json
{
  "success": true,
  "files": [
    {
      "name": "data.csv",
      "path": "raw_data/data.csv",
      "type": "file",
      "size": 1024,
      "modified": "2025-09-11T00:00:00Z",
      "status": "tracked"
    },
    {
      "name": "raw_data",
      "path": "raw_data",
      "type": "directory",
      "status": "tracked"
    }
  ]
}
```

#### Upload File
```http
POST /api/dataflows/{dataflow_id}/files
```

**Request Body:** (multipart/form-data)
- `file`: File to upload
- `path`: Destination path (optional)

**Response:**
```json
{
  "success": true,
  "file": {
    "name": "uploaded_file.csv",
    "path": "raw_data/uploaded_file.csv",
    "size": 2048,
    "status": "untracked"
  }
}
```

#### Download File
```http
GET /api/dataflows/{dataflow_id}/files/{file_path}
```

**Response:** File content with appropriate headers

#### Delete File
```http
DELETE /api/dataflows/{dataflow_id}/files/{file_path}
```

**Response:**
```json
{
  "success": true,
  "message": "File deleted successfully"
}
```

#### Get File Content
```http
GET /api/dataflows/{dataflow_id}/files/{file_path}/content
```

**Response:**
```json
{
  "success": true,
  "content": "file content here",
  "encoding": "utf-8",
  "size": 1024
}
```

### Git API

#### Get Commit History
```http
GET /api/dataflows/{dataflow_id}/commits
```

**Query Parameters:**
- `limit` (optional): Number of commits to return
- `offset` (optional): Offset for pagination

**Response:**
```json
{
  "success": true,
  "commits": [
    {
      "hash": "abc123def456",
      "message": "Added initial data files",
      "author": "John Doe",
      "email": "john@example.com",
      "date": "2025-09-11T00:00:00Z",
      "files_changed": 5,
      "insertions": 100,
      "deletions": 0
    }
  ]
}
```

#### Get Commit Details
```http
GET /api/dataflows/{dataflow_id}/commits/{commit_hash}
```

**Response:**
```json
{
  "success": true,
  "commit": {
    "hash": "abc123def456",
    "message": "Added initial data files",
    "author": "John Doe",
    "email": "john@example.com",
    "date": "2025-09-11T00:00:00Z",
    "files": [
      {
        "path": "raw_data/data.csv",
        "status": "added",
        "changes": "+100 -0"
      }
    ],
    "diff": "diff --git a/raw_data/data.csv..."
  }
}
```

#### Create Commit
```http
POST /api/dataflows/{dataflow_id}/commits
```

**Request Body:**
```json
{
  "message": "Commit message",
  "files": ["raw_data/data.csv", "scripts/analysis.py"]
}
```

**Response:**
```json
{
  "success": true,
  "commit": {
    "hash": "def456ghi789",
    "message": "Commit message",
    "date": "2025-09-11T00:00:00Z"
  }
}
```

#### Revert Commit
```http
POST /api/dataflows/{dataflow_id}/commits/{commit_hash}/revert
```

**Request Body:**
```json
{
  "message": "Revert commit message"
}
```

**Response:**
```json
{
  "success": true,
  "commit": {
    "hash": "ghi789jkl012",
    "message": "Revert commit message",
    "date": "2025-09-11T00:00:00Z"
  }
}
```

### Task API

#### List Tasks
```http
GET /api/tasks
```

**Query Parameters:**
- `project_id` (optional): Filter by project ID
- `status` (optional): Filter by status
- `assignee` (optional): Filter by assignee

**Response:**
```json
{
  "success": true,
  "tasks": [
    {
      "id": 1,
      "title": "Data Collection",
      "description": "Collect water samples",
      "project_id": 1,
      "status": "in_progress",
      "priority": "high",
      "deadline": "2025-09-15T00:00:00Z",
      "assignee_id": 1,
      "created_at": "2025-09-11T00:00:00Z"
    }
  ]
}
```

#### Create Task
```http
POST /api/tasks
```

**Request Body:**
```json
{
  "title": "New Task",
  "description": "Task description",
  "project_id": 1,
  "priority": "medium",
  "deadline": "2025-09-15T00:00:00Z",
  "assignee_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "task": {
    "id": 2,
    "title": "New Task",
    "description": "Task description",
    "project_id": 1,
    "status": "pending",
    "priority": "medium",
    "deadline": "2025-09-15T00:00:00Z",
    "assignee_id": 1,
    "created_at": "2025-09-11T00:00:00Z"
  }
}
```

#### Update Task
```http
PUT /api/tasks/{task_id}
```

**Request Body:**
```json
{
  "status": "completed",
  "priority": "low"
}
```

**Response:**
```json
{
  "success": true,
  "task": {
    "id": 1,
    "status": "completed",
    "priority": "low",
    "updated_at": "2025-09-11T00:00:00Z"
  }
}
```

#### Delete Task
```http
DELETE /api/tasks/{task_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Task deleted successfully"
}
```

### Admin API

#### Load Demo Data
```http
POST /api/admin/load-demo
```

**Response:**
```json
{
  "success": true,
  "message": "Demo data loaded successfully",
  "projects_created": 1,
  "dataflows_created": 1
}
```

#### Reset All Data
```http
POST /api/admin/reset-all
```

**Response:**
```json
{
  "success": true,
  "message": "All data reset successfully"
}
```

#### Reset Projects
```http
POST /api/admin/reset-projects
```

**Response:**
```json
{
  "success": true,
  "message": "Projects reset successfully"
}
```

#### Reset Dataflows
```http
POST /api/admin/reset-dataflows
```

**Response:**
```json
{
  "success": true,
  "message": "Dataflows reset successfully"
}
```

#### Reset Tasks
```http
POST /api/admin/reset-tasks
```

**Response:**
```json
{
  "success": true,
  "message": "Tasks reset successfully"
}
```

## 🔧 Error Handling

### Common Error Codes

#### Validation Errors
```json
{
  "success": false,
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "field": "name",
    "message": "Name is required"
  }
}
```

#### Authentication Errors
```json
{
  "success": false,
  "error": "Authentication required",
  "code": "AUTH_REQUIRED"
}
```

#### Permission Errors
```json
{
  "success": false,
  "error": "Insufficient permissions",
  "code": "PERMISSION_DENIED"
}
```

#### Not Found Errors
```json
{
  "success": false,
  "error": "Resource not found",
  "code": "NOT_FOUND",
  "details": {
    "resource": "project",
    "id": 999
  }
}
```

#### DataLad Errors
```json
{
  "success": false,
  "error": "DataLad operation failed",
  "code": "DATALAD_ERROR",
  "details": {
    "command": "datalad create",
    "stderr": "Error message from DataLad"
  }
}
```

## 📝 Usage Examples

### Python Example
```python
import requests

# Login
session = requests.Session()
login_data = {
    "username": "admin",
    "password": "admin123"
}
response = session.post("http://localhost:5001/auth/login", json=login_data)

# Create a project
project_data = {
    "name": "API Test Project",
    "description": "Testing API integration",
    "research_type": "environmental"
}
response = session.post("http://localhost:5001/api/projects", json=project_data)
project = response.json()["project"]

# Create a dataflow
dataflow_data = {
    "name": "Test Dataflow",
    "project_id": project["id"],
    "research_type": "environmental"
}
response = session.post("http://localhost:5001/api/dataflows", json=dataflow_data)
dataflow = response.json()["dataflow"]

print(f"Created project: {project['name']}")
print(f"Created dataflow: {dataflow['name']}")
```

### JavaScript Example
```javascript
// Login
const loginData = {
    username: 'admin',
    password: 'admin123'
};

fetch('/auth/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(loginData)
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('Login successful');
        
        // Create a project
        const projectData = {
            name: 'API Test Project',
            description: 'Testing API integration',
            research_type: 'environmental'
        };
        
        return fetch('/api/projects', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(projectData)
        });
    }
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('Project created:', data.project.name);
    }
});
```

### cURL Examples
```bash
# Login
curl -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Create project
curl -X POST http://localhost:5001/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Project", "description": "API test", "research_type": "environmental"}'

# List projects
curl -X GET http://localhost:5001/api/projects

# Get project details
curl -X GET http://localhost:5001/api/projects/1
```

## 🔄 Rate Limiting

SciTrace implements rate limiting to prevent abuse:

- **Default Limit**: 100 requests per minute per IP
- **Authentication Endpoints**: 10 requests per minute per IP
- **File Upload Endpoints**: 20 requests per minute per IP
- **Admin Endpoints**: 5 requests per minute per IP

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## 📚 Additional Resources

- **OpenAPI Specification**: [Coming Soon]
- **Postman Collection**: [Coming Soon]
- **SDK Libraries**: [Coming Soon]
- **Webhook Documentation**: [Coming Soon]

---

**Need help?** Check out the [Troubleshooting Guide](../troubleshooting/README.md) for common issues, or explore the [Developer Guide](../developer/README.md) for more technical details.