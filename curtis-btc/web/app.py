import os
import json
import requests
from datetime import datetime
from flask import Flask, render_template, request, redirect, jsonify
from typing import Dict, Any

app = Flask(__name__)

CONFIG_PATH = "/data/config.json"
STATE_PATH = "/data/state.json"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "").strip()

# Bitcoin RPC configuration
BTC_RPC_USER = os.getenv("BITCOIN_RPC_USER", "")
BTC_RPC_PASS = os.getenv("BITCOIN_RPC_PASS", "")
BTC_RPC_HOST = os.getenv("BITCOIN_RPC_HOST", "localhost")
BTC_RPC_PORT = os.getenv("BITCOIN_RPC_PORT", "8332")


def load_config() -> Dict[str, Any]:
    """Load application configuration"""
    defaults = {
        "discord_webhook": "",
        "notify_blocks": True,
        "notify_ath": True,
        "pruning_enabled": False,
        "pruning_target_gb": 50,
        "poll_seconds": 30,
    }
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            for key in defaults:
                if key in data and data[key] is not None:
                    defaults[key] = data[key]
    except Exception:
        pass
    return defaults


def save_config(data: Dict[str, Any]) -> None:
    """Save application configuration"""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_state() -> Dict[str, Any]:
    """Load monitoring state"""
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def check_password(pw: str) -> bool:
    """Verify admin password"""
    if not ADMIN_PASSWORD:
        return True
    return pw == ADMIN_PASSWORD


def bitcoin_rpc(method: str, params: list = None) -> Any:
    """Make RPC call to Bitcoin node"""
    if params is None:
        params = []
    
    url = f"http://{BTC_RPC_HOST}:{BTC_RPC_PORT}"
    headers = {"content-type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": "btc-monitor",
        "method": method,
        "params": params
    }
    
    try:
        response = requests.post(
            url,
            auth=(BTC_RPC_USER, BTC_RPC_PASS),
            headers=headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        return result.get("result")
    except Exception as e:
        print(f"RPC Error ({method}): {e}")
        return None


def get_blockchain_info() -> Dict[str, Any]:
    """Get blockchain synchronization status"""
    info = bitcoin_rpc("getblockchaininfo")
    if not info:
        return {
            "connected": False,
            "blocks": 0,
            "headers": 0,
            "sync_progress": 0,
            "verification_progress": 0,
            "chain": "unknown",
            "difficulty": 0,
            "size_on_disk": 0,
            "pruned": False,
            "prune_target_size": 0,
        }
    
    return {
        "connected": True,
        "blocks": info.get("blocks", 0),
        "headers": info.get("headers", 0),
        "sync_progress": info.get("verificationprogress", 0) * 100,
        "verification_progress": info.get("verificationprogress", 0),
        "chain": info.get("chain", "main"),
        "difficulty": info.get("difficulty", 0),
        "size_on_disk": info.get("size_on_disk", 0),
        "pruned": info.get("pruned", False),
        "prune_target_size": info.get("pruneheight", 0) if info.get("pruned") else 0,
        "initial_block_download": info.get("initialblockdownload", False),
    }


def get_network_info() -> Dict[str, Any]:
    """Get network information"""
    info = bitcoin_rpc("getnetworkinfo")
    if not info:
        return {
            "version": "Unknown",
            "subversion": "Unknown",
            "connections": 0,
        }
    
    return {
        "version": info.get("version", "Unknown"),
        "subversion": info.get("subversion", "Unknown"),
        "connections": info.get("connections", 0),
    }


def format_bytes(bytes_val: int) -> str:
    """Format bytes to human readable format"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} PB"


@app.route("/")
def index():
    """Main dashboard page"""
    pw = request.args.get("pw", "")
    needs_pw = ADMIN_PASSWORD and not check_password(pw)
    
    cfg = load_config()
    state = load_state()
    blockchain = get_blockchain_info()
    network = get_network_info()
    
    return render_template(
        "index.html",
        cfg=cfg,
        state=state,
        blockchain=blockchain,
        network=network,
        needs_pw=needs_pw,
        format_bytes=format_bytes,
    )


@app.route("/api/stats")
def api_stats():
    """API endpoint for stats"""
    blockchain = get_blockchain_info()
    network = get_network_info()
    state = load_state()
    
    return jsonify({
        "blockchain": blockchain,
        "network": network,
        "state": state,
    })


@app.route("/api/widget/stats")
def widget_stats():
    """Widget API endpoint"""
    blockchain = get_blockchain_info()
    
    sync_percent = f"{blockchain['sync_progress']:.1f}%"
    if blockchain['sync_progress'] >= 99.9:
        sync_percent = "✓ Synced"
    
    return jsonify({
        "type": "two-stats",
        "items": [
            {
                "title": "Sync Progress",
                "value": sync_percent
            },
            {
                "title": "Blocks",
                "value": f"{blockchain['blocks']:,}"
            }
        ]
    })


@app.route("/save", methods=["POST"])
def save():
    """Save configuration"""
    pw = request.form.get("pw", "")
    if not check_password(pw):
        return redirect("/?pw=" + pw)
    
    cfg = {
        "discord_webhook": request.form.get("discord_webhook", "").strip(),
        "notify_blocks": request.form.get("notify_blocks") == "on",
        "notify_ath": request.form.get("notify_ath") == "on",
        "pruning_enabled": request.form.get("pruning_enabled") == "on",
        "pruning_target_gb": int(request.form.get("pruning_target_gb", "50")),
        "poll_seconds": int(request.form.get("poll_seconds", "30")),
    }
    save_config(cfg)
    return redirect("/?pw=" + pw + "&saved=1")


@app.route("/reset", methods=["POST"])
def reset():
    """Reset blockchain (stop and restart with -reindex)"""
    pw = request.form.get("pw", "")
    if not check_password(pw):
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    
    # In a real implementation, this would trigger a container restart
    # with the -reindex flag set in the Bitcoin configuration
    return jsonify({
        "success": True,
        "message": "Reset initiated. This feature requires manual configuration."
    })


@app.route("/test-webhook", methods=["POST"])
def test_webhook():
    """Test Discord webhook"""
    pw = request.form.get("pw", "")
    if not check_password(pw):
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    
    cfg = load_config()
    webhook = cfg.get("discord_webhook", "").strip()
    
    if not webhook:
        return jsonify({"success": False, "error": "No webhook configured"}), 400
    
    blockchain = get_blockchain_info()
    
    embed = {
        "embeds": [{
            "title": "🔔 BTC Monitor Test",
            "description": "Webhook test successful!",
            "color": 0xF7931A,
            "fields": [
                {
                    "name": "⛓️ Current Height",
                    "value": f"{blockchain['blocks']:,}",
                    "inline": True
                },
                {
                    "name": "📊 Sync Progress",
                    "value": f"{blockchain['sync_progress']:.2f}%",
                    "inline": True
                },
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "Curtis BTC ⚡"}
        }]
    }
    
    try:
        response = requests.post(webhook, json=embed, timeout=10)
        response.raise_for_status()
        return jsonify({"success": True, "message": "Webhook test sent!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3456, debug=False)
