# Installation Guide and Documentation

## Introduction
Welcome to the Voice Call API. This guide will walk you through setting up the server, running it locally, and deploying it on a platform like DigitalOcean using Docker.

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
docker build -t voice-call-api .
```

### 2. Run Docker Container
```
docker run -p 8000:8000 voice-call-api
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
  docker tag voice-call-api yourdockerhubusername/voice-call-api
  docker push yourdockerhubusername/voice-call-api
  ```
- On your Droplet, pull the image:
  ```
  docker pull yourdockerhubusername/voice-call-api
  docker run -d -p 80:8000 yourdockerhubusername/voice-call-api
  ```

---

## API Endpoints
- **GET /api/status**: Returns the status of the application.
- **POST /api/call**: Initiates a call.

---

## Troubleshooting
- Ensure all environment variables are set correctly.
- Check Docker and application logs for error messages.

---

This concludes the setup and usage guide for the Voice Call API server. For further support, please contact the development team.
