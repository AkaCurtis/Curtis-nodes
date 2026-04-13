import os
import time
import json
import requests
import sys
from typing import Dict, Any, Optional
from datetime import datetime, timezone

# Configuration paths
CONFIG_PATH = "/data/config.json"
STATE_PATH = "/data/state.json"

# Environment variables
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "30"))
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK", "").strip()
NOTIFY_BLOCKS = os.getenv("NOTIFY_BLOCKS", "true").lower() == "true"
NOTIFY_ATH = os.getenv("NOTIFY_ATH", "true").lower() == "true"

# Bitcoin RPC configuration
BTC_RPC_USER = os.getenv("BITCOIN_RPC_USER", "")
BTC_RPC_PASS = os.getenv("BITCOIN_RPC_PASS", "")
BTC_RPC_HOST = os.getenv("BITCOIN_RPC_HOST", "localhost")
BTC_RPC_PORT = os.getenv("BITCOIN_RPC_PORT", "8332")


def log(message: str) -> None:
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)
    sys.stdout.flush()


def load_config() -> Dict[str, Any]:
    """Load configuration from file"""
    defaults = {
        "discord_webhook": DISCORD_WEBHOOK,
        "notify_blocks": NOTIFY_BLOCKS,
        "notify_ath": NOTIFY_ATH,
        "poll_seconds": POLL_SECONDS,
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


def load_state() -> Dict[str, Any]:
    """Load monitoring state"""
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "last_block": 0,
            "last_ath": 0,
            "blocks_found_today": 0,
            "last_block_time": None,
            "startup_time": datetime.now(timezone.utc).isoformat(),
        }


def save_state(state: Dict[str, Any]) -> None:
    """Save monitoring state"""
    try:
        os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        log(f"Failed to save state: {e}")


