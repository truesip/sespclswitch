# SESPCLSwitch API Documentation

## Overview
SESPCLSwitch provides a comprehensive API for integrating voice call capabilities into your applications using SIP and text-to-speech technologies.

## Base URL
```
http://167.172.135.7:5000
```

## Authentication
No authentication is required for accessing these endpoints.

## Endpoints

### 1. Health Check
**GET /health**  

Returns the health status of the SESPCLSwitch service.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-08T02:51:40.423301",
  "version": "1.0.0",
  "sip_server": "sip.truesip.net",
  "tts_service": "espeak"
}
```

### 2. API Information
**GET /api/info**

Provides detailed information about the SESPCLSwitch API and configuration.

**Response:**
```json
{
  "name": "SESPCLSwitch",
  "version": "1.0.0",
  "description": "Production-ready SESPCLSwitch using SIP and Text-to-Speech",
  "endpoints": {
    "GET /health": "Health check endpoint",
    "POST /voice/call": "Make a voice call",
    "GET /voice/status/{call_id}": "Get call status",
    "GET /api/info": "API information"
  },
  "configuration": {
    "sip_server": "sip.truesip.net",
    "sip_port": "5060",
    "tts_service": "espeak"
  }
}
```

### 3. Make a Voice Call
**POST /voice/call**

Initiates a voice call using SIP and text-to-speech conversion.

**Request Body:**
```json
{
  "ToNumber": "+1234567890",
  "FromNumber": "12156",
  "Text": "Hello from SESPCLSwitch!"
}
```

**Response (202 Accepted):**
```json
{
  "success": true,
  "call_id": "18885f34-d743-4ca1-96a8-55d340bd3937",
  "task_id": "cd06dcec-a255-4dcb-bd01-997ca1ef9300",
  "status": "queued",
  "to_number": "+1234567890",
  "from_number": "12156",
  "timestamp": "2025-07-08T02:52:41.080771",
  "estimated_processing_time": "30-60 seconds"
}
```

### 4. Check Call Status
**GET /voice/status/{call_id}**

Retrieves the status of a specific voice call.

**Response:**
```json
{
  "id": "18885f34-d743-4ca1-96a8-55d340bd3937",
  "to_number": "+1234567890",
  "from_number": "12156",
  "text": "Hello from SESPCLSwitch!",
  "status": "pending",
  "created_at": "2025-07-08T02:52:41.035361",
  "started_at": null,
  "completed_at": null,
  "duration": null,
  "task_status": "FAILURE",
  "error_message": null
}
```

### 5. Bulk Voice Calls
**POST /voice/bulk**

Initiates multiple voice calls with a single request. Allows for increased throughput by processing calls in bulk.

**Request Body:**
```json
{
  "calls": [
    {
      "ToNumber": "+1234567890",
      "FromNumber": "12156",
      "Text": "Hello from SESPCLSwitch!"
    },
    {
      "ToNumber": "+0987654321",
      "FromNumber": "12156",
      "Text": "Hello from SESPCLSwitch again!"
    }
  ]
}
```

**Response (202 Accepted):**
```json
{
  "success": true,
  "queued_calls": 2,
  "call_ids": ["18885f34-d743-4ca1-96a8-55d340bd3937", "18885f34-d743-4ca1-96a8-55d340bd3938"],
  "timestamp": "2025-07-08T02:55:21.080771"
}
```

### 6. System Metrics
**GET /api/metrics**

Provides real-time performance metrics for the SESCPCLSwitch system.

**Response:**
```json
{
  "timestamp": "2025-07-08T02:52:55.802240",
  "calls": {
    "total": 1,
    "pending": 1,
    "processing": 0,
    "completed": 0,
    "failed": 0,
    "success_rate": 0.0
  },
  "system": {
    "status": "operational",
    "version": "2.0.0",
    "celery_workers": "Active"
  }
}
```

## Error Responses

### 400 Bad Request:
Occurs when essential fields are missing or contain invalid data.

```json
{
  "error": "Missing required fields",
  "missing": ["ToNumber"],
  "required": ["ToNumber", "FromNumber", "Text"]
}
```

### 500 Internal Server Error:
Triggered by server-side issues like failed connections or processing errors.

```json
{
  "error": "Internal server error",
  "details": "Error description"
}
```

## Environment Variables

- `DATABASE_URL`: Connection string for PostgreSQL.
- `CELERY_BROKER_URL`: Address of the Redis broker for Celery.
- `result_backend`: Redis backend URL for Celery.
- `REDIS_URL`: Redis caching URL.
- `SIP_TRUNK_IP`: SIP trunk server IP.
- `SIP_TRUNK_PORT`: SIP trunk port.
- `SIP_USERNAME`: SIP account username.
- `SIP_PASSWORD`: SIP account password.
- `TTS_SERVICE`: Text-to-Speech service (espeak, google, azure, aws).
- Additional keys for cloud TTS: `GOOGLE_TTS_API_KEY`, `AZURE_TTS_KEY`, `AWS_ACCESS_KEY`.

## Contact
For further support, reach the development team at support@sespclswitch.com.
