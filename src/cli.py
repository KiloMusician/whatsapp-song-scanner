"""Command-line interface for WhatsApp Song Scanner."""

import click
from datetime import datetime
from config.database import SessionLocal
from config.settings import WHATSAPP_CONFIG
from src.whatsapp.chat_scanner import chat_scanner
from src.radiodj_integration.sync_service import sync_service
from src.database.operations import ChatOperations, RequestOperations
from src.core.state_manager import state_manager
from src.utils.logger import get_logger

logger = get_logger(__name__)


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """WhatsApp Song Scanner CLI - Manage song requests from WhatsApp to RadioDJ."""
    pass


@cli.command()
@click.option(
    "--chat-id",
    required=False,
    help="Specific chat ID to scan (optional)",
)
def scan(chat_id):
    """Scan WhatsApp chats for song requests.
    
    Examples:
        python -m src.cli scan                    # Scan all active chats
        python -m src.cli scan --chat-id=<id>    # Scan specific chat
    """
    db = SessionLocal()
    try:
        if chat_id:
            click.echo(f"Scanning chat: {chat_id}")
            results = chat_scanner.scan_chat(db, chat_id)
            click.echo(f"✓ Scan completed: {results} messages processed")
        else:
            click.echo("Scanning all active chats...")
            results = chat_scanner.scan_all_active_chats(db)
            total = sum(results.values())
            click.echo(f"✓ Scan completed: {total} total messages processed")
            for chat_name, count in results.items():
                click.echo(f"  - {chat_name}: {count} messages")
        state_manager.update_last_scan()
    except Exception as e:
        click.echo(f"✗ Error during scan: {e}", err=True)
        logger.error("Scan error: %s", e)
    finally:
        db.close()


@cli.command()
@click.option(
    "--limit",
    default=50,
    type=int,
    help="Maximum requests to sync",
)
def sync(limit):
    """Sync approved song requests to RadioDJ.
    
    Examples:
        python -m src.cli sync              # Sync up to 50 requests
        python -m src.cli sync --limit=10   # Sync up to 10 requests
    """
    db = SessionLocal()
    try:
        click.echo(f"Syncing approved requests (limit: {limit})...")
        stats = sync_service.sync_approved_requests(db, limit)
        click.echo(f"✓ Sync completed:")
        click.echo(f"  - Synced: {stats['synced']}")
        click.echo(f"  - Failed: {stats['failed']}")
        state_manager.update_last_sync()
    except Exception as e:
        click.echo(f"✗ Error during sync: {e}", err=True)
        logger.error("Sync error: %s", e)
    finally:
        db.close()


@cli.command()
def status():
    """Show current application status.
    
    Examples:
        python -m src.cli status
    """
    state = state_manager.get_state()
    uptime = state_manager.get_uptime_seconds()
    
    click.echo("\n" + "=" * 50)
    click.echo("WhatsApp Song Scanner Status")
    click.echo("=" * 50)
    click.echo(f"Status: {state.get('status', 'unknown')}")
    click.echo(f"Uptime: {uptime:.0f} seconds")
    click.echo(f"Started: {state.get('started_at', 'unknown')}")
    click.echo(f"Last scan: {state.get('last_scan', 'never')}")
    click.echo(f"Last sync: {state.get('last_sync', 'never')}")
    click.echo("\nStatistics:")
    stats = state.get("stats", {})
    for stat_name, value in stats.items():
        click.echo(f"  - {stat_name}: {value}")
    click.echo("=" * 50 + "\n")


@cli.command()
def list_chats():
    """List all active WhatsApp chats.
    
    Examples:
        python -m src.cli list-chats
    """
    db = SessionLocal()
    try:
        chats = ChatOperations.get_active_chats(db)
        if not chats:
            click.echo("No active chats found.")
            return
        
        click.echo(f"\nActive chats ({len(chats)}):")
        click.echo("-" * 60)
        for chat in chats:
            click.echo(f"  ID: {chat.chat_id}")
            click.echo(f"  Name: {chat.chat_name or 'Unknown'}")
            click.echo(f"  Last scan: {chat.last_scan_time or 'Never'}")
            click.echo()
    except Exception as e:
        click.echo(f"✗ Error listing chats: {e}", err=True)
        logger.error("List chats error: %s", e)
    finally:
        db.close()


@cli.command()
@click.option("--limit", default=10, type=int, help="Maximum requests to display")
def list_requests(limit):
    """List pending song requests.
    
    Examples:
        python -m src.cli list-requests              # Show 10 pending requests
        python -m src.cli list-requests --limit=20   # Show 20 pending requests
    """
    db = SessionLocal()
    try:
        requests = RequestOperations.get_pending_requests(db, limit)
        if not requests:
            click.echo("No pending requests found.")
            return
        
        click.echo(f"\nPending requests ({len(requests)}):")
        click.echo("-" * 80)
        for req in requests:
            matched = req.matched_song
            artist = matched.artist_name if matched else "Unknown"
            title = matched.song_title if matched else "Unknown"
            click.echo(f"  ID: {req.id}")
            click.echo(f"  Song: {artist} - {title}")
            click.echo(f"  Requested by: {req.requested_by or 'Anonymous'}")
            click.echo(f"  Status: {req.status}")
            click.echo(f"  Created: {req.created_at}")
            click.echo()
    except Exception as e:
        click.echo(f"✗ Error listing requests: {e}", err=True)
        logger.error("List requests error: %s", e)
    finally:
        db.close()


@cli.command()
@click.argument("request_id", type=int)
def approve(request_id):
    """Approve a song request.
    
    Examples:
        python -m src.cli approve 5
    """
    db = SessionLocal()
    try:
        request = db.query(RequestOperations.__class__).get(request_id)
        if not request:
            click.echo(f"✗ Request {request_id} not found.", err=True)
            return
        
        RequestOperations.approve_request(db, request_id)
        click.echo(f"✓ Request {request_id} approved.")
    except Exception as e:
        click.echo(f"✗ Error approving request: {e}", err=True)
        logger.error("Approve request error: %s", e)
    finally:
        db.close()


@cli.command()
@click.argument("request_id", type=int)
@click.option("--notes", default="", help="Rejection notes")
def reject(request_id, notes):
    """Reject a song request.
    
    Examples:
        python -m src.cli reject 5
        python -m src.cli reject 5 --notes="Not available"
    """
    db = SessionLocal()
    try:
        RequestOperations.reject_request(db, request_id, notes)
        click.echo(f"✓ Request {request_id} rejected.")
    except Exception as e:
        click.echo(f"✗ Error rejecting request: {e}", err=True)
        logger.error("Reject request error: %s", e)
    finally:
        db.close()


if __name__ == "__main__":
    cli()
