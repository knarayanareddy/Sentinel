# SENTINEL Deployment Files

This directory contains all configuration files and scripts needed to deploy SENTINEL to the Vultr VM.

## Files

| File | Purpose |
|------|---------|
| `sentinel-backend.service` | systemd service configuration for the backend API |
| `nginx.conf` | nginx reverse proxy configuration |
| `deploy.sh` | Automated deployment script |
| `DEPLOYMENT.md` | Comprehensive deployment guide |
| `CHECKLIST.md` | Quick deployment checklist |

## Quick Start

```bash
# 1. Copy project to VM
scp -r /home/user/Sentinel root@78.141.222.154:/opt/sentinel

# 2. SSH into VM
ssh root@78.141.222.154

# 3. Configure environment
cd /opt/sentinel
nano .env

# 4. Run deployment
chmod +x deploy/deploy.sh
./deploy/deploy.sh

# 5. Start services
systemctl start sentinel-backend nginx
systemctl enable sentinel-backend nginx
```

## Target Environment

- **VM IP:** 78.141.222.154
- **Backend:** http://78.141.222.154:8000 (internal)
- **Frontend:** http://78.141.222.154:80 (public)
- **WebSocket:** ws://78.141.222.154/ws

## Architecture

```
Internet → nginx (port 80)
              ├─ /api/* → Backend API (port 8000)
              ├─ /ws → WebSocket (port 8000)
              └─ /* → Frontend (static files)
```

## Troubleshooting

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting guide.

Common commands:
```bash
# View logs
journalctl -u sentinel-backend -f

# Restart services
systemctl restart sentinel-backend nginx

# Check status
systemctl status sentinel-backend nginx
```
