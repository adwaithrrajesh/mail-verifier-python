#!/usr/bin/env python3
"""
Hetzner-optimized configuration for MailScout
Optimized for 5GB RAM, 2-4 CPU cores, 20TB traffic
High-performance settings for 90-95% success rate
"""

import os

# Hetzner-optimized settings for 5GB RAM
HETZNER_CONFIG = {
    # Threading configuration optimized for 5GB RAM
    'NUM_THREADS': 50,  # Optimized for 5GB RAM
    'NUM_BULK_THREADS': 25,  # Optimized for bulk processing
    
    # SMTP settings optimized for high success rate
    'SMTP_TIMEOUT': 8,  # Increased timeout for better success rate
    'BATCH_SIZE': 100,  # Larger batches for better throughput
    'MAX_RETRIES': 3,  # Retry failed connections
    'RETRY_DELAY': 1.0,  # Base retry delay
    
    # Connection pooling for 5GB RAM
    'CONNECTION_POOL_SIZE': 50,  # More connections for better performance
    'CONNECTION_VALIDATION': True,  # Validate connections before reuse
    
    # Memory optimization for 5GB RAM
    'MAX_CACHE_SIZE': 2000,  # Larger DNS cache
    'MEMORY_LIMIT_MB': 4096,  # Reserve 4GB for the application
    'CIRCUIT_BREAKER_TIMEOUT': 300,  # 5 minutes
    'MAX_FAILURES': 5,  # Max failures before circuit opens
    
    # Network optimizations
    'ENABLE_DNS_CACHE': True,
    'ENABLE_CONNECTION_REUSE': True,
    'ENABLE_CIRCUIT_BREAKER': True,
    'RATE_LIMIT_PER_MINUTE': 500,  # Higher rate limit for 5GB RAM
    
    # Performance monitoring
    'ENABLE_PERFORMANCE_LOGGING': True,
    'LOG_LEVEL': 'INFO',
    'ENABLE_DETAILED_STATS': True
}

def apply_hetzner_config():
    """Apply Hetzner-optimized configuration to environment variables"""
    for key, value in HETZNER_CONFIG.items():
        os.environ[key] = str(value)
    
    print("🚀 Hetzner-optimized configuration applied for 5GB RAM!")
    print(f"📊 Threads: {HETZNER_CONFIG['NUM_THREADS']}")
    print(f"📦 Batch Size: {HETZNER_CONFIG['BATCH_SIZE']}")
    print(f"⏱️  SMTP Timeout: {HETZNER_CONFIG['SMTP_TIMEOUT']}s")
    print(f"🔗 Connection Pool: {HETZNER_CONFIG['CONNECTION_POOL_SIZE']}")
    print(f"💾 Memory Limit: {HETZNER_CONFIG['MEMORY_LIMIT_MB']}MB")
    print(f"🔄 Max Retries: {HETZNER_CONFIG['MAX_RETRIES']}")
    print(f"⚡ Circuit Breaker: {HETZNER_CONFIG['ENABLE_CIRCUIT_BREAKER']}")
    print(f"🎯 Target Success Rate: 90-95%")

if __name__ == "__main__":
    apply_hetzner_config()

