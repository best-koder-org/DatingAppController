#!/bin/bash
set -e

echo "🚀 Starting OpenHands..."

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not set!"
    echo "Please run: export ANTHROPIC_API_KEY='your-key'"
    exit 1
fi

# Pull runtime image if needed
echo "📦 Checking runtime image..."
docker pull ghcr.io/openhands/runtime:latest 2>/dev/null || true

# Start OpenHands
echo "🌐 Starting OpenHands GUI on http://localhost:3000"
echo "📁 Workspace: /home/m/development/DatingAppController"
echo ""
echo "Once it opens, give it this task:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Read .ai-workspace/task-queue.json and implement the next"
echo "onboarding screen (ONB-060). Create a feature branch,"
echo "generate the Flutter code in repos/mobile_dejtingapp/,"
echo "run flutter analyze, commit, and create a PR."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

docker run -it --rm \
    --pull=always \
    -e SANDBOX_RUNTIME_CONTAINER_IMAGE=ghcr.io/openhands/runtime:latest \
    -e LOG_ALL_EVENTS=true \
    -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /home/m/development/DatingAppController:/workspace \
    -p 3000:3000 \
    --add-host=host.docker.internal:host-gateway \
    --name openhands \
    ghcr.io/openhands/openhands:latest
