#!/bin/bash
# Rollback all repos to snapshot tag

set -e

SNAPSHOT_NAME="$1"

if [ -z "$SNAPSHOT_NAME" ]; then
    echo "❌ Error: Snapshot name required"
    echo "Usage: $0 <snapshot-name>"
    exit 1
fi

echo "⏪ Rolling back to: $SNAPSHOT_NAME"
echo "=================================="
read -p "Are you sure? This will DISCARD all changes! (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Rollback cancelled"
    exit 1
fi

cd repos

for repo in */; do
    if [ -d "$repo/.git" ]; then
        echo "  ⏮️  Resetting $repo..."
        cd "$repo"
        git reset --hard "$SNAPSHOT_NAME"
        git clean -fd
        cd ..
    fi
done

cd ..

echo ""
echo "✅ Rollback complete"
echo "📊 All repos reset to: $SNAPSHOT_NAME"
