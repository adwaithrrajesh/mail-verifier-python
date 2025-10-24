# 📧 Hetzner Support Contact - SMTP Port Unblock Request

This folder contains all documentation needed to contact Hetzner support for unblocking SMTP ports.

## 📁 Files in This Folder

### 1. **REQUEST_SMTP_UNBLOCK.sh** ⭐ START HERE
**Purpose**: Automated guide with pre-filled support ticket template

**Usage**:
```bash
./REQUEST_SMTP_UNBLOCK.sh
```

This script displays:
- Your server details (IP, hostname)
- Complete support ticket template
- Step-by-step instructions
- Verification commands

### 2. **SUMMARY_SMTP_BLOCK.md**
**Purpose**: Complete root cause analysis

**Contains**:
- Problem description
- Test results showing all ports blocked
- Why it happens (Hetzner policy)
- All solution options
- Next steps

### 3. **UNBLOCK_SMTP_GUIDE.md**
**Purpose**: Detailed step-by-step unblock guide

**Contains**:
- Login instructions for Hetzner Console
- Support ticket submission process
- Message template
- Timeline expectations
- Verification steps after approval

### 4. **HETZNER_DEPLOYMENT.md**
**Purpose**: Original deployment documentation

**Contains**:
- Full Hetzner deployment guide
- Performance optimization tips
- Port configuration details
- Troubleshooting section

### 5. **test_smtp_locally.py**
**Purpose**: SMTP port connectivity testing script

**Usage**:
```bash
python3 test_smtp_locally.py
```

Tests all SMTP ports and shows blocked/open status.

## 🚀 Quick Start

### Step 1: Review the Problem
```bash
cat SUMMARY_SMTP_BLOCK.md
```

### Step 2: Get Support Ticket Template
```bash
./REQUEST_SMTP_UNBLOCK.sh
```

### Step 3: Submit to Hetzner
1. Go to: https://console.hetzner.cloud
2. Navigate: **Support → Create Ticket**
3. Copy the template from Step 2
4. Submit the request

### Step 4: Wait for Approval
- **Timeline**: 1-4 weeks
- **Notification**: Email from Hetzner support

### Step 5: Verify After Approval
```bash
# Quick test
timeout 3 bash -c 'cat < /dev/null > /dev/tcp/gmail-smtp-in.l.google.com/587' \
  && echo "✅ UNBLOCKED" || echo "❌ Still blocked"

# Or use the test script
python3 test_smtp_locally.py
```

## 📋 Support Ticket Information

**What to Include**:
- ✅ Server IP: 91.98.122.114
- ✅ Server Name: mailsfinder-server
- ✅ Use Case: Email verification service
- ✅ Ports Needed: 25, 465, 587 (outbound)
- ✅ Confirmation: Will NOT send spam

**Subject Line**:
```
Unblock outbound SMTP ports (25, 465, 587) for email verification service
```

## ⚠️ Important Notes

1. **Be Clear**: Explain you're verifying emails, NOT sending bulk emails
2. **Be Patient**: Approval takes 1-4 weeks
3. **Be Professional**: Follow the provided template
4. **Be Honest**: Hetzner will deny if they suspect spam

## 🔄 Alternative Solutions

If Hetzner denies or takes too long:

### Option A: Different Cloud Provider
- AWS EC2 (SMTP open by default)
- DigitalOcean
- Vultr
- Linode

### Option B: Email Validation APIs
- ZeroBounce
- NeverBounce
- Hunter.io
- Clearout

### Option C: Hybrid Approach
- DNS/MX validation (works without SMTP)
- Third-party API for deliverability
- Combine both methods

## 📞 Hetzner Contact Information

**Support Portal**: https://console.hetzner.cloud
**Documentation**: https://docs.hetzner.com
**Community**: https://community.hetzner.com

## ✅ Current Status

- **Server**: Running
- **Docker**: Configured
- **Application**: Ready
- **SMTP Ports**: ❌ BLOCKED (waiting for Hetzner approval)

## 🎯 Next Action

**Run this command now**:
```bash
./REQUEST_SMTP_UNBLOCK.sh
```

Then submit the support ticket to Hetzner.
