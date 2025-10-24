# 🔓 How to Unblock SMTP Ports on Hetzner

## Problem
Hetzner blocks outbound SMTP ports (25, 465, 587) by default to prevent spam.

## Solution: Request Port Unblock

### Step 1: Login to Hetzner Console
https://console.hetzner.cloud

### Step 2: Create Support Ticket
1. Go to **Support** → **Create Ticket**
2. Select your project

### Step 3: Submit Request
**Subject**: Unblock outbound SMTP ports for email verification service

**Message Template**:
```
Hello Hetzner Support,

I am requesting to unblock outbound SMTP ports (25, 465, 587) for my server.

Server: [Your Server Name/IP]
Use Case: Legitimate email verification service for business purposes
Application: Email validation API that verifies email deliverability

I understand the anti-spam policies and confirm this will be used only for 
legitimate email verification, not for sending bulk emails.

Thank you.
```

### Step 4: Wait for Approval
- **Timeline**: 1-4 weeks
- **Response**: Hetzner will review and approve/deny

## Alternative: Use Different Provider
If you need immediate access:
- AWS EC2 (ports open by default)
- DigitalOcean
- Vultr
- Linode

## Verification After Unblock
```bash
# Test port 587
timeout 3 bash -c 'cat < /dev/null > /dev/tcp/gmail-smtp-in.l.google.com/587' && echo "✅ Port 587 OPEN" || echo "❌ Still blocked"

# Or use the diagnostics endpoint
curl "http://localhost:9080/diagnostics/smtp?host=gmail-smtp-in.l.google.com&port=587"
```
