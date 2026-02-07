#!/bin/bash
# Show status across all repos

echo "📊 DatingApp Multi-Repo Status"
echo "=============================="

cd repos

for repo in */; do
    if [ -d "$repo/.git" ]; then
        cd "$repo"
        
        # Check if repo has changes
        if ! git diff-index --quiet HEAD 2>/dev/null || [ -n "$(git ls-files --others --exclude-standard)" ]; then
            echo ""
            echo "📁 $repo"
            echo "   Branch: $(git branch --show-current)"
            echo "   Changes:"
            
            # Modified files
            modified=$(git diff --name-only | wc -l)
            [ $modified -gt 0 ] && echo "      Modified: $modified files"
            
            # Untracked files
            untracked=$(git ls-files --others --exclude-standard | wc -l)
            [ $untracked -gt 0 ] && echo "      Untracked: $untracked files"
            
            # Commits ahead
            ahead=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo "0")
            [ $ahead -gt 0 ] && echo "      Commits ahead: $ahead"
        fi
        
        cd ..
    fi
done

cd ..

echo ""
echo "✅ Status check complete"
