# SENTINEL Deployment Guide

## Overview

This guide walks through deploying SENTINEL to the Vultr VM at `78.141.222.154`.

**Architecture:**
- Backend: FastAPI + Uvicorn (port 8000)
- Frontend: React (built static files)
- Reverse Proxy: nginx (port 80)
- Process Manager: systemd

## Pre-Deployment Checklist

- [ ] VM is accessible via SSH at `78.141.222.154`
- [ ] You have root access or sudo privileges
- [ ] `.env` file is configured with valid Vultr API credentials
- [ ] All code is committed and pushed to the repository

## Deployment Steps

### Step 1: Copy Project to VM

From your local machine, copy the entire project to the VM:

```bash
# From your local Sentinel directory
scp -r /home/user/Sentinel root@78.141.222.154:/opt/sentinel
```

**Alternative:** If you prefer to clone from GitHub on the VM:

```bash
ssh root@78.141.222.154
cd /opt
git clone https://github.com/knarayanareddy/Sentinel.git sentinel
cd sentinel
```

### Step 2: Configure Environment

SSH into the VM and configure the `.env` file:

```bash
ssh root@78.141.222.154
cd /opt/sentinel
nano .env
```

Ensure these values are set:

```bash
VULTR_API_KEY=your_actual_vultr_api_key
VULTR_BASE_URL=https://api.vultrinference.com/v1
REASONING_PRIME_MODEL=Qwen/Qwen3.6-27B
REASONING_CORE_MODEL=Qwen/Qwen3.6-27B
REASONING_FLASH_MODEL=deepseek-ai/DeepSeek-V4-Flash
VULTRON_RERANK_MODEL=vultr/VultronRetrieverFlash-Qwen3.5-0.8B
SANDBOX_EMAIL_SINK=mailhog
SENTINEL_ENV=production
```

### Step 3: Run Deployment Script

Make the deployment script executable and run it:

```bash
cd /opt/sentinel
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

The script will:
1. Update system packages
2. Install Python 3.11
3. Install Node.js 18
4. Install nginx
5. Install Python dependencies
6. Build the frontend
7. Configure systemd service
8. Configure nginx

### Step 4: Start Services

Start the backend and nginx:

```bash
systemctl start sentinel-backend
systemctl start nginx
```

Enable services to start on boot:

```bash
systemctl enable sentinel-backend
systemctl enable nginx
```

### Step 5: Verify Deployment

Check service status:

```bash
systemctl status sentinel-backend
systemctl status nginx
```

Check backend logs:

```bash
journalctl -u sentinel-backend -f
```

You should see:
```
[SENTINEL] Initializing vector store...
[SENTINEL] Vector store collection created.
[SENTINEL] Ingested: credit_agreement.md (item_id: ...)
[SENTINEL] Ingested: historical_ratios.md (item_id: ...)
[SENTINEL] Ingested: recent_transactions.md (item_id: ...)
[SENTINEL] Ingested 3 documents into vector store.
[SENTINEL] Initializing Sentinel pipeline...
[SENTINEL] Sentinel pipeline initialized.
[SENTINEL] WebSocket broadcaster wired to eventbus.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Test the health endpoint:

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{"status":"ok"}
```

Test the frontend:

```bash
curl http://localhost/
```

Expected: HTML content (React app)

### Step 6: Test from External Browser

Open your browser and navigate to:

```
http://78.141.222.154
```

You should see the SENTINEL Monitor Page with:
- "SENTINEL — Live Monitor" header
- Connection status indicator
- "Run Agent" button
- Empty event stream

Click "Run Agent" and verify:
1. Events appear in real-time
2. Agent completes all 7 steps
3. ACTION_FROZEN event appears
4. You can navigate to Signal Page
5. You can navigate to Gate Page
6. You can approve/abort the action
7. Incident record appears with SHA-256 hash

## Troubleshooting

### Backend Won't Start

Check logs:
```bash
journalctl -u sentinel-backend -n 50
```

Common issues:
- **Missing .env**: Ensure `.env` file exists and has all required variables
- **Port 8000 in use**: `lsof -i :8000` to find the process, then kill it
- **Python import errors**: Reinstall dependencies with `pip install -r requirements.txt`

### Frontend Not Loading

Check nginx status and logs:
```bash
systemctl status nginx
tail -f /var/log/nginx/error.log
```

Common issues:
- **404 errors**: Ensure frontend was built (`ls /opt/sentinel/frontend/dist/index.html`)
- **502 Bad Gateway**: Backend is not running, start it with `systemctl start sentinel-backend`
- **CORS errors**: Check that `ALLOWED_ORIGINS` in backend includes `http://78.141.222.154`

