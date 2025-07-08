# SESPCLSwitch - Installation Guide and API Documentation

## Introduction
Welcome to SESPCLSwitch. This guide will walk you through setting up the server, running it locally, and deploying it on a platform like DigitalOcean using Docker.

---

## Prerequisites
- **Python:** Make sure Python is installed (version 3.7 or higher).
- **Docker:** Have Docker installed on your machine.
- **Git:** Ensure Git is installed for version control.

---

## Installation

### 1. Clone the Repository
```
git clone https://github.com/truesip/sespclswitch.git
cd sespclswitch
```

### 2. Set up a Virtual Environment (Optional but recommended)
```
python -m venv venv
./venv/Scripts/Activate.ps1  # Windows
```

### 3. Install Dependencies
```
pip install -r requirements.txt
```

---

## Running the Server Locally

### 1. Environment Variables
Create a `.env` file at the root of the project and define any necessary environment variables. For example:
```env
FLASK_APP=app.py
SECRET_KEY=your_secret_key_here
```

### 2. Run the Server
```
flask run
```
Your server will be running on `http://localhost:5000`.

---

## Docker Setup

### 1. Build Docker Image
```
docker build -t sespclswitch .
```

### 2. Run Docker Container
```
docker run -p 5000:5000 sespclswitch
```

---

## Deployment to DigitalOcean

### 1. Create a Docker Droplet
- Log in to DigitalOcean.
- Create a new Docker Droplet and follow the guided steps.

### 2. Transfer Docker Image to Droplet
- You may use Docker Hub to share images between your local machine and the Droplet.
- Push your Docker image to Docker Hub:
  ```
  docker tag sespclswitch yourdockerhubusername/sespclswitch
  docker push yourdockerhubusername/sespclswitch
  ```
- On your Droplet, pull the image:
  ```
  docker pull yourdockerhubusername/sespclswitch
  docker run -d -p 80:5000 yourdockerhubusername/sespclswitch
  ```

---

## API Documentation

### Base URL
```
http://localhost:5000
```

### Authentication
Currently, no authentication is required for API endpoints.

### Available Endpoints

#### 1. Health Check
**GET /health**

Returns the health status of the SESPCLSwitch service.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-08T01:35:22.123456",
  "version": "1.0.0",
  "sip_server": "sip.truesip.net",
  "tts_service": "espeak"
}
```

#### 2. Make Voice Call
**POST /voice/call**

Initiates a voice call with text-to-speech conversion.

**Request Body:**
```json
{
  "ToNumber": "+1234567890",
  "FromNumber": "12156",
  "Text": "Hello, this is a test call from SESPCLSwitch",
  "AudioUrl": "https://example.com/audio.mp3" // Optional
}
```

**Response (202 Accepted):**
```json
{
  "success": true,
  "call_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": "12345678-1234-5678-9012-123456789012",
  "status": "queued",
  "to_number": "+1234567890",
  "from_number": "12156",
  "timestamp": "2025-01-08T01:35:22.123456",
  "estimated_processing_time": "30-60 seconds"
}
```

#### 3. Get Call Status
**GET /voice/status/{call_id}**

Returns the status of a specific voice call.

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "to_number": "+1234567890",
  "from_number": "12156",
  "text": "Hello, this is a test call",
  "status": "completed",
  "created_at": "2025-01-08T01:35:22.123456",
  "started_at": "2025-01-08T01:35:30.123456",
  "completed_at": "2025-01-08T01:36:15.123456",
  "duration": 45,
  "task_status": "SUCCESS"
}
```

**Call Status Values:**
- `pending`: Call is queued for processing
- `processing`: Call is being processed (TTS conversion, SIP call)
- `completed`: Call was successfully completed
- `failed`: Call failed due to an error

#### 4. API Information
**GET /api/info**

Returns detailed information about the SESPCLSwitch API.

**Response:**
```json
{
  "name": "SESPCLSwitch",
  "version": "1.0.0",
  "description": "Production-ready SESPCLSwitch using SIP and Text-to-Speech",
  "endpoints": {
    "GET /health": "Health check endpoint",
    "POST /voice/call": "Make a voice call",
    "GET /voice/status/<call_id>": "Get call status",
    "GET /api/info": "API information"
  },
  "configuration": {
    "sip_server": "sip.truesip.net",
    "sip_port": "5060",
    "tts_service": "espeak"
  }
}
```

#### 5. System Metrics
**GET /api/metrics**

Returns system performance metrics and call statistics.

**Response:**
```json
{
  "timestamp": "2025-01-08T01:35:22.123456",
  "calls": {
    "total": 1250,
    "pending": 5,
    "processing": 10,
    "completed": 1200,
    "failed": 35,
    "success_rate": 96.0
  },
  "system": {
    "status": "operational",
    "version": "2.0.0",
    "celery_workers": "Active"
  }
}
```

#### 6. Bulk Voice Calls
**POST /voice/bulk**

Initiate multiple voice calls in a single request (up to 1000 calls).

**Request Body:**
```json
{
  "calls": [
    {
      "ToNumber": "+1234567890",
      "FromNumber": "12156",
      "Text": "First call message"
    },
    {
      "ToNumber": "+0987654321",
      "FromNumber": "12156",
      "Text": "Second call message"
    }
  ]
}
```

**Response (202 Accepted):**
```json
{
  "success": true,
  "queued_calls": 2,
  "call_ids": ["call-id-1", "call-id-2"],
  "total_calls": 2,
  "timestamp": "2025-01-08T01:35:22.123456"
}
```

### Error Responses

All error responses follow this format:

**400 Bad Request:**
```json
{
  "error": "Missing required fields",
  "missing": ["ToNumber"],
  "required": ["ToNumber", "FromNumber", "Text"]
}
```

**404 Not Found:**
```json
{
  "error": "Call not found"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error",
  "details": "Error description"
}
```

### Environment Variables

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/voicecall_db

# Redis Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/1

# SIP Configuration
SIP_TRUNK_IP=sip.truesip.net
SIP_TRUNK_PORT=5060
SIP_USERNAME=your_sip_username
SIP_PASSWORD=your_sip_password

# TTS Configuration
TTS_SERVICE=espeak  # Options: espeak, google, azure, aws
GOOGLE_TTS_API_KEY=your_google_api_key
AZURE_TTS_KEY=your_azure_key
AZURE_TTS_REGION=your_azure_region
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key

# Application Settings
DEBUG=false
MAX_WORKERS=20
MAX_CONCURRENT_CALLS=1000
```

---

## Troubleshooting
- Ensure all environment variables are set correctly.
- Check Docker and application logs for error messages.

---

This concludes the setup and usage guide for the SESPCLSwitch server. For further support, please contact the development team.
