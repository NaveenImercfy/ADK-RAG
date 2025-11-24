# Postman API Guide for Student Educational RAG Agent

This guide provides step-by-step instructions for testing the deployed Student Educational RAG Agent using Postman.

## Prerequisites

1. **Deployed Agent:** The agent must be deployed to Vertex AI Agent Engine
   - Run: `uv run python deployment/deploy.py`
   - Note the `AGENT_ENGINE_ID` from the deployment output

2. **Google Cloud Authentication:**
   - Set up Application Default Credentials (ADC)
   - Run: `gcloud auth application-default login`

3. **Environment Variables:**
   - `GOOGLE_CLOUD_PROJECT`: Your GCP project ID
   - `GOOGLE_CLOUD_LOCATION`: Your GCP location (e.g., `us-central1`)
   - `AGENT_ENGINE_ID`: The agent engine resource name from deployment

## Postman Setup

### Step 1: Create Environment Variables

1. Open Postman
2. Click on "Environments" → "Create Environment"
3. Name it: `Student RAG Agent`
4. Add these variables:

| Variable | Initial Value | Current Value |
|----------|---------------|---------------|
| `project_id` | `your-project-id` | `your-project-id` |
| `location` | `us-central1` | `us-central1` |
| `agent_engine_id` | `projects/123/locations/us-central1/reasoningEngines/456` | `projects/123/locations/us-central1/reasoningEngines/456` |
| `access_token` | (leave empty) | (will be set automatically) |
| `session_id` | (leave empty) | (will be set automatically) |
| `user_id` | `student123` | `student123` |

### Step 2: Get Access Token

**Request:** Get OAuth Token

- **Method:** `POST`
- **URL:** `https://oauth2.googleapis.com/token`
- **Headers:**
  ```
  Content-Type: application/x-www-form-urlencoded
  ```
- **Body (x-www-form-urlencoded):**
  ```
  grant_type: refresh_token
  client_id: YOUR_CLIENT_ID
  client_secret: YOUR_CLIENT_SECRET
  refresh_token: YOUR_REFRESH_TOKEN
  ```
  
**Note:** For easier testing, use the Postman OAuth 2.0 helper or get token via gcloud:
```bash
gcloud auth print-access-token
```

**Alternative: Use Postman OAuth 2.0 Helper**
1. In Postman, go to Authorization tab
2. Select Type: OAuth 2.0
3. Click "Get New Access Token"
4. Configure OAuth settings
5. Copy the token to `access_token` environment variable

### Step 3: Set Access Token Script (Pre-request Script)

Add this to your Postman collection's Pre-request Script:

```javascript
// Get access token using gcloud (requires gcloud CLI)
// Or manually set access_token in environment variables
if (!pm.environment.get("access_token")) {
    console.log("Please set access_token in environment variables");
    console.log("Run: gcloud auth print-access-token");
}
```

## API Endpoints

### 1. Create Session

**Purpose:** Create a new conversation session for a student.

**Request:**
- **Method:** `POST`
- **URL:** 
  ```
  https://{{location}}-aiplatform.googleapis.com/v1/projects/{{project_id}}/locations/{{location}}/sessions
  ```
- **Headers:**
  ```
  Authorization: Bearer {{access_token}}
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "app_name": "{{agent_engine_id}}",
    "user_id": "{{user_id}}"
  }
  ```

**Response:**
```json
{
  "id": "session_abc123",
  "app_name": "projects/123/locations/us-central1/reasoningEngines/456",
  "user_id": "student123",
  "create_time": "2025-01-15T10:30:00Z"
}
```

**Postman Test Script:**
```javascript
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set("session_id", jsonData.id);
    console.log("Session created:", jsonData.id);
}
```

---

### 2. Query Agent (Streaming)

**Purpose:** Send a student question to the agent and get streaming response.

**Request:**
- **Method:** `POST`
- **URL:**
  ```
  https://{{location}}-aiplatform.googleapis.com/v1/projects/{{project_id}}/locations/{{location}}/reasoningEngines/{{agent_engine_id}}:streamQuery
  ```