def bitcoin_rpc(method: str, params: list = None) -> Optional[Any]:
    """Make RPC call to Bitcoin node"""
    if params is None:
        params = []
    
    url = f"http://{BTC_RPC_HOST}:{BTC_RPC_PORT}"
    headers = {"content-type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": "btc-monitor-watcher",
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
        log(f"RPC Error ({method}): {e}")
        return None


def get_blockchain_info() -> Optional[Dict[str, Any]]:
    """Get blockchain information"""
    info = bitcoin_rpc("getblockchaininfo")
    if not info:
        return None
    
    return {
        "blocks": info.get("blocks", 0),
        "headers": info.get("headers", 0),
        "sync_progress": info.get("verificationprogress", 0) * 100,
        "chain": info.get("chain", "main"),
        "difficulty": info.get("difficulty", 0),
        "size_on_disk": info.get("size_on_disk", 0),
        "pruned": info.get("pruned", False),
        "initial_block_download": info.get("initialblockdownload", False),
    }


def get_block_hash(height: int) -> Optional[str]:
    """Get block hash for given height"""
    return bitcoin_rpc("getblockhash", [height])


def get_block_info(block_hash: str) -> Optional[Dict[str, Any]]:
    """Get detailed block information"""
    return bitcoin_rpc("getblock", [block_hash, 1])


def get_network_info() -> Optional[Dict[str, Any]]:
    """Get network information"""
    info = bitcoin_rpc("getnetworkinfo")
    if not info:
        return None
    
    return {
        "version": info.get("version", 0),
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


def send_discord_notification(title: str, description: str, fields: list = None, 
                              color: int = 0xF7931A) -> bool:
    """Send notification to Discord webhook"""
    cfg = load_config()
    webhook = cfg.get("discord_webhook", "").strip()
    
    if not webhook:
        return False
    
    if fields is None:
        fields = []
    
    embed = {
        "embeds": [{
            "title": title,
            "description": description,
            "color": color,
            "fields": fields,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "Curtis BTC ⚡"}
        }]
    }
    
    try:
        response = requests.post(webhook, json=embed, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        log(f"Failed to send Discord notification: {e}")
        return False


def check_new_block(blockchain: Dict[str, Any], state: Dict[str, Any]) -> None:
    """Check for new blocks and send notifications"""
    cfg = load_config()
    current_block = blockchain["blocks"]
    last_block = state.get("last_block", 0)
    
    if current_block > last_block and last_block > 0:
        # New block found!
        log(f"🎉 New block detected: {current_block}")
        
        # Get block details
        block_hash = get_block_hash(current_block)
        block_info = get_block_info(block_hash) if block_hash else None
        
        # Update state
        state["last_block"] = current_block
        state["last_block_time"] = datetime.now(timezone.utc).isoformat()
        
        # Track blocks found today
        today = datetime.now().strftime("%Y-%m-%d")
        last_date = state.get("last_date", "")
        if today != last_date:
            state["blocks_found_today"] = 1
            state["last_date"] = today
        else:
            state["blocks_found_today"] = state.get("blocks_found_today", 0) + 1
        
        # Check for all-time high
        is_ath = current_block > state.get("last_ath", 0)
        if is_ath:
            state["last_ath"] = current_block
            log(f"🏆 New all-time high: {current_block}")
        
        save_state(state)
        
        # Send Discord notifications
        if cfg.get("notify_blocks", True):
            fields = [
                {
                    "name": "⛓️ Block Height",
                    "value": f"{current_block:,}",
                    "inline": True
                },
                {
                    "name": "🔗 Block Hash",
                    "value": f"`{block_hash[:16]}...`" if block_hash else "N/A",
                    "inline": True
                },
                {
                    "name": "📊 Sync Progress",
                    "value": f"{blockchain['sync_progress']:.2f}%",
                    "inline": True
                },
            ]
            
            if block_info:
                fields.append({
                    "name": "📦 Transactions",
                    "value": str(len(block_info.get("tx", []))),
                    "inline": True
                })
                fields.append({
                    "name": "💾 Size",
                    "value": format_bytes(block_info.get("size", 0)),
                    "inline": True
                })
                fields.append({
                    "name": "⏰ Time",
                    "value": datetime.fromtimestamp(
                        block_info.get("time", 0), tz=timezone.utc
                    ).strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "inline": True
                })
            
            title = "🔔 New Block Found!"
            if is_ath and cfg.get("notify_ath", True):
                title = "🏆 New All-Time High Block!"
                fields.insert(0, {
                    "name": "🎉 Achievement",
                    "value": "**New blockchain height record!**",
                    "inline": False
                })
            
            send_discord_notification(
                title=title,
                description=f"Block **#{current_block:,}** has been added to the blockchain.",
                fields=fields,
                color=0x10B981 if is_ath else 0xF7931A
            )
    elif last_block == 0:
        # First run, just store the current block
        state["last_block"] = current_block
        state["last_ath"] = current_block
        save_state(state)


def check_sync_milestone(blockchain: Dict[str, Any], state: Dict[str, Any]) -> None:
    """Check for sync milestones and notify"""
    sync_progress = blockchain["sync_progress"]
    last_milestone = state.get("last_sync_milestone", 0)
    
    # Notify on every 10% milestone
    milestones = [10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99]
    for milestone in milestones:
        if sync_progress >= milestone and last_milestone < milestone:
            log(f"📊 Sync milestone reached: {milestone}%")
            
            send_discord_notification(
                title=f"📊 Sync Progress: {milestone}%",
                description=f"Your Bitcoin node is {milestone}% synchronized.",
                fields=[
                    {
                        "name": "⛓️ Current Block",
                        "value": f"{blockchain['blocks']:,}",
                        "inline": True
                    },
                    {
                        "name": "🎯 Target Block",
                        "value": f"{blockchain['headers']:,}",
                        "inline": True
                    },
                    {
                        "name": "💾 Disk Usage",
                        "value": format_bytes(blockchain['size_on_disk']),
                        "inline": True
                    },
                ],
                color=0x3B82F6
            )
            
            state["last_sync_milestone"] = milestone
            save_state(state)
            break


def monitor_loop() -> None:
    """Main monitoring loop"""
    log("=" * 60)
    log("🚀 Curtis BTC Watcher Starting...")
    log("=" * 60)
    log(f"Bitcoin RPC: {BTC_RPC_HOST}:{BTC_RPC_PORT}")
    log(f"Poll Interval: {POLL_SECONDS} seconds")
    log(f"Notify Blocks: {NOTIFY_BLOCKS}")
    log(f"Notify ATH: {NOTIFY_ATH}")
    log("=" * 60)
    
    state = load_state()
    consecutive_errors = 0
    max_errors = 5
    
    while True:
        try:
            # Get blockchain info
            blockchain = get_blockchain_info()
            
            if blockchain:
                consecutive_errors = 0
                
                # Check for new blocks
                check_new_block(blockchain, state)
                
                # Check sync milestones
                if blockchain["initial_block_download"]:
                    check_sync_milestone(blockchain, state)
                
                # Log status periodically
                if int(time.time()) % 300 < POLL_SECONDS:  # Every 5 minutes
                    network = get_network_info()
                    log(
                        f"Status: Block {blockchain['blocks']:,}/{blockchain['headers']:,} "
                        f"({blockchain['sync_progress']:.2f}%) | "
                        f"Connections: {network['connections'] if network else 0} | "
                        f"Disk: {format_bytes(blockchain['size_on_disk'])}"
                    )
            else:
                consecutive_errors += 1
                log(f"⚠️ Failed to get blockchain info (attempt {consecutive_errors}/{max_errors})")
                
                if consecutive_errors >= max_errors:
                    log("❌ Too many consecutive errors, sending alert...")
                    send_discord_notification(
                        title="⚠️ Bitcoin Node Connection Issue",
                        description="Failed to connect to Bitcoin node after multiple attempts.",
                        fields=[
                            {
                                "name": "RPC Host",
                                "value": f"{BTC_RPC_HOST}:{BTC_RPC_PORT}",
                                "inline": True
                            },
                            {
                                "name": "Consecutive Errors",
                                "value": str(consecutive_errors),
                                "inline": True
                            },
                        ],
                        color=0xEF4444
                    )
                    consecutive_errors = 0  # Reset to avoid spam
            
        except KeyboardInterrupt:
            log("🛑 Shutting down watcher...")
            break
        except Exception as e:
            log(f"❌ Unexpected error in monitor loop: {e}")
            consecutive_errors += 1
        
        # Wait for next poll
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    monitor_loop()
