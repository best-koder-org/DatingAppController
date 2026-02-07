#!/bin/bash
# Create snapshot tags across all repos

set -e

SNAPSHOT_NAME="${1:-snapshot-$(date +%Y%m%d-%H%M%S)}"

echo "📸 Creating snapshot: $SNAPSHOT_NAME"
echo "=================================="

cd repos

for repo in */; do
    if [ -d "$repo/.git" ]; then
        echo "  📌 Tagging $repo..."
        cd "$repo"
        git tag -f "$SNAPSHOT_NAME" -m "Snapshot before AI batch"
        cd ..
    fi
done

cd ..

echo ""
echo "✅ Snapshot created: $SNAPSHOT_NAME"
echo "📝 To rollback: ./scripts/rollback.sh \"$SNAPSHOT_NAME\""
