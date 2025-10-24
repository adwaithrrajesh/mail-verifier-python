#!/bin/bash

echo "================================================================"
echo "HETZNER SMTP PORT UNBLOCK REQUEST - AUTOMATED GUIDE"
echo "================================================================"
echo ""
echo "Server Details:"
echo "  Hostname: $(hostname)"
echo "  IP Address: $(hostname -I | awk '{print $1}')"
echo ""
echo "================================================================"
echo "STEP 1: Contact Hetzner Support"
echo "================================================================"
echo ""
echo "URL: https://console.hetzner.cloud"
echo ""
echo "Navigate to: Support → Create Ticket"
echo ""
echo "================================================================"
echo "STEP 2: Use This Template"
echo "================================================================"
echo ""
cat << 'TEMPLATE'
Subject: Unblock outbound SMTP ports (25, 465, 587) for email verification service

Hello Hetzner Support Team,

I am requesting to unblock outbound SMTP ports for my server:

Server IP: 91.98.122.114
Server Name: mailsfinder-server
Project: Email Verification Service

Purpose:
- Running a legitimate email verification API (MailScout)
- Performing SMTP validation to check email deliverability
- NOT sending bulk emails or spam
- Only verifying if email addresses exist via SMTP handshake

Technical Details:
- Application: Python-based email validator
- Ports needed: 25, 465, 587 (outbound only)
- Expected usage: Email validation requests
- Will respect rate limits and anti-spam policies

I understand Hetzner's anti-spam policies and confirm this service will:
✓ Only validate email addresses (no email sending)
✓ Follow best practices for email verification
✓ Not be used for spam or unsolicited emails
✓ Respect target server rate limits

Please let me know if you need any additional information.

Thank you for your assistance.
TEMPLATE

echo ""
echo "================================================================"
echo "STEP 3: Wait for Response"
echo "================================================================"
echo "Timeline: 1-4 weeks (sometimes faster)"
echo ""
echo "================================================================"
echo "STEP 4: Verify After Approval"
echo "================================================================"
echo "Run this command to test:"
echo ""
echo "  timeout 3 bash -c 'cat < /dev/null > /dev/tcp/gmail-smtp-in.l.google.com/587' && echo '✅ UNBLOCKED' || echo '❌ Still blocked'"
echo ""
echo "Or use the diagnostics endpoint:"
echo "  curl 'http://localhost:9080/diagnostics/smtp?host=gmail-smtp-in.l.google.com&port=587'"
echo ""
echo "================================================================"
echo "ALTERNATIVE: Use a Different Server"
echo "================================================================"
echo "If you need immediate access, consider:"
echo "  - AWS EC2 (SMTP ports open by default)"
echo "  - DigitalOcean"
echo "  - Vultr"
echo "  - Your own dedicated server"
echo ""