- **Headers:**
  ```
  Authorization: Bearer {{access_token}}
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "user_id": "{{user_id}}",
    "session_id": "{{session_id}}",
    "message": "I'm studying CBSE Grade 10 Science. What is photosynthesis?"
  }
  ```

**Response (Streaming):**
The response is a stream of events. Each event contains:
```json
{
  "author": "agent",
  "content": {
    "parts": [
      {
        "text": "Photosynthesis is the process..."
      }
    ]
  }
}
```

**Postman Test Script:**
```javascript
if (pm.response.code === 200) {
    console.log("Query sent successfully");
    // Note: Streaming responses may need special handling
}
```

---

### 3. Query Agent (Non-Streaming)

**Purpose:** Send a student question and get complete response.

**Request:**
- **Method:** `POST`
- **URL:**
  ```
  https://{{location}}-aiplatform.googleapis.com/v1/projects/{{project_id}}/locations/{{location}}/reasoningEngines/{{agent_engine_id}}:query
  ```
- **Headers:**
  ```
  Authorization: Bearer {{access_token}}
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "user_id": "{{user_id}}",
    "session_id": "{{session_id}}",
    "message": "I'm studying CBSE Grade 10 Science. What is photosynthesis?"
  }
  ```

**Response:**
```json
{
  "response": {
    "content": {
      "parts": [
        {
          "text": "Photosynthesis is the process by which green plants make their own food using sunlight, water, and carbon dioxide..."
        }
      ]
    },
    "citations": [
      {
        "title": "CBSE Grade 10 Science Textbook - Chapter 6: Life Processes"
      }
    ]
  }
}
```

---

## Example Requests

### Example 1: Student Question with Context

**Request Body:**
```json
{
  "user_id": "student123",
  "session_id": "{{session_id}}",
  "message": "I'm studying CBSE Grade 10 Science. What is photosynthesis?"
}
```

**Expected Response:**
- Agent identifies: CBSE, Grade 10, Science
- Retrieves content from CBSE Grade 10 Science textbook
- Provides answer with citations

---

### Example 2: Student Question Without Context

**Request Body:**
```json
{
  "user_id": "student123",
  "session_id": "{{session_id}}",
  "message": "What is a quadratic equation?"
}
```

**Expected Response:**
- Agent asks for board, grade, and subject
- Waits for student to provide context

---

### Example 3: Multiple Terms (Tamil Nadu State Board)

**Request Body:**
```json
{
  "user_id": "student123",
  "session_id": "{{session_id}}",
  "message": "I'm studying Tamil Nadu State Board Grade 4 Science. What is the water cycle?"
}
```

**Expected Response:**
- Agent searches across Term1, Term2, Term3
- Provides answer from relevant term
- Citations show which term was used

---

### Example 4: Follow-up Question (Context Remembered)

**Request Body:**
```json
{
  "user_id": "student123",
  "session_id": "{{session_id}}",
  "message": "What about cellular respiration?"
}
```

**Expected Response:**
- Agent uses previously set context (CBSE Grade 10 Science)
- Provides answer without asking for context again

---

## Postman Collection Structure

Create a collection with these folders:

```
Student RAG Agent API
├── Authentication
│   └── Get Access Token
├── Session Management
│   └── Create Session
└── Agent Queries
    ├── Query with Context (CBSE Grade 10 Science)
    ├── Query without Context
    ├── Query Tamil Nadu State Board
    └── Follow-up Question
```

## Complete Postman Collection JSON

Save this as `Student_RAG_Agent.postman_collection.json`:

