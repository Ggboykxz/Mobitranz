#!/bin/bash
# MobiTranz Desktop Admin Launcher

cd /workspaces/Mobitranz

export ADMIN_USERNAME="${ADMIN_USERNAME:-admin}"
export ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin123}"
export API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"

echo "🚀 Starting MobiTranz Admin Desktop..."
echo "   Admin: $ADMIN_USERNAME"
echo "   API:   $API_BASE_URL"

python -m desktop_admin.main