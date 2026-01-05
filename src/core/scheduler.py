"""Task scheduling and management."""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from config.database import SessionLocal
from config.settings import WHATSAPP_CONFIG
from src.whatsapp.chat_scanner import chat_scanner
from src.radiodj_integration.sync_service import sync_service
from src.core.state_manager import state_manager
from src.utils.logger import get_logger

logger = get_logger(__name__)

class Scheduler:
    """Application task scheduler."""
    
    def __init__(self):
        """Initialize scheduler."""
        self.scheduler = BackgroundScheduler()
        self.scan_interval = WHATSAPP_CONFIG['scan_interval_minutes']
        logger.info("Scheduler initialized")
    
    def start(self):
        """Start all scheduled tasks."""
        logger.info("Starting scheduler...")
        
        # Schedule chat scanning
        self.scheduler.add_job(
            func=self._scan_chats_job,
            trigger=IntervalTrigger(minutes=self.scan_interval),
            id='scan_chats',
            name='Scan WhatsApp chats',
            replace_existing=True
        )
        
        # Schedule RadioDJ sync
        self.scheduler.add_job(
            func=self._sync_radiodj_job,
            trigger=IntervalTrigger(minutes=2),
            id='sync_radiodj',
            name='Sync to RadioDJ',
            replace_existing=True
        )
        
        self.scheduler.start()
        state_manager.set_status('running')
        logger.info("Scheduler started")
    
    def stop(self):
        """Stop scheduler."""
        logger.info("Stopping scheduler...")
        self.scheduler.shutdown()
        state_manager.set_status('stopped')
        logger.info("Scheduler stopped")
    
    def _scan_chats_job(self):
        """Job to scan WhatsApp chats."""
        logger.info("Running scheduled chat scan")
        db = SessionLocal()
        try:
            results = chat_scanner.scan_all_active_chats(db)
            total_processed = sum(results.values())
            state_manager.increment_stat('messages_processed', total_processed)
            state_manager.update_last_scan()
            logger.info(f"Scheduled scan completed: {total_processed} messages")
        except Exception as e:
            logger.error(f"Error in scan job: {e}")
        finally:
            db.close()
    
    def _sync_radiodj_job(self):
        """Job to sync to RadioDJ."""
        logger.info("Running scheduled RadioDJ sync")
        db = SessionLocal()
        try:
            stats = sync_service.sync_approved_requests(db)
            state_manager.increment_stat('requests_synced', stats['synced'])
            state_manager.update_last_sync()
            logger.info(f"Scheduled sync completed: {stats}")
        except Exception as e:
            logger.error(f"Error in sync job: {e}")
        finally:
            db.close()

# SINGLETON INSTANCE
scheduler = Scheduler()
