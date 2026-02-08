#!/bin/bash

echo "🔍 OpenHands Setup Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Docker
if docker --version &>/dev/null; then
    echo "✅ Docker installed: $(docker --version | cut -d' ' -f3)"
else
    echo "❌ Docker not found"
    exit 1
fi

# Check OpenHands image
if docker images | grep -q "openhands/openhands"; then
    SIZE=$(docker images ghcr.io/openhands/openhands:latest --format "{{.Size}}")
    echo "✅ OpenHands image ready: $SIZE"
else
    echo "❌ OpenHands image not found"
    exit 1
fi

# Check API key
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "✅ ANTHROPIC_API_KEY set (${ANTHROPIC_API_KEY:0:10}...)"
else
    echo "⚠️  ANTHROPIC_API_KEY not set"
    echo "   Run: export ANTHROPIC_API_KEY='sk-ant-...'"
    echo ""
fi

# Check task queue
if [ -f .ai-workspace/task-queue.json ]; then
    NEXT_TASK=$(jq -r '.queue[0].title' .ai-workspace/task-queue.json 2>/dev/null || echo "Error")
    if [ "$NEXT_TASK" != "Error" ]; then
        echo "✅ Task queue ready: $NEXT_TASK"
    else
        echo "⚠️  Task queue has errors"
    fi
else
    echo "❌ Task queue not found"
fi

# Check workspace
if [ -d repos/mobile_dejtingapp ]; then
    echo "✅ Mobile app repo ready"
else
    echo "❌ Mobile app repo not found"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "🚀 READY TO LAUNCH!"
    echo ""
    echo "Run: ./start-openhands.sh"
else
    echo "⚠️  SET API KEY FIRST:"
    echo ""
    echo "export ANTHROPIC_API_KEY='your-key'"
    echo "./start-openhands.sh"
fi
