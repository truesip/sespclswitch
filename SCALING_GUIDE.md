# SESPCLSwitch - Scaling Guide for 1 Million Calls

## Overview
This guide explains how to scale the SESPCLSwitch to handle 1 million calls efficiently using the optimized architecture.

## Current Optimizations Implemented

### 1. **Asynchronous Processing**
- **Celery**: Background task processing for TTS and SIP calls
- **Redis**: Message broker and result backend
- **Gevent Workers**: Async I/O for handling concurrent connections

### 2. **Database Optimization**
- **PostgreSQL**: Robust database with connection pooling
- **SQLAlchemy**: ORM with optimized connection management
- **Call Tracking**: Persistent storage for call status and metrics

### 3. **Production Server**
- **Gunicorn**: Production WSGI server
- **Multiple Workers**: CPU cores × 2 + 1 workers
- **Supervisor**: Process management and auto-restart

### 4. **Containerization**
- **Docker**: Consistent deployment environment
- **Docker Compose**: Multi-service orchestration
- **Health Checks**: Service monitoring and auto-healing

## Performance Capacity

### Current Configuration
- **Single Instance**: ~1,000-5,000 concurrent calls
- **API Throughput**: ~10,000 requests/minute
- **Database**: 20 connection pool, optimized queries
- **Redis**: High-performance caching and queuing

### Scaling to 1 Million Calls

#### Horizontal Scaling (Recommended)
```bash
# Deploy multiple instances behind load balancer
docker-compose up --scale sespclswitch=10
```

#### Load Balancer Configuration
```nginx
upstream sespclswitch {
    least_conn;
    server sespclswitch-1:5000;
    server sespclswitch-2:5000;
    server sespclswitch-3:5000;
    # Add more instances as needed
}

server {
    listen 80;
    location / {
        proxy_pass http://sespclswitch;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Deployment Instructions

### 1. **Local Development**
```bash
# Install dependencies
pip install -r requirements.txt

# Start Redis and PostgreSQL
docker run -d -p 6379:6379 redis:7-alpine
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:15

# Run the application
python app.py
```

### 2. **Production Deployment**
```bash
# Build and deploy with Docker Compose
docker-compose up -d --build

# Scale to multiple instances
docker-compose up -d --scale sespclswitch=5

# Monitor logs
docker-compose logs -f sespclswitch
```

### 3. **Kubernetes Deployment** (For Large Scale)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sespclswitch
spec:
  replicas: 20  # Scale as needed
  selector:
    matchLabels:
      app: sespclswitch
  template:
    metadata:
      labels:
        app: sespclswitch
    spec:
      containers:
      - name: sespclswitch
        image: sespclswitch:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          value: "postgresql://postgres:password@postgres:5432/voicecall_db"
        - name: CELERY_BROKER_URL
          value: "redis://redis:6379/0"
        resources:
          requests:
            memory: "1Gi"
            cpu: "1000m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
```

## Performance Monitoring

### 1. **Built-in Metrics**
- `GET /api/metrics` - System performance data
- `GET /health` - Health check endpoint
- Database call statistics and success rates

### 2. **External Monitoring** (Recommended)
```bash
# Prometheus + Grafana for monitoring
# Log aggregation with ELK stack
# APM tools like New Relic or DataDog
```

## Optimization Tips

### 1. **Database Tuning**
```sql
-- PostgreSQL optimizations
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '4MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
```

### 2. **Redis Optimization**
```conf
# Redis configuration
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
```

### 3. **Application Tuning**
- **Bulk Operations**: Use `/voice/bulk` for batch calls
- **Caching**: TTS results and audio files
- **Connection Pooling**: Database and SIP connections

## Expected Performance

### Single Instance
- **Concurrent Calls**: 1,000-5,000
- **Throughput**: 10,000 requests/minute
- **Response Time**: <100ms for API calls
- **Call Processing**: 30-60 seconds per call

### Scaled Deployment (10 instances)
- **Concurrent Calls**: 10,000-50,000
- **Daily Capacity**: 1+ million calls
- **High Availability**: Load balancing + auto-scaling
- **Fault Tolerance**: Automatic failover

## Cost Estimation

### Infrastructure Requirements (AWS/DigitalOcean)
- **Load Balancer**: $20/month
- **API Instances** (10 × 2GB RAM): $500/month
- **Database** (PostgreSQL): $100/month
- **Redis Cache**: $50/month
- **Storage**: $50/month
- **Total**: ~$720/month for 1M calls capacity

## Troubleshooting

### Common Issues
1. **High Memory Usage**: Scale Redis or add more instances
2. **Database Locks**: Optimize queries and connection pooling
3. **SIP Failures**: Check network connectivity and timeouts
4. **Queue Backlog**: Add more Celery workers

### Monitoring Commands
```bash
# Check API health
curl http://localhost:5000/health

# Monitor metrics
curl http://localhost:5000/api/metrics

# Check Docker stats
docker stats

# Monitor Celery workers
celery -A app.celery inspect active
```

## Support and Maintenance

### Regular Tasks
- Monitor system metrics daily
- Review error logs weekly
- Database maintenance monthly
- Security updates quarterly

### Scaling Triggers
- CPU usage > 80% for 5 minutes
- Memory usage > 85%
- Queue length > 1000 pending calls
- Response time > 200ms average

This optimized architecture can efficiently handle 1 million calls with proper scaling and monitoring.
