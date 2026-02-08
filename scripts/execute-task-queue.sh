#!/bin/bash
# Task Queue Execution Engine
# Processes tasks from .ai-workspace/task-queue.json autonomously

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TASK_QUEUE="$PROJECT_ROOT/.ai-workspace/task-queue.json"
EXECUTION_LOG="$PROJECT_ROOT/.ai-workspace/execution.log"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$EXECUTION_LOG"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "[ERROR] $1" >> "$EXECUTION_LOG"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    echo "[SUCCESS] $1" >> "$EXECUTION_LOG"
}

# Initialize execution log
echo "=== Task Queue Execution Started: $(date) ===" > "$EXECUTION_LOG"

# Check if task queue exists
if [ ! -f "$TASK_QUEUE" ]; then
    error "Task queue not found at $TASK_QUEUE"
    exit 1
fi

# Count tasks
QUEUE_COUNT=$(jq '.queue | length' "$TASK_QUEUE")

log "Found $QUEUE_COUNT tasks in queue"

if [ "$QUEUE_COUNT" -eq 0 ]; then
    success "No tasks in queue. Nothing to do!"
    exit 0
fi

# Show queued tasks
echo ""
echo -e "${YELLOW}📋 QUEUED TASKS:${NC}"
jq -r '.queue[] | "  ✓ [\(.id)] \(.title) (\(.estimatedHours)h)"' "$TASK_QUEUE"
echo ""

# Ask for confirmation
read -p "Execute all $QUEUE_COUNT tasks? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log "Execution cancelled by user"
    exit 0
fi

# Create automation marker file for AI to detect
echo "AUTOMATION_MODE=true" > "$PROJECT_ROOT/.ai-workspace/automation-active.txt"
echo "START_TIME=$(date -Iseconds)" >> "$PROJECT_ROOT/.ai-workspace/automation-active.txt"

success "Automation mode activated!"
echo ""
echo -e "${YELLOW}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║  AI AUTOMATION MODE                                        ║${NC}"
echo -e "${YELLOW}║                                                            ║${NC}"
echo -e "${YELLOW}║  The AI will now process each task autonomously.          ║${NC}"
echo -e "${YELLOW}║  Progress will be logged to execution.log                 ║${NC}"
echo -e "${YELLOW}║                                                            ║${NC}"
echo -e "${YELLOW}║  Current tasks: $QUEUE_COUNT                                          ║${NC}"
echo -e "${YELLOW}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Export task queue path for AI to read
export TASK_QUEUE_PATH="$TASK_QUEUE"
export AUTOMATION_MODE="true"

log "Task queue location: $TASK_QUEUE"
log "Working directory: $PROJECT_ROOT/repos/mobile_dejtingapp"
log "Execution log: $EXECUTION_LOG"
log ""
log "🤖 AI: Please process the task queue now!"
log "   1. Read tasks from: $TASK_QUEUE"
log "   2. For each task in queue[]:"
log "      - Move to inProgress[]"
log "      - Implement the screen per specification"
log "      - Run testCommand to validate"
log "      - Commit with: 'feat(onboarding): Add [title] ([id])'"
log "      - Move to completed[]"
log "   3. Update task-queue.json after each task"
log ""
log "Task execution ready. AI should now begin implementation..."

# Keep log open for AI to append to
tail -f "$EXECUTION_LOG" &
TAIL_PID=$!

# Wait for user to press key to stop monitoring
echo ""
echo "Press any key to stop monitoring (tasks will continue)..."
read -n 1 -s

kill $TAIL_PID 2>/dev/null || true

echo ""
success "Monitoring stopped. Check execution.log for progress."
echo "View live progress: tail -f $EXECUTION_LOG"

