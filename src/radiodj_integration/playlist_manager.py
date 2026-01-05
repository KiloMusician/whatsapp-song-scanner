"""Manage RadioDJ playlists."""
from typing import List, Dict, Optional
from src.radiodj_integration.radiodj_client import radiodj_client
from src.utils.logger import get_logger

logger = get_logger(__name__)

class PlaylistManager:
    """Manage RadioDJ playlists."""
    
    def __init__(self):
        """Initialize playlist manager."""
        self.client = radiodj_client
    
    def add_song_to_playlist(
        self,
        artist: str,
        title: str,
        playlist_id: int = None,
        use_api: bool = True
    ) -> Optional[int]:
        """Add song to RadioDJ playlist.
        
        Args:
            artist: Artist name
            title: Song title
            playlist_id: Playlist ID (optional)
            use_api: Use API if True, database if False
            
        Returns:
            Track ID if successful, None otherwise
        """
        logger.info(f"Adding to playlist: {artist} - {title}")
        
        if use_api:
            # TRY API FIRST
            success = self.client.add_track_via_api(artist, title, playlist_id)
            if success:
                logger.info("Successfully added via API")
                return -1  # API doesn't return track ID
        
        # FALLBACK TO DATABASE METHOD
        logger.info("Attempting database method...")
        
        # Find track in library
        track_id = self.client.find_track_in_library(artist, title)
        if not track_id:
            logger.warning("Track not found in RadioDJ library")
            return None
        
        # Add to queue
        success = self.client.add_track_to_queue_db(track_id)
        if success:
            logger.info(f"Successfully added track {track_id} to queue")
            return track_id
        
        return None
    
    def bulk_add_songs(
        self,
        songs: List[Dict],
        playlist_id: int = None
    ) -> Dict[str, int]:
        """Add multiple songs to playlist.
        
        Args:
            songs: List of song dictionaries with 'artist' and 'title'
            playlist_id: Playlist ID (optional)
            
        Returns:
            Dictionary with success/failure counts
        """
        results = {
            'success': 0,
            'failed': 0,
            'not_found': 0
        }
        
        for song in songs:
            artist = song.get('artist', '')
            title = song.get('title', '')
            
            if not artist or not title:
                results['failed'] += 1
                continue
            
            track_id = self.add_song_to_playlist(artist, title, playlist_id)
            
            if track_id:
                results['success'] += 1
            elif track_id is None:
                results['not_found'] += 1
            else:
                results['failed'] += 1
        
        logger.info(f"Bulk add results: {results}")
        return results

# SINGLETON INSTANCE
playlist_manager = PlaylistManager()
