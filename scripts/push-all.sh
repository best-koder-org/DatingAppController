#!/bin/bash
# Push all repos with changes atomically

set -e

echo "🚀 Pushing all changed repositories"
echo "===================================="

cd repos

# First, verify all repos can push (no conflicts)
echo "✓ Verifying remote access..."
failed=0
for repo in */; do
    if [ -d "$repo/.git" ]; then
        cd "$repo"
        if [ -n "$(git rev-list --count @{u}..HEAD 2>/dev/null)" ]; then
            git fetch origin --dry-run 2>&1 || ((failed++))
        fi
        cd ..
    fi
done

if [ $failed -gt 0 ]; then
    echo "❌ Error: $failed repos cannot connect to remote"
    exit 1
fi

# Now push
for repo in */; do
    if [ -d "$repo/.git" ] && [ -n "$(git -C "$repo" rev-list --count @{u}..HEAD 2>/dev/null)" ]; then
        echo "  📤 Pushing $repo..."
        cd "$repo"
        git push origin "$(git branch --show-current)"
        cd ..
    fi
done

cd ..

echo ""
echo "✅ All repositories pushed"
