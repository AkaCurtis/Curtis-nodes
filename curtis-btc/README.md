# Curtis BTC ⚡

Bitcoin Monitoring, Perfected

## Features

### 📊 Real-time Sync Progress
- Visual progress bar showing blockchain synchronization status
- Live updates every 30 seconds
- Displays current block height vs. total headers
- Shows sync percentage with precision

### 🔔 Discord Notifications
- **New Block Alerts**: Get notified when new blocks are found
- **All-Time High Alerts**: Special notifications for blockchain height records
- **Sync Milestones**: Progress updates at 10%, 20%, 30%, etc.
- **Connection Issues**: Alerts when Bitcoin node is unreachable
- Customizable notification settings

### 💾 Pruning Support
- Enable blockchain pruning to save disk space
- Configure pruning target size (minimum 5GB)
- Monitor current disk usage
- See pruning status in real-time

### 🚀 Quick Syncing
- Optimized polling intervals (configurable)
- Lightweight monitoring with minimal overhead
- Efficient RPC calls to Bitcoin node
- Auto-reconnect on connection failures

### 🎨 Clean Modern UI
- Dark theme optimized for readability
- Live statistics dashboard
- Current block height, connections, disk usage, difficulty
- Recent activity tracking
- Mobile-responsive design

### 🔄 Reset Functionality
- Reset blockchain with one click
- Trigger reindex operations
- Confirmation dialogs to prevent accidents

## Installation

1. Place this folder in your Umbrel app-data directory:
   ```
   /umbrel/app-data/curtis-btc/
   ```

2. Make sure Bitcoin Knots (or Bitcoin Core) is installed and running

3. Configure the app through Umbrel settings or by editing `settings.yml`

4. Start the app through Umbrel dashboard

## Configuration

### Environment Variables

Configure these in Umbrel settings or `exports.sh`:

- `APP_CURTIS_BTC_ADMIN_PASSWORD`: Password to protect settings (optional)
- `APP_CURTIS_BTC_POLL_SECONDS`: How often to check node status (default: 30)
- `APP_CURTIS_BTC_DISCORD_WEBHOOK`: Discord webhook URL for notifications
- `APP_CURTIS_BTC_NOTIFY_BLOCKS`: Enable new block notifications (default: true)
- `APP_CURTIS_BTC_NOTIFY_ATH`: Enable all-time high notifications (default: true)
- `APP_CURTIS_BTC_PRUNING_ENABLED`: Enable blockchain pruning (default: false)
- `APP_CURTIS_BTC_PRUNING_TARGET_GB`: Pruning target in GB (default: 50)

### Discord Webhook Setup

1. Go to your Discord server settings
2. Navigate to Integrations → Webhooks
3. Click "New Webhook"
4. Customize name and channel
5. Copy webhook URL
6. Paste into BTC Monitor settings
7. Test webhook to verify connection

## Usage

### Dashboard

The main dashboard displays:
- **Sync Status Badge**: Shows current synchronization state
- **Progress Bar**: Visual representation of sync progress
- **Statistics Grid**: 
  - Current block height
  - Network connections
  - Disk usage
  - Network difficulty
- **Node Information**: Chain, version, pruning status
- **Recent Activity**: Last block time, ATH, blocks found today

### Settings Panel

Configure all features from the web interface:
- Discord webhook URL
- Notification preferences
- Pruning settings
- Monitoring interval

### Testing

Use the "Test Webhook" button to verify Discord integration without waiting for events.

### Reset Blockchain

The reset button allows you to trigger a blockchain reindex. Use with caution as this process can take hours.

## API Endpoints

### GET `/api/stats`
Returns JSON with blockchain, network, and state information.

```json
{
  "blockchain": {
    "blocks": 850432,
    "headers": 850432,
    "sync_progress": 100.0,
    "connected": true,
    ...
  },
  "network": {
    "connections": 12,
    "version": "270000",
    ...
  },
  "state": {
    "last_block": 850432,
    "last_ath": 850432,
    ...
  }
}
```

### GET `/api/widget/stats`
Umbrel widget endpoint for dashboard integration.

## Architecture

```
curtis-btc/
├── umbrel-app.yml          # App manifest
├── docker-compose.yml      # Container orchestration
├── settings.yml            # User-configurable settings
├── exports.sh             # Environment variable exports
├── web/                   # Flask web application
│   ├── app.py            # Main application
│   ├── Dockerfile        # Web container config
│   ├── requirements.txt  # Python dependencies
│   └── templates/
│       └── index.html    # Dashboard UI
└── watcher/              # Background monitoring service
    ├── watcher.py        # Main watcher script
    ├── Dockerfile        # Watcher container config
    └── requirements.txt  # Python dependencies
```

## Dependencies

- **Bitcoin Knots** (or Bitcoin Core) - Required for RPC access
- **Python 3.11** - Runtime environment
- **Flask** - Web framework
- **Requests** - HTTP client library

## Troubleshooting

### "Failed to connect to Bitcoin node"
- Verify Bitcoin Knots/Core is running
- Check RPC credentials in environment variables
- Ensure Bitcoin RPC port is accessible

### "Webhook test failed"
- Verify Discord webhook URL is correct
- Check network connectivity
- Ensure webhook hasn't been deleted in Discord

### "Progress not updating"
- Check poll interval setting
- Verify watcher container is running
- Check container logs for errors

### "Page not loading"
- Verify web container is running
- Check port 3456 is not in use
- Review container logs

## Development

To run locally for development:

```bash
# Web interface
cd web
pip install -r requirements.txt
export BITCOIN_RPC_USER=your_user
export BITCOIN_RPC_PASS=your_pass
export BITCOIN_RPC_HOST=localhost
export BITCOIN_RPC_PORT=8332
python app.py

# Watcher service
cd watcher
pip install -r requirements.txt
export BITCOIN_RPC_USER=your_user
export BITCOIN_RPC_PASS=your_pass
python watcher.py
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

MIT License - See LICENSE file for details

## Support

For issues and feature requests, please use the GitHub issue tracker or visit the support forums.

## Credits

Built for the Bitcoin and Umbrel communities with ❤️

---

**Note**: This app requires a Bitcoin node to function. It works with both Bitcoin Knots and Bitcoin Core.
