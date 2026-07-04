# SENTINEL Deployment Checklist

## Target: Vultr VM at 78.141.222.154

---

## Pre-Deployment

- [ ] VM is accessible: `ssh root@78.141.222.154`
- [ ] Code is committed and pushed to GitHub
- [ ] `.env` file has valid Vultr API credentials
- [ ] All Phase 6 tests pass locally

---

## Deployment Execution

### 1. Copy Project to VM

```bash
# From local machine
scp -r /home/user/Sentinel root@78.141.222.154:/opt/sentinel
```

- [ ] Files copied successfully
- [ ] Verify: `ssh root@78.141.222.154 ls /opt/sentinel`

### 2. Configure Environment

```bash
ssh root@78.141.222.154
cd /opt/sentinel
nano .env
```

- [ ] VULTR_API_KEY is set
- [ ] All model IDs are correct
- [ ] File saved

### 3. Run Deployment Script

```bash
cd /opt/sentinel
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

- [ ] Script completes without errors
- [ ] Python 3.11 installed
- [ ] Node.js 18 installed
- [ ] nginx installed
- [ ] Dependencies installed
- [ ] Frontend built successfully

### 4. Start Services

```bash
systemctl start sentinel-backend
systemctl start nginx
systemctl enable sentinel-backend
systemctl enable nginx
```

- [ ] Backend starts: `systemctl status sentinel-backend`
- [ ] nginx starts: `systemctl status nginx`
- [ ] Services enabled for boot

---

## Verification

### Backend Health Check

```bash
curl http://localhost:8000/api/health
```

- [ ] Response: `{"status":"ok"}`

### Frontend Load Check

```bash
curl http://localhost/
```

- [ ] Returns HTML content
- [ ] No 404 errors

### Logs Check

```bash
journalctl -u sentinel-backend -n 20
```

- [ ] Vector store initialized
- [ ] 3 documents ingested
- [ ] Pipeline initialized
- [ ] WebSocket broadcaster wired
- [ ] Uvicorn running on 0.0.0.0:8000

### Browser Test

Open: `http://78.141.222.154`

- [ ] Monitor Page loads
- [ ] Connection indicator shows "Connected"
- [ ] "Run Agent" button is visible

### Agent Execution Test

1. Click "Run Agent"
2. Watch events appear in real-time
3. Wait for ACTION_FROZEN

- [ ] AGENT_PLAN event appears
- [ ] RETRIEVAL_PASS events appear (×3)
- [ ] TOOL_CALLED event appears
- [ ] DRIFT_SCORED event appears
- [ ] MAARS_PROBE event appears
- [ ] CITATION_CHECKED event appears
- [ ] ACTION_FROZEN event appears
- [ ] Freeze alert banner appears (red)

### Navigation Test

1. Click "View Signals" from freeze alert
2. Click "Proceed to Gate"
3. Click "Approve" or "Abort"

- [ ] Signal Page loads
- [ ] Three signal cards visible
- [ ] Model badges visible on each card
- [ ] Citations list visible
- [ ] Gate Page loads
- [ ] Operator decision buttons visible
- [ ] Decision submitted successfully
- [ ] Incident record appears
- [ ] SHA-256 hash visible
- [ ] Hash is copyable

### WebSocket Test

Browser console (F12):

- [ ] WebSocket connection established
- [ ] Events received in real-time
- [ ] No connection errors

---

## Post-Deployment

### Save Deployment State

```bash
# Create deployment snapshot
cd /opt/sentinel
git log --oneline -1 > /opt/sentinel/deploy/VERSION
echo "Deployed: $(date)" >> /opt/sentinel/deploy/VERSION
```

- [ ] Version file created
- [ ] Commit hash recorded
- [ ] Deployment timestamp recorded

### Document Deployment

- [ ] Update README with live URL
- [ ] Add deployment notes to project docs
- [ ] Record any issues encountered

---

## Quick Reference Commands

```bash
# View logs
journalctl -u sentinel-backend -f

# Restart services
systemctl restart sentinel-backend nginx

# Check status
systemctl status sentinel-backend nginx

# Update code
cd /opt/sentinel && git pull
pip install -r requirements.txt
cd frontend && npm install && npm run build
systemctl restart sentinel-backend

# Stop services
systemctl stop sentinel-backend nginx
```

---

## Deployment Complete?

- [ ] All checks passed
- [ ] Application is live at http://78.141.222.154
- [ ] Ready for Phase 7 (demo video)

**Deployment Status:** ⏳ In Progress  
**Timestamp:** _______________  
**Deployed By:** _______________
