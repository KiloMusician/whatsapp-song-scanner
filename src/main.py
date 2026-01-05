"""Main application entry point."""
from flask import Flask, request, jsonify
from flask_cors import CORS
from config.database import SessionLocal
from config.settings import APP_CONFIG
from src.whatsapp.message_handler import message_handler
from src.database.operations import RequestOperations
from src.core.scheduler import scheduler
from src.core.health_check import health_check
from src.core.state_manager import state_manager
from src.utils.logger import get_logger

logger = get_logger(__name__)

# CREATE FLASK APP
app = Flask(__name__)
CORS(app)

# HEALTH CHECK ENDPOINT
@app.route('/api/v1/health', methods=['GET'])
def get_health():
    """Health check endpoint."""
    try:
        health_status = health_check.get_health()
        status_code = 200 if health_status['status'] in ['healthy', 'degraded'] else 503
        return jsonify(health_status), status_code
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# METRICS ENDPOINT
@app.route('/api/v1/metrics', methods=['GET'])
def get_metrics():
    """Metrics endpoint."""
    try:
        metrics = health_check.get_metrics()
        return jsonify(metrics), 200
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        return jsonify({'error': str(e)}), 500

# TWILIO WEBHOOK ENDPOINT
@app.route('/api/v1/webhook/twilio', methods=['POST'])
def twilio_webhook():
    """Handle incoming Twilio webhook."""
    try:
        webhook_data = request.form.to_dict()
        logger.info(f"Received Twilio webhook: {webhook_data.get('From')}")
        
        db = SessionLocal()
        try:
            success = message_handler.handle_twilio_webhook(db, webhook_data)
            if success:
                return jsonify({'status': 'success'}), 200
            else:
                return jsonify({'status': 'error'}), 500
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

# EVOLUTION API WEBHOOK ENDPOINT
@app.route('/api/v1/webhook/evolution', methods=['POST'])
def evolution_webhook():
    """Handle incoming Evolution API webhook."""
    try:
        message_data = request.get_json()
        logger.info(f"Received Evolution webhook")
        
        db = SessionLocal()
        try:
            success = message_handler.handle_evolution_message(db, message_data)
            if success:
                return jsonify({'status': 'success'}), 200
            else:
                return jsonify({'status': 'error'}), 500
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

# GET PENDING REQUESTS
@app.route('/api/v1/requests/pending', methods=['GET'])
def get_pending_requests():
    """Get pending song requests."""
    try:
        limit = int(request.args.get('limit', 50))
        
        db = SessionLocal()
        try:
            requests_list = RequestOperations.get_pending_requests(db, limit)
            
            results = []
            for req in requests_list:
                results.append({
                    'id': req.id,
                    'chat_id': req.chat_id,
                    'requested_by': req.requested_by,
                    'song_title': req.matched_song.song_title,
                    'artist_name': req.matched_song.artist_name,
                    'status': req.status,
                    'priority': req.request_priority,
                    'created_at': req.created_at.isoformat()
                })
            
            return jsonify({'requests': results, 'count': len(results)}), 200
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error getting pending requests: {e}")
        return jsonify({'error': str(e)}), 500

# APPROVE REQUEST
@app.route('/api/v1/requests/approve', methods=['POST'])
def approve_request():
    """Approve a song request."""
    try:
        data = request.get_json()
        request_id = data.get('request_id')
        
        if not request_id:
            return jsonify({'error': 'request_id required'}), 400
        
        db = SessionLocal()
        try:
            RequestOperations.approve_request(db, request_id)
            return jsonify({'status': 'approved'}), 200
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error approving request: {e}")
        return jsonify({'error': str(e)}), 500

# REJECT REQUEST
@app.route('/api/v1/requests/reject', methods=['POST'])
def reject_request():
    """Reject a song request."""
    try:
        data = request.get_json()
        request_id = data.get('request_id')
        notes = data.get('notes')
        
        if not request_id:
            return jsonify({'error': 'request_id required'}), 400
        
        db = SessionLocal()
        try:
            RequestOperations.reject_request(db, request_id, notes)
            return jsonify({'status': 'rejected'}), 200
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error rejecting request: {e}")
        return jsonify({'error': str(e)}), 500

# SCAN STATUS
@app.route('/api/v1/scan/status', methods=['GET'])
def scan_status():
    """Get scan status."""
    try:
        state = state_manager.get_state()
        return jsonify({
            'status': state['status'],
            'last_scan': state['last_scan'].isoformat() if state['last_scan'] else None,
            'stats': state['stats']
        }), 200
    except Exception as e:
        logger.error(f"Error getting scan status: {e}")
        return jsonify({'error': str(e)}), 500

def initialize_app():
    """Initialize application."""
    logger.info("Initializing WhatsApp Song Scanner...")
    
    # Initialize database
    from src.database.models import init_database
    try:
        init_database()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database may already be initialized: {e}")
    
    # Start scheduler
    scheduler.start()
    
    logger.info("Application initialized successfully")

def main():
    """Run the application."""
    initialize_app()
    
    logger.info(f"Starting Flask server on {APP_CONFIG['host']}:{APP_CONFIG['port']}")
    app.run(
        host=APP_CONFIG['host'],
        port=APP_CONFIG['port'],
        debug=APP_CONFIG['debug']
    )

if __name__ == '__main__':
    main()
