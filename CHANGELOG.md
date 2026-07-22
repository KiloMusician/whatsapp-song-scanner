# Changelog

All notable changes to the **Telegram Song Scanner** project will be documented in this file.

**Note: WhatsApp integration has been deprecated in favor of Telegram.**

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-05

### Added
- Initial release of **Telegram Song Scanner Bot**
- **Telegram integration** with support for bot-based messaging
- **WhatsApp integration deprecated** - migrated to Telegram
- Text processing pipeline for song request extraction
- MusicBrainz integration with intelligent fuzzy matching
- Complete MariaDB database schema with 5 core tables
- RadioDJ integration for automated playlist management
- RESTful API with health checks and monitoring endpoints
- Background task scheduler for automated scanning
- Redis-based caching system
- Rate limiting for API calls
- Comprehensive logging system
- Docker deployment configuration
- Database migration support with Alembic
- Setup and maintenance scripts
- Unit and integration tests
- Complete documentation

### Features
- **WhatsApp Integration**
  - Twilio WhatsApp Business API support
  - Evolution API support for self-hosted WhatsApp
  - Webhook-based and polling-based message ingestion
  - Multi-chat support

- **Song Matching**
  - MusicBrainz API integration
  - Fuzzy string matching with confidence scoring
  - Multi-pattern message parsing
  - Automatic match validation
  - Fallback API support (Spotify, Deezer)

- **Database**
  - Complete MariaDB schema
  - Automatic table creation
  - Migration support
  - CRUD operations
  - Analytics and reporting views

- **RadioDJ Integration**
  - API-based integration (preferred)
  - Direct database access (fallback)
  - Safety checks and validation
  - Automatic backup before modifications

- **Monitoring**
  - Health check endpoints
  - Application metrics
  - Prometheus integration (optional)
  - Grafana dashboards (optional)
  - Comprehensive logging

### Infrastructure
- Docker Compose setup with all services
- MariaDB with optimized configuration
- Redis for caching and queues
- Evolution API for WhatsApp (optional)
- Automated database backups
- Log rotation
- Cache cleanup

### Documentation
- Complete README with quick start guide
- API documentation
- Architecture overview
- Setup instructions
- Troubleshooting guide
- Maintenance procedures

### Security
- Environment-based configuration
- Webhook signature validation
- Rate limiting
- Input sanitization
- Secure database connections

## [Unreleased]

### Planned
- Advanced analytics dashboard
- Machine learning for song matching improvement
- Multi-language support
- Voice message support
- Custom playlist scheduling
- Web UI for management
- Mobile app integration
- Advanced reporting features
