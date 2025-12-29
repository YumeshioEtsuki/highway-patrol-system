## 📁 bin/ Directory Structure

This directory contains all startup scripts and utilities for the Highway Patrol System.

### 🚀 Quick Start (Windows Users)

```bash
# Main menu (Recommended for beginners)
menu.bat

# Quick start for development
startup.bat

# Full start (Redis + Celery + FastAPI)
startup_full.bat

# Config management tool
env-manager-web.bat
```

---

## 📂 Directory Structure

```
bin/
├── menu.bat                    # Main menu - Quick access to all tools
├── startup.bat                 # Quick start (dev mode)
├── startup_full.bat            # Full start (production-like)
├── stop_all.bat                # Stop all services
├── env-manager-web.bat         # Web-based config manager
├── env-manager-web.ps1         # PowerShell version
├── setup_password.bat          # Database password setup wizard
├── verify-dashboard-reports.py # Dashboard verification script
│
├── docs/                       # Documentation
│   ├── STARTUP_GUIDE.md
│   ├── TOOLS_GUIDE.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── DOCKER_INSTALL_GUIDE.md
│   └── REDIS_DOCKER_GUIDE.md
│
├── admin-tools/                # Admin utilities
│   ├── check_password.py
│   ├── create_admin.py
│   └── reset_admin_password.py
│
├── redis-tools/                # Redis utilities
│   └── start_redis.bat
│
└── linux-macos/                # Linux/macOS scripts (not for Windows users)
    ├── env-manager-web.sh
    ├── menu.sh
    └── start_redis.ps1
```

---

## 🎯 Common Tasks

### 1. First Time Setup
```bash
# Step 1: Configure database password
setup_password.bat

# Step 2: Start the system
menu.bat
→ Select: 1. Quick Start
```

### 2. Daily Development
```bash
# Quick start for development
startup.bat

# Or use menu for more options
menu.bat
```

### 3. Modify Configuration
```bash
# Open web-based config manager
env-manager-web.bat
→ Browser opens at http://127.0.0.1:5051
```

### 4. Full Environment (with Redis & Celery)
```bash
startup_full.bat
```

### 5. Admin Management
```bash
# Create new admin user
python admin-tools/create_admin.py

# Reset admin password
python admin-tools/reset_admin_password.py

# Check password hash
python admin-tools/check_password.py
```

---

## 📖 Documentation

All detailed documentation is in the `docs/` folder:

- **[STARTUP_GUIDE.md](docs/STARTUP_GUIDE.md)** - System startup guide
- **[TOOLS_GUIDE.md](docs/TOOLS_GUIDE.md)** - Development tools overview
- **[IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md)** - Architecture and design

---

## ⚙️ Script Details

### Core Startup Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `menu.bat` | Main menu | New users, quick access |
| `startup.bat` | Quick start (dev) | Daily development |
| `startup_full.bat` | Full start | Testing full features |
| `stop_all.bat` | Stop all services | Clean shutdown |

### Configuration Tools

| Script | Purpose | Interface |
|--------|---------|-----------|
| `env-manager-web.bat` | Config manager | Web UI (Recommended) |
| `setup_password.bat` | DB password setup | Interactive CLI |

### Admin Tools (in `admin-tools/`)

| Script | Purpose |
|--------|---------|
| `create_admin.py` | Create admin user |
| `reset_admin_password.py` | Reset password |
| `check_password.py` | Verify password hash |

---

## 🔧 Troubleshooting

### Issue: Virtual environment not found
```bash
# Create virtual environment first
python -m venv .venv
```

### Issue: Redis not starting
```bash
# Check Redis installation
redis-tools/start_redis.bat

# Or see Redis guide
docs/REDIS_DOCKER_GUIDE.md
```

### Issue: Database connection failed
```bash
# Reconfigure database password
setup_password.bat
```

---

## 📝 Notes

- **Windows Users**: Use `.bat` scripts (double-click or run in CMD)
- **PowerShell Users**: Use `.ps1` scripts (requires execution policy)
- **Linux/macOS Users**: Scripts are in `linux-macos/` folder
- **Documentation**: All docs are in `docs/` folder

---

## 🆘 Need Help?

1. Check documentation in `docs/` folder
2. Run `menu.bat` for guided options
3. Use web config tool: `env-manager-web.bat`

