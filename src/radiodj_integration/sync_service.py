"""Sync MariaDB song requests with RadioDJ."""
from typing import Dict
from sqlalchemy.orm import Session
from src.database.operations import RequestOperations
from src.radiodj_integration.playlist_manager import playlist_manager
from src.utils.logger import get_logger

logger = get_logger(__name__)

class SyncService:
    """Sync song requests to RadioDJ."""
    
    def __init__(self):
        """Initialize sync service."""
        self.playlist_manager = playlist_manager
    
    def sync_approved_requests(self, db: Session, limit: int = 50) -> Dict[str, int]:
        """Sync approved requests to RadioDJ.
        
        Args:
            db: Database session
            limit: Maximum requests to process
            
        Returns:
            Dictionary with sync statistics
        """
        logger.info("Starting sync of approved requests to RadioDJ")
        
        # Get pending approved requests
        requests = RequestOperations.get_pending_requests(db, limit)
        
        # Filter for approved status
        approved_requests = [r for r in requests if r.status == 'approved']
        
        if not approved_requests:
            logger.info("No approved requests to sync")
            return {'synced': 0, 'failed': 0}
        
        stats = {'synced': 0, 'failed': 0}
        
        for request in approved_requests:
            try:
                # Get matched song details
                matched_song = request.matched_song
                
                artist = matched_song.artist_name or 'Unknown'
                title = matched_song.song_title
                
                # Add to RadioDJ
                track_id = self.playlist_manager.add_song_to_playlist(
                    artist=artist,
                    title=title,
                    use_api=True
                )
                
                if track_id is not None:
                    # Mark as queued
                    RequestOperations.mark_queued(db, request.id, track_id if track_id > 0 else None)
                    stats['synced'] += 1
                    logger.info(f"Synced request {request.id}: {artist} - {title}")
                else:
                    stats['failed'] += 1
                    logger.warning(f"Failed to sync request {request.id}: {artist} - {title}")
                    
            except Exception as e:
                logger.error(f"Error syncing request {request.id}: {e}")
                stats['failed'] += 1
                continue
        
        logger.info(f"Sync completed: {stats}")
        return stats
    
    def run_continuous_sync(self, db: Session, interval_seconds: int = 60):
        """Run continuous sync (for scheduler).
        
        Args:
            db: Database session
            interval_seconds: Sync interval
        """
        import time
        
        logger.info(f"Starting continuous sync with {interval_seconds}s interval")
        
        while True:
            try:
                self.sync_approved_requests(db)
                time.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Error in continuous sync: {e}")
                time.sleep(interval_seconds)

# SINGLETON INSTANCE
sync_service = SyncService()
