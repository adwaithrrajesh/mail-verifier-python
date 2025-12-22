#!/usr/bin/env python3
"""
Test script for enhanced catch-all detection
Tests the new multi-email catch-all detection functionality
"""

import sys
sys.path.insert(0, '/Users/adwaithrrajesh/Freelance/mailsfinder-backend/verification-service/mailscout')

from scout import Scout

# Initialize Scout with catch-all detection enabled (default)
scout = Scout(
    check_catchall=True,
    catchall_test_emails=3,
    smtp_timeout=3
)

print("=" * 60)
print("TESTING ENHANCED CATCH-ALL DETECTION")
print("=" * 60)

# Test 1: Known non-catch-all domain (Gmail)
print("\n1. Testing known NON-catch-all domain (gmail.com)...")
test_email_1 = "test.user.does.not.exist.12345@gmail.com"
result_1 = scout.check_smtp(test_email_1)
print(f"Email: {result_1['email']}")
print(f"Status: {result_1['status']}")
print(f"Catch-all: {result_1['catch_all']}")
print(f"Catch-all Confidence: {result_1['catch_all_confidence']}")
print(f"Message: {result_1['message']}")

# Test 2: User's domain (if they want to test manually)
print("\n2. Testing a real email address...")
test_email_2 = "adwaith@adwaithrrajesh.in"  # Replace with actual test email
result_2 = scout.check_smtp(test_email_2)
print(f"Email: {result_2['email']}")
print(f"Status: {result_2['status']}")
print(f"Catch-all: {result_2['catch_all']}")
print(f"Catch-all Confidence: {result_2['catch_all_confidence']}")
print(f"Message: {result_2['message']}")

# Test 3: Check if caching works
print("\n3. Testing cache (second verification of same domain)...")
import time
start = time.time()
test_email_3 = "another.test@adwaithrrajesh.in"
result_3 = scout.check_smtp(test_email_3)
elapsed = time.time() - start
print(f"Email: {result_3['email']}")
print(f"Status: {result_3['status']}")
print(f"Catch-all: {result_3['catch_all']}")
print(f"Catch-all Confidence: {result_3['catch_all_confidence']}")
print(f"Time taken: {elapsed:.2f}s (should be faster due to caching)")

print("\n" + "=" * 60)
print("Tests completed!")
print("=" * 60)
print(f"\nCatch-all cache entries: {len(scout.catchall_cache)}")
print(f"MX cache entries: {len(scout.mx_cache)}")
