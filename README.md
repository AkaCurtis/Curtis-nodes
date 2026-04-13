# Curtis BTC - Umbrel App Store

This repository contains the Curtis BTC app for Umbrel - a professional Bitcoin node monitoring application.

## 📁 Repository Structure

This repo is structured as an **Umbrel app store** repository with `umbrel-app-store.yml` at the root:

```
Curtis-Umbrel/
├── README.md                # This file
├── umbrel-app-store.yml     # App store manifest (REQUIRED)
└── curtis-btc/              # App directory
    ├── umbrel-app.yml       # App manifest
    ├── docker-compose.yml   # Container configuration
    ├── settings.yml         # User settings
    ├── exports.sh           # Environment variables
    ├── icon.svg             # App icon (vector)
    ├── icon.png             # App icon (raster)
    ├── README.md            # App documentation
    ├── docker-compose.standalone.yml  # Testing config
    ├── web/                 # Flask web interface
    │   ├── app.py
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── templates/
    │       └── index.html
    └── watcher/             # Monitoring service
        ├── watcher.py
        ├── Dockerfile
        └── requirements.txt
```

**Key files:**
- `umbrel-app-store.yml` - Identifies this repo as an app store
- `curtis-btc/umbrel-app.yml` - Defines the Curtis BTC app

## 🚀 Adding as a Custom App Store

To add this repository as a custom app store in Umbrel:

1. **In Umbrel UI:**
   - Go to App Store → Community App Stores
   - Add repository: `https://github.com/AkaCurtis/Curtis-Umbrel`

2. **Or via CLI:**
   ```bash
   # The app store should auto-discover the curtis-btc/ folder
   # Check if it appears:
   ls /home/umbrel/umbrel/app-stores/*/curtis-btc/
   ```

3. **Force refresh:**
   ```bash
   sudo rm -rf /home/umbrel/umbrel/app-stores/.tmp/*
   sudo systemctl restart umbrel
   ```

## 📦 What is Curtis BTC?

Curtis BTC is a comprehensive Bitcoin node monitoring app featuring:

- ✨ **Real-time Sync Progress** - Beautiful progress bars
- 📊 **Clean Dashboard** - Modern UI with live stats
- 🔔 **Discord Notifications** - Block alerts and milestones
- 💾 **Pruning Control** - Save disk space
- 🚀 **Quick Sync** - Optimized monitoring
- 🔄 **One-Click Reset** - Easy blockchain reindex

See [curtis-btc/README.md](curtis-btc/README.md) for full documentation.

## 🔧 Development & Testing

To test the app locally without Umbrel:

1. **Standalone Testing:**
   ```bash
   cd curtis-btc
   docker compose -f docker-compose.standalone.yml up
   ```
   Access at: `http://localhost:3457`

2. **Check Logs:**
   ```bash
   docker logs curtis-btc_web_1 -f
   docker logs curtis-btc_watcher_1 -f
   ```

## 📝 Important: Repository Structure
App Store Repositories:**
1. Looks for `umbrel-app-store.yml` at root → Confirms it's an app store
2. Scans subdirectories for `umbrel-app.yml` files
3. Finds `curtis-btc/umbrel-app.yml` → App discovered and added

**What doesn't work:**
- ❌ `umbrel-app.yml` at root (no app store file)
- ❌ No `umbrel-app-store.yml` (repo not recognized as app store
Umbrel expects app stores to contain **app folders**, not to BE the app itself. This is why the app lives inside `curtis-btc/` rather than at the repo root.

**How Umbrel Scans Repositories:**
- ✅ Finds `curtis-btc/umbrel-app.yml` → App discovered and added to store
- ❌ Finds `umbrel-app.yml` at root → Ignored (not in an app folder)

### Migration from Old Structure

If you previously cloned this repo when files were at the root level:

1. **Pull the latest changes:**
   ```bash
   git pull origin main
   ```

2. **Old root-level files can be deleted** (if they still exist):
   - Old: `umbrel-app.yml`, `docker-compose.yml`, `web/`, `watcher/`, `exports.sh`, `settings.yml`
   - New: `umbrel-app-store.yml` at root, everything else in `curtis-btc/` subdirectory

## 🐛 Troubleshooting
# Should find the app store manifest
   find ~/umbrel/app-stores -maxdepth 3 -name "umbrel-app-store.yml"
   # Should find the app manifest
   find ~/umbrel/app-stores -maxdepth 4 -name "umbrel-app.yml"
   ```
   
   You should see:
   ```
   .../Curtis-Umbrel/umbrel-app-store.yml
   .../Curtis-Umbrel/curtis-btc/umbrel-app.yml
   ``
1. **Check directory structure:**
   ```bash
   find /home/umbrel/umbrel/app-stores -name "umbrel-app.yml"
   ```
   You should see: `.../curtis-btc/umbrel-app.yml`

2. **Clear cache and restart:**
   ```bash
   sudo rm -rf /home/umbrel/umbrel/app-stores/.tmp/*
   sudo systemctl restart umbrel
   ```

3. **Wait 2-3 minutes** then check Umbrel App Store UI

### Icon Files

If icons are missing, the app requires these files in `curtis-btc/`:
- `icon.svg` - Vector icon (200x200px recommended)
- `icon.png` - Raster icon (512x512px recommended)

## 🔗 Links

- **App ID:** `curtis-btc`
- **Repository:** https://github.com/AkaCurtis/Curtis-Umbrel
- **Issues:** https://github.com/AkaCurtis/Curtis-Umbrel/issues
- **App Documentation:** [curtis-btc/README.md](curtis-btc/README.md)

## 📜 License

MIT License - Built with ❤️ for the Bitcoin community

---

**Curtis BTC ⚡ - Bitcoin monitoring, perfected**
