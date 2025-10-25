# MailScout Email Verification Service

High-performance email verification service using SMTP validation.

## Features

- 🚀 **Fast**: ~1000 emails in 5-6 minutes
- 🎯 **Accurate**: Smart MX-based port selection
- 🔧 **Optimized**: 100 concurrent threads, 2s timeouts
- 🐳 **Docker-ready**: One command to start

## Quick Start

```bash
# Start the service
docker compose up -d

# Verify emails
curl -X POST http://localhost:9080/verify-bulk \
  -H "Content-Type: application/json" \
  -d '{"emails": ["test@example.com"]}'

# Check stats
curl http://localhost:9080/stats
```

## API Endpoints

- `GET /` - Service status
- `POST /verify` - Verify single email
- `POST /verify-bulk` - Verify up to 1000 emails
- `GET /stats` - Performance statistics
- `POST /find` - Find emails for domain + names
- `GET /diagnostics/smtp` - SMTP connectivity test

## Project Structure

```
.
├── Dockerfile              # Container build config
├── docker-compose.yml      # Service orchestration
├── requirements.txt        # Python dependencies
├── mailscout/             # Core verification engine
│   ├── __main__.py        # Flask API
│   └── scout.py           # SMTP verification logic
├── tests/                 # Unit tests
└── docs/                  # Documentation
    ├── README.md          # Full documentation
    ├── DOCKER.md          # Docker guide
    ├── OPTIMIZATION_SUMMARY.md  # Performance details
    └── HETZNER_DEPLOYMENT.md    # Cloud deployment
```

## Configuration

Environment variables in `docker-compose.yml`:

```yaml
SMTP_TIMEOUT: 2          # Connection timeout (seconds)
NUM_THREADS: 100         # Concurrent workers
BATCH_SIZE: 100          # Emails per batch
MAX_RETRIES: 1           # Retry attempts
```

## Performance

- **Throughput**: 2.8+ emails/second
- **Latency**: 0.2-1.5s per email
- **Success Rate**: 75%+ (depends on server reputation)

## Documentation

See the `docs/` directory for detailed documentation:
- [Full README](docs/README.md) - Complete feature documentation
- [Optimization Summary](docs/OPTIMIZATION_SUMMARY.md) - Performance improvements
- [Docker Guide](docs/DOCKER.md) - Docker deployment details

## License

MIT License - See [LICENSE](LICENSE) file
