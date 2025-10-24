#!/usr/bin/env python3
"""
Test script to verify SMTP connectivity issues
"""
import socket
import time

def test_port(host, port, timeout=5):
    """Test if a port is reachable"""
    try:
        start = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        elapsed = time.time() - start
        sock.close()
        
        if result == 0:
            return f"✅ {host}:{port} - OPEN ({elapsed:.2f}s)"
        else:
            return f"❌ {host}:{port} - BLOCKED/CLOSED (errno: {result})"
    except socket.timeout:
        return f"⏱️  {host}:{port} - TIMEOUT ({timeout}s)"
    except Exception as e:
        return f"❌ {host}:{port} - ERROR: {e}"

# Test SMTP servers
hosts = [
    ("gmail-smtp-in.l.google.com", 25),
    ("gmail-smtp-in.l.google.com", 587),
    ("gmail-smtp-in.l.google.com", 465),
    ("hotmail-com.olc.protection.outlook.com", 25),
    ("hotmail-com.olc.protection.outlook.com", 587),
]

print("=" * 60)
print("SMTP PORT CONNECTIVITY TEST")
print("=" * 60)

for host, port in hosts:
    print(test_port(host, port, timeout=3))

print("\n" + "=" * 60)
print("SOLUTION:")
print("=" * 60)
print("SMTP ports are BLOCKED by Hetzner by default.")
print("Contact Hetzner support to unblock ports 25, 465, 587")
print("See: HETZNER_DEPLOYMENT.md for instructions")
