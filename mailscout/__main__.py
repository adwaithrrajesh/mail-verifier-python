# from flask import Flask

# app = Flask(__name__)

# @app.route("/")
# def home():
#     return "Hello, Flask is working!"

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8080)



from flask import Flask, request, jsonify
from .scout import Scout  # Import Scout class
import time
from functools import wraps
import re
from typing import Dict, Any, List
import os
import socket
import threading

app = Flask(__name__)
scout = Scout(
    smtp_timeout=int(os.getenv("SMTP_TIMEOUT", "10")),
    num_threads=int(os.getenv("NUM_THREADS", "20")),
    batch_size=int(os.getenv("BATCH_SIZE", "50"))
)  # Initialize Scout with optimized settings

# Rate limiting configuration
RATE_LIMIT = 100  # requests per minute
rate_limit_data: Dict[str, list] = {}

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = request.remote_addr
        current_time = time.time()
        
        # Clean old timestamps
        if ip in rate_limit_data:
            rate_limit_data[ip] = [t for t in rate_limit_data[ip] if current_time - t < 60]
        else:
            rate_limit_data[ip] = []
        
        # Check rate limit
        if len(rate_limit_data[ip]) >= RATE_LIMIT:
            return jsonify({
                "error": "Rate limit exceeded. Please try again later.",
                "retry_after": 60 - (current_time - rate_limit_data[ip][0])
            }), 429
        
        rate_limit_data[ip].append(current_time)
        return f(*args, **kwargs)
    return decorated_function

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_domain(domain: str) -> bool:
    """Validate domain format."""
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9](?:\.[a-zA-Z]{2,})+$'
    return bool(re.match(pattern, domain))

def validate_request_data(data: Dict[str, Any], required_fields: list) -> tuple[bool, str]:
    """Validate request data and return (is_valid, error_message)."""
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    return True, ""

@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "version": "2.0.0-optimized",
        "endpoints": {
            "/verify": "POST - Verify a single email address",
            "/verify-bulk": "POST - High-performance bulk email verification (up to 1000 emails)",
            "/find": "POST - Find valid emails for a domain and names",
            "/stats": "GET - Get performance statistics",
            "/diagnostics/smtp": "GET - SMTP connectivity diagnostics"
        },
        "performance": {
            "max_emails_per_request": 1000,
            "estimated_time_1000_emails": "under 10 minutes",
            "concurrent_threads": scout.num_threads,
            "batch_size": scout.batch_size
        }
    })

@app.route("/verify", methods=["POST"])
@rate_limit
def verify_email():
    data = request.get_json(silent=True)
    is_valid, error = validate_request_data(data or {}, ["email"])
    if not is_valid:
        return jsonify({"error": error}), 400

    email = (data.get("email", "") if data else "").strip().lower()
    if not validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    try:
        result = scout.check_smtp(email)
        valid_bool = None
        status = None
        message = None
        if isinstance(result, dict):
            status = result.get("status")
            message = result.get("message")
            if status in ["valid", "risky"]:
                valid_bool = True
            elif status == "invalid":
                valid_bool = False
            else:
                valid_bool = None
        else:
            valid_bool = bool(result)

        return jsonify({
            "email": email,
            "valid": valid_bool,
            "status": status,
            "message": message,
            "details": result if isinstance(result, dict) else None,
            "timestamp": time.time()
        })
    except Exception as e:
        return jsonify({
            "error": "Email verification failed",
            "details": str(e)
        }), 500

@app.route("/verify-bulk", methods=["POST"])
@rate_limit
def verify_emails_bulk():
    """High-performance bulk email verification endpoint"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    emails = data.get("emails", [])
    if not isinstance(emails, list) or not emails:
        return jsonify({"error": "emails must be a non-empty list"}), 400

    # Limit to 1000 emails for performance
    if len(emails) > 1000:
        return jsonify({"error": "Maximum 1000 emails per request"}), 400

    # Validate email formats
    invalid_emails = []
    valid_emails = []
    for email in emails:
        if not isinstance(email, str) or not validate_email(email.strip().lower()):
            invalid_emails.append(email)
        else:
            valid_emails.append(email.strip().lower())

    if invalid_emails:
        return jsonify({
            "error": f"Invalid email formats: {invalid_emails[:5]}{'...' if len(invalid_emails) > 5 else ''}",
            "invalid_count": len(invalid_emails),
            "valid_count": len(valid_emails)
        }), 400

    try:
        start_time = time.time()
        
        # Progress tracking
        progress_data = {"completed": 0, "total": len(valid_emails), "results": []}
        
        def progress_callback(progress, batch_size, total_results):
            progress_data["completed"] = total_results
            # Could implement WebSocket or Server-Sent Events here for real-time updates
        
        # Perform bulk verification
        results = scout.verify_emails_bulk_optimized(valid_emails, progress_callback)
        
        # Calculate statistics
        valid_count = sum(1 for r in results if r.get('status') in ['valid', 'risky'])
        invalid_count = sum(1 for r in results if r.get('status') == 'invalid')
        unknown_count = sum(1 for r in results if r.get('status') == 'unknown')
        
        processing_time = round(time.time() - start_time, 2)
        performance_stats = scout.get_performance_stats()

        return jsonify({
            "success": True,
            "summary": {
                "total_emails": len(valid_emails),
                "valid_emails": valid_count,
                "invalid_emails": invalid_count,
                "unknown_emails": unknown_count,
                "processing_time_seconds": processing_time,
                "emails_per_second": round(len(valid_emails) / processing_time, 2) if processing_time > 0 else 0
            },
            "performance_stats": performance_stats,
            "results": results,
            "timestamp": time.time()
        })

    except Exception as e:
        return jsonify({
            "error": "Bulk email verification failed",
            "details": str(e)
        }), 500

@app.route("/stats", methods=["GET"])
def get_stats():
    """Get current performance statistics"""
    return jsonify({
        "performance_stats": scout.get_performance_stats(),
        "system_info": {
            "concurrent_threads": scout.num_threads,
            "batch_size": scout.batch_size,
            "smtp_timeout": scout.smtp_timeout,
            "cache_size": len(scout.mx_cache)
        },
        "timestamp": time.time()
    })

@app.route("/find", methods=["POST"])
@rate_limit
def find_emails():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        domain = data.get("domain", "").strip().lower()
        if not domain or not validate_domain(domain):
            return jsonify({"error": "Domain is required and must be valid"}), 400

        names = data.get("names", [])
        if not isinstance(names, list) or not names:
            return jsonify({"error": "Names must be a non-empty list"}), 400

        result = scout.find_valid_emails(domain=domain, names=names)

        response = {
            "domain": domain,
            "names": names,
            "result": result,
            "timestamp": time.time()
        }
        return jsonify(response)

    except Exception as e:
        print(f"Error in find_emails: {str(e)}")
        return jsonify({
            "error": "Email finding failed",
            "details": str(e)
        }), 500

@app.route("/diagnostics/smtp", methods=["GET"]) 
@rate_limit
def smtp_diagnostics():
    target = request.args.get("host", "aspmx.l.google.com")
    port = int(request.args.get("port", "25"))
    timeout = int(request.args.get("timeout", "5"))
    try:
        with socket.create_connection((target, port), timeout=timeout):
            reachable = True
    except Exception as e:
        reachable = False
        err = str(e)
    return jsonify({
        "target": f"{target}:{port}",
        "reachable": reachable,
        "note": None if reachable else "SMTP egress blocked or target unreachable",
        "timestamp": time.time()
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8008)