### WebSocket Not Connecting

Browser console should show:
```
WebSocket connection to 'ws://78.141.222.154/ws' established
```

If not connecting:
1. Check nginx config has WebSocket proxy settings
2. Verify backend is listening on port 8000
3. Check firewall allows WebSocket traffic
4. Try direct connection: `wscat -c ws://78.141.222.154/ws`

### Vector Store Issues

If you see "Collection does not contain any embeddings records":
1. Documents weren't ingested properly
2. Restart the backend: `systemctl restart sentinel-backend`
3. Check logs for ingestion errors

If you see "Maximum sequence length exceeded":
1. Document chunking isn't working
2. Ensure you're running the latest code with chunking fix
3. Pull latest code and rebuild: `git pull && ./deploy/deploy.sh`

## Maintenance Commands

### View Logs

```bash
# Backend logs (real-time)
journalctl -u sentinel-backend -f

# nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Restart Services

```bash
# Restart backend
systemctl restart sentinel-backend

# Restart nginx
systemctl restart nginx

# Restart both
systemctl restart sentinel-backend nginx
```

### Update Code

```bash
cd /opt/sentinel
git pull
pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..
systemctl restart sentinel-backend
```

### Check Resource Usage

```bash
# System resources
htop

# Disk usage
df -h

# Memory usage
free -h
```

## Security Considerations

### Current Setup (Development/Demo)

- No HTTPS (HTTP only)
- No authentication on API endpoints
- Open CORS (any origin allowed)

### Production Hardening (Future)

To prepare for production:

1. **Enable HTTPS with Let's Encrypt:**
   ```bash
   apt-get install certbot python3-certbot-nginx
   certbot --nginx -d your-domain.com
   ```

2. **Add authentication:**
   - Implement API key or JWT authentication
   - Protect `/api/run` and `/api/decide` endpoints

3. **Restrict CORS:**
   - Update `ALLOWED_ORIGINS` to specific domains
   - Remove wildcard `*`

4. **Rate limiting:**
   - Add nginx rate limiting for API endpoints
   - Prevent abuse of agent execution

5. **Firewall:**
   ```bash
   ufw allow 22    # SSH
   ufw allow 80    # HTTP
   ufw allow 443   # HTTPS
   ufw enable
   ```

## Rollback Plan

If deployment fails:

1. Stop services:
   ```bash
   systemctl stop sentinel-backend nginx
   ```

2. Restore previous code:
   ```bash
   cd /opt/sentinel
   git checkout <previous-commit-hash>
   ```

3. Rebuild and restart:
   ```bash
   pip install -r requirements.txt
   cd frontend && npm install && npm run build && cd ..
   systemctl start sentinel-backend nginx
   ```

## Support

If you encounter issues not covered in this guide:

1. Check the logs first
2. Review the troubleshooting section
3. Check GitHub issues for similar problems
4. Create a new issue with:
   - Error messages
   - Relevant log output
   - Steps to reproduce

---

**Deployment Status:** Ready to deploy  
**Target URL:** http://78.141.222.154  
**Last Updated:** Phase 6.5
