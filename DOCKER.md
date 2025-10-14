# 🐳 Docker Setup for Email Finder

This guide explains how to run the Email Finder application using Docker and Docker Compose.

## 🚀 Quick Start

### Prerequisites
- Docker installed and running
- Docker Compose installed

### Basic Usage

1. **Start the application:**
   ```bash
   docker-compose up --build
   ```

2. **Or use the startup script:**
   ```bash
   ./docker-start.sh
   ```

3. **Access the API:**
   - API Info: http://localhost:8008/
   - Bulk Verification: http://localhost:8008/verify-bulk
   - Performance Stats: http://localhost:8008/stats

## 📋 Available Commands

### Development
```bash
# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and start
docker-compose up --build
```

### Production
```bash
# Start with production configuration
docker-compose -f docker-compose.prod.yml up -d

# Start with nginx reverse proxy
docker-compose --profile production up -d

# Start with monitoring
docker-compose --profile monitoring up -d
```

## 🔧 Configuration

### Environment Variables
You can customize the application by setting environment variables:

```bash
# In docker-compose.yml or .env file
SMTP_TIMEOUT=10          # SMTP connection timeout
NUM_THREADS=20           # Number of concurrent threads
BATCH_SIZE=50            # Emails per batch
```

### Resource Limits
The application includes resource limits to prevent system overload:

- **Development**: 1 CPU, 512MB RAM
- **Production**: 2 CPU, 1GB RAM

## 📊 Performance Optimization

### For High-Volume Processing
```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up -d

# Or manually set higher limits
docker-compose up -d --scale email-finder=2
```

### Monitoring
```bash
# Start with Prometheus monitoring
docker-compose --profile monitoring up -d

# Access Prometheus at http://localhost:9090
```

## 🌐 Network Configuration

The application runs on:
- **Port 8008**: Main API endpoint
- **Port 80/443**: Nginx reverse proxy (with --profile production)

### External Access
To access from other machines:
```bash
# Allow external connections
docker-compose up -d -p 0.0.0.0:8008:8008
```

## 🔍 Troubleshooting

### Check Service Status
```bash
# View running containers
docker-compose ps

# Check logs
docker-compose logs email-finder

# Check health
curl http://localhost:8008/
```

### Common Issues

1. **Port already in use:**
   ```bash
   # Change port in docker-compose.yml
   ports:
     - "8009:8008"  # Use port 8009 instead
   ```

2. **SMTP blocked (local development):**
   - Use your hosted server for SMTP testing
   - The container will work fine on servers with open SMTP access

3. **Memory issues:**
   ```bash
   # Increase memory limits
   deploy:
     resources:
       limits:
         memory: 2G
   ```

## 📈 Scaling

### Horizontal Scaling
```bash
# Run multiple instances
docker-compose up -d --scale email-finder=3
```

### Load Balancing
Use the nginx configuration with multiple instances:
```bash
docker-compose --profile production up -d --scale email-finder=3
```

## 🔒 Security

### Production Security
1. Use HTTPS with SSL certificates
2. Set up proper firewall rules
3. Use secrets management for sensitive data
4. Regular security updates

### SSL Configuration
```bash
# Place SSL certificates in ./ssl/
# Update nginx.conf for HTTPS
docker-compose --profile production up -d
```

## 📝 API Usage Examples

### Single Email Verification
```bash
curl -X POST http://localhost:8008/verify \
  -H "Content-Type: application/json" \
  -d '{"email": "test@gmail.com"}'
```

### Bulk Verification (1000 emails)
```bash
curl -X POST http://localhost:8008/verify-bulk \
  -H "Content-Type: application/json" \
  -d '{"emails": ["email1@domain.com", "email2@domain.com", ...]}'
```

### Performance Stats
```bash
curl http://localhost:8008/stats
```

## 🛠️ Development

### Local Development with Docker
```bash
# Mount local code for development
docker-compose -f docker-compose.dev.yml up

# Or use bind mounts
docker run -v $(pwd):/app -p 8008:8008 mailscout-email-finder
```

### Building Custom Image
```bash
# Build with custom tag
docker build -t my-email-finder .

# Run custom image
docker run -p 8008:8008 my-email-finder
```
