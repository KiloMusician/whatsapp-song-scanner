#!/bin/bash
# Configure environment for WhatsApp Song Scanner

set -e

echo "Configuring environment..."

# CHECK IF .env EXISTS
if [ -f .env ]; then
    echo "Warning: .env already exists. Backing up to .env.backup"
    cp .env .env.backup
fi

# COPY .env.example TO .env
cp .env.example .env

echo ""
echo "✅ Environment configuration created!"
echo ""
echo "Important: Edit .env file and configure the following:"
echo ""
echo "  1. WhatsApp Provider Settings:"
echo "     - Choose 'twilio' or 'evolution' as WHATSAPP_PROVIDER"
echo "     - For Twilio: Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER"
echo "     - For Evolution: Set EVOLUTION_API_URL and EVOLUTION_API_KEY"
echo ""
echo "  2. Database Settings:"
echo "     - Set MARIADB_PASSWORD (required)"
echo "     - Optionally customize MARIADB_HOST, MARIADB_PORT, MARIADB_DATABASE"
echo ""
echo "  3. Optional Services:"
echo "     - MusicBrainz settings (user agent)"
echo "     - Spotify/Deezer API credentials (for fallback matching)"
echo "     - RadioDJ API settings"
echo ""
echo "After configuring .env, run:"
echo "  ./scripts/setup/install_dependencies.sh"
echo "  ./scripts/setup/setup_database.sh"
