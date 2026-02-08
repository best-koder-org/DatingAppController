#!/bin/bash
# Overnight Task Execution - Main Entry Point
# Creates snapshot and launches task processor

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  OVERNIGHT TASK AUTOMATION                                 ║${NC}"
echo -e "${BLUE}║  DatingApp Controller - Multi-Repo Orchestration           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Pre-flight checks
echo -e "${YELLOW}📋 Running pre-flight checks...${NC}"
if [ ! -f "$SCRIPT_DIR/.ai-workspace/task-queue.json" ]; then
    echo -e "${RED}❌ Task queue not found!${NC}"
    exit 1
fi

TASK_COUNT=$(jq '.queue | length' "$SCRIPT_DIR/.ai-workspace/task-queue.json")
if [ "$TASK_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  No tasks in queue. Nothing to do.${NC}"
    exit 0
fi

echo -e "${GREEN}✅ Found $TASK_COUNT tasks in queue${NC}"
echo ""

# Step 2: Create safety snapshot
echo -e "${YELLOW}📸 Creating safety snapshot...${NC}"
SNAPSHOT_NAME="Before overnight run - $(date '+%b %d %Y %H:%M')"
"$SCRIPT_DIR/scripts/snapshot.sh" "$SNAPSHOT_NAME"
echo ""

# Step 3: Show what will be executed
echo -e "${YELLOW}📝 Tasks queued for execution:${NC}"
jq -r '.queue[] | "  ✓ [\(.id)] \(.title) (\(.estimatedHours)h)"' "$SCRIPT_DIR/.ai-workspace/task-queue.json"
echo ""

# Step 4: Provide rollback instructions
echo -e "${BLUE}💡 If anything goes wrong, rollback with:${NC}"
echo "   cd $SCRIPT_DIR && ./scripts/rollback.sh \"$SNAPSHOT_NAME\""
echo ""

# Step 5: Launch task processor
echo -e "${GREEN}🚀 Ready to launch automation engine!${NC}"
echo ""

"$SCRIPT_DIR/scripts/execute-task-queue.sh"

echo ""
echo -e "${GREEN}✅ PRE-FLIGHT CHECK COMPLETE!${NC}"
echo -e "${GREEN}Task processor has been activated.${NC}"