```json
{
  "info": {
    "name": "Student RAG Agent API",
    "description": "API collection for Student Educational RAG Agent",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "1. Create Session",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{access_token}}",
            "type": "text"
          },
          {
            "key": "Content-Type",
            "value": "application/json",
            "type": "text"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"app_name\": \"{{agent_engine_id}}\",\n  \"user_id\": \"{{user_id}}\"\n}"
        },
        "url": {
          "raw": "https://{{location}}-aiplatform.googleapis.com/v1/projects/{{project_id}}/locations/{{location}}/sessions",
          "host": ["{{location}}-aiplatform.googleapis.com"],
          "path": ["v1", "projects", "{{project_id}}", "locations", "{{location}}", "sessions"]
        }
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "if (pm.response.code === 200) {",
              "    var jsonData = pm.response.json();",
              "    pm.environment.set(\"session_id\", jsonData.id);",
              "    console.log(\"Session created:\", jsonData.id);",
              "}"
            ]
          }
        }
      ]
    },
    {
      "name": "2. Query Agent - With Context",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{access_token}}",
            "type": "text"
          },
          {
            "key": "Content-Type",
            "value": "application/json",
            "type": "text"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"user_id\": \"{{user_id}}\",\n  \"session_id\": \"{{session_id}}\",\n  \"message\": \"I'm studying CBSE Grade 10 Science. What is photosynthesis?\"\n}"
        },
        "url": {
          "raw": "https://{{location}}-aiplatform.googleapis.com/v1/projects/{{project_id}}/locations/{{location}}/reasoningEngines/{{agent_engine_id}}:query",
          "host": ["{{location}}-aiplatform.googleapis.com"],
          "path": ["v1", "projects", "{{project_id}}", "locations", "{{location}}", "reasoningEngines", "{{agent_engine_id}}:query"]
        }
      }
    },
    {
      "name": "3. Query Agent - Without Context",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{access_token}}",
            "type": "text"
          },
          {
            "key": "Content-Type",
            "value": "application/json",
            "type": "text"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"user_id\": \"{{user_id}}\",\n  \"session_id\": \"{{session_id}}\",\n  \"message\": \"What is a quadratic equation?\"\n}"
        },
        "url": {
          "raw": "https://{{location}}-aiplatform.googleapis.com/v1/projects/{{project_id}}/locations/{{location}}/reasoningEngines/{{agent_engine_id}}:query",
          "host": ["{{location}}-aiplatform.googleapis.com"],
          "path": ["v1", "projects", "{{project_id}}", "locations", "{{location}}", "reasoningEngines", "{{agent_engine_id}}:query"]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "project_id",
      "value": "your-project-id"
    },
    {
      "key": "location",
      "value": "us-central1"
    },
    {
      "key": "agent_engine_id",
      "value": "projects/123/locations/us-central1/reasoningEngines/456"
    }
  ]
}
```

## Quick Start Guide

1. **Import Collection:**
   - Open Postman
   - Click "Import"
   - Paste the JSON above or import from file

2. **Set Environment Variables:**
   - Create environment as described in Step 1
   - Set `project_id`, `location`, `agent_engine_id`

3. **Get Access Token:**
   ```bash
   gcloud auth print-access-token
   ```
   - Copy the token
   - Set it in Postman environment variable `access_token`

4. **Create Session:**
   - Run "1. Create Session" request
   - Session ID will be automatically saved

5. **Query Agent:**
   - Run "2. Query Agent - With Context"
   - Modify the message in the request body as needed

## Troubleshooting

### Error: 401 Unauthorized
- **Solution:** Check that `access_token` is valid and not expired
- Run: `gcloud auth print-access-token` to get a new token

### Error: 404 Not Found
- **Solution:** Verify `agent_engine_id` is correct
- Check that the agent is deployed: `uv run python deployment/deploy.py`

### Error: 400 Bad Request
- **Solution:** Check that `session_id` is set correctly
- Create a new session if needed

### Streaming Response Not Working
- **Note:** Postman may not handle streaming responses well
- Use the non-streaming `:query` endpoint instead of `:streamQuery`
- Or use the Python SDK for streaming: `deployment/run.py`

## Additional Resources

- [Vertex AI Agent Engine API Documentation](https://cloud.google.com/vertex-ai/docs/agent-engine/overview)
- [Google Cloud Authentication](https://cloud.google.com/docs/authentication)
- [Postman OAuth 2.0 Guide](https://learning.postman.com/docs/sending-requests/authorization/oauth-20/)

