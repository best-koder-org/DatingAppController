#!/bin/bash
# Eval all screen templates and show a compact leaderboard.
# Usage: ./scripts/eval-all.sh

set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$DIR")"
TEMPLATES="$ROOT/scripts/templates"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📊  Screen Eval Leaderboard"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
printf "%-10s  %-6s  %-5s  %s\n" "TASK" "GRADE" "SCORE" "QUICK TAKE"
echo "──────────────────────────────────────────────────"

for f in "$TEMPLATES"/ONB-*.dart; do
  [ -f "$f" ] || continue
  result=$(python3 "$DIR/eval-screen.py" "$f" --format json 2>/dev/null)
  task=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['task_id'])" 2>/dev/null)
  grade=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['grade'])" 2>/dev/null)
  score=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['total_score'])" 2>/dev/null)
  
  # Grade emoji
  case "$grade" in
    A) emoji="🟢" ;;
    B) emoji="🔵" ;;
    C) emoji="🟡" ;;
    D) emoji="🟠" ;;
    F) emoji="🔴" ;;
    *) emoji="⚪" ;;
  esac
  
  # Quick take from checks
  fails=$(echo "$result" | python3 -c "
import sys,json
d=json.load(sys.stdin)
fails=[c['name'] for c in d.get('checks',[]) if not c.get('passed',True)]
print(', '.join(fails[:3]) if fails else 'all good')
" 2>/dev/null)
  
  printf "%-10s  %s %-4s  %s/100  %s\n" "$task" "$emoji" "$grade" "$score" "$fails"
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
