# API Documentation

## Overview

The Telegram Song Scanner API provides endpoints for health checks, metrics, and webhook integration with Telegram bots.

**Note: WhatsApp integration is deprecated. The project now uses Telegram for all messaging functionality.**

## Base URL

```
http://localhost:5000/api/v1
```

## Authentication

Currently, the API is open. In production, consider adding:
- API key authentication
- Bearer token validation
- Rate limiting per endpoint

## Endpoints

### Health & Status

#### Health Check
Returns basic health status of the application.

**Request:**
```
GET /health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-05T12:00:00Z",
  "version": "1.0.0"
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "unhealthy",
  "errors": ["Database connection failed"]
}
```

---

#### Application Metrics
Returns current application statistics and state.

**Request:**
```
GET /metrics
```

**Response (200 OK):**
```json
{
  "status": "running",
  "uptime_seconds": 3600,
  "started_at": "2024-01-05T10:00:00Z",
  "last_scan": "2024-01-05T11:55:00Z",
  "last_sync": "2024-01-05T11:58:00Z",
  "statistics": {
    "messages_processed": 142,
    "songs_matched": 38,
    "requests_created": 28,
    "requests_synced": 15
  }
}
```

---

#### Scan Status
Get status of the last chat scan.

**Request:**
```
GET /status
```

**Response (200 OK):**
```json
{
  "status": "running",
  "uptime_seconds": 3600,
  "started_at": "2024-01-05T10:00:00Z",
  "last_scan": "2024-01-05T11:55:00Z",
  "last_sync": "2024-01-05T11:58:00Z"
}
```

---

### Webhooks

#### Twilio WhatsApp Messages
Receive incoming messages from Twilio WhatsApp API.

**Request:**
```
POST /webhook/twilio
Content-Type: application/x-www-form-urlencoded
```

**Body Parameters:**
```
SmsStatus=received
From=whatsapp:+1234567890
To=whatsapp:+0987654321
MessageSid=SM1234567890abcdef1234567890abcdef
AccountSid=AC1234567890abcdef1234567890abcdef
MessagingServiceSid=MG1234567890abcdef1234567890abcdef
Body=play+thriller+by+michael+jackson
NumMedia=0
```

**Response (200 OK):**
```json
{
  "status": "received",
  "message_id": "SM1234567890abcdef1234567890abcdef",
  "sender": "whatsapp:+1234567890"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Invalid webhook signature",
  "details": "Twilio signature validation failed"
}
```

---

#### Evolution API WhatsApp Messages
Receive incoming messages from Evolution API.

**Request:**
```
POST /webhook/evolution
Content-Type: application/json
Authorization: Bearer <api_key>
```

**Body:**
```json
{
  "data": {
    "key": {
      "remoteJid": "1234567890@s.whatsapp.net",
      "fromMe": false,
      "id": "3A40C9E1234567890"
    },
    "pushName": "John Doe",
    "message": {
      "conversation": "play thriller by michael jackson"
    },
    "messageTimestamp": 1704448800
  },
  "serverUrl": "https://evolution-api.example.com"
}
```

**Response (200 OK):**
```json
{
  "status": "processed",
  "message_id": "3A40C9E1234567890",
  "sender": "1234567890@s.whatsapp.net"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": "Invalid API key",
  "details": "Authorization header missing or invalid"
}
```

---

## Webhook Integration

### Setting up Webhooks

#### For Twilio

1. Go to Twilio Console → WhatsApp Sandbox
2. Set webhook URL to: `https://your-domain.com/api/v1/webhook/twilio`
3. Select event: "Incoming Messages"
4. The system will validate webhook with Twilio signature

#### For Evolution API

1. Configure in Evolution API dashboard
2. Webhook URL: `https://your-domain.com/api/v1/webhook/evolution`
3. Add API key to header: `Authorization: Bearer <your_key>`

### Webhook Retry Logic

- **Timeout**: 30 seconds
- **Retries**: 3 attempts with exponential backoff
- **Backoff**: 2s, 4s, 6s between attempts

---

## Rate Limiting

**Current**: No rate limiting (implement in production)

**Recommended**:
```
- 100 requests per minute per IP
- 1000 requests per hour per API key
- Webhook endpoints: 50 messages per minute
```

---

## Error Codes

| Code | Error | Description |
|------|-------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid parameters or malformed request |
| 401 | Unauthorized | Missing or invalid API key |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

---

## Response Format

### Success Response

```json
{
  "status": "success",
  "data": { /* endpoint-specific data */ },
  "timestamp": "2024-01-05T12:00:00Z"
}
```

### Error Response

```json
{
  "error": "Error Type",
  "message": "Detailed error message",
  "code": "ERROR_CODE",
  "timestamp": "2024-01-05T12:00:00Z"
}
```

---

## Examples

### cURL Examples

**Health Check:**
```bash
curl http://localhost:5000/api/v1/health
```

**Get Metrics:**
```bash
curl http://localhost:5000/api/v1/metrics
```

**Send Twilio Message (simulated):**
```bash
curl -X POST http://localhost:5000/api/v1/webhook/twilio \
  -d "From=whatsapp:%2B1234567890&Body=play+thriller+by+michael+jackson"
```

**Send Evolution Message:**
```bash
curl -X POST http://localhost:5000/api/v1/webhook/evolution \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "message": {
        "conversation": "play thriller by michael jackson"
      }
    }
  }'
```

### Python Examples

**Using requests library:**
```python
import requests

# Health check
response = requests.get('http://localhost:5000/api/v1/health')
print(response.json())

# Get metrics
response = requests.get('http://localhost:5000/api/v1/metrics')
print(response.json())
```

---

## Changelog

### v1.0.0 (Current)
- Initial release
- Health checks
- Metrics endpoint
- Twilio webhook support
- Evolution API webhook support

---

## Support

For issues or questions:
1. Check [troubleshooting guide](README.md#-troubleshooting)
2. Review [project issues](https://github.com/KiloMusician/whatsapp-song-scanner/issues)
3. Check application logs in Docker container

