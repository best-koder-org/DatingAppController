#!/usr/bin/env python3
"""
Morning report generator for DatingApp overnight automation.
Creates a GitHub Issue summarizing overnight activity:
  - PRs created/merged/failed
  - CI status per PR
  - Merge conflict analysis
  - Queue status
  - Action items for human review
"""
import json, subprocess, sys
from datetime import datetime
from pathlib import Path

REPOS = [
    "best-koder-ever/mobile_dejtingapp",
    "best-koder-ever/UserService",
    "best-koder-ever/MatchmakingService",
    "best-koder-ever/swipe-service",
    "best-koder-ever/photo-service",
    "best-koder-ever/messaging-service",
    "best-koder-ever/dejting-yarp",
]

CONTROLLER_REPO = "best-koder-ever/DatingAppController"

def run(cmd, check=False):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r

def get_open_prs(repo):
    """Get open automation PRs for a repo."""
    r = run(f'gh pr list --repo {repo} --label automation --state open --json number,title,headRefName,createdAt,statusCheckRollup --limit 20')
    if r.returncode != 0:
        # Try without label filter (our PRs may not have labels)
        r = run(f'gh pr list --repo {repo} --state open --json number,title,headRefName,createdAt,statusCheckRollup --limit 20')
    if r.returncode == 0 and r.stdout.strip():
        prs = json.loads(r.stdout)
        # Filter to automation branches only
        return [p for p in prs if p.get("headRefName", "").startswith("automation/")]
    return []

def get_ci_status(pr, repo):
    """Get CI check status for a PR."""
    checks = pr.get("statusCheckRollup", [])
    if not checks:
        return "⏳ pending"
    
    statuses = [c.get("conclusion", c.get("status", "unknown")) for c in checks]
    if all(s == "SUCCESS" or s == "success" for s in statuses):
        return "✅ passing"
    elif any(s == "FAILURE" or s == "failure" for s in statuses):
        return "❌ failing"
    elif any(s in ("PENDING", "pending", "IN_PROGRESS") for s in statuses):
        return "⏳ running"
    return "⚠️ unknown"

def main():
    root = Path(__file__).parent.parent
    queue_file = root / ".ai-workspace/task-queue.json"
    merge_report = root / ".ai-workspace/merge-report.json"

    with open(queue_file) as f:
        queue = json.load(f)

    today = datetime.now().strftime("%Y-%m-%d")
    
    # ── Gather PR data ──────────────────────────────────────────
    all_prs = {}
    total_open = 0
    for repo in REPOS:
        prs = get_open_prs(repo)
        if prs:
            all_prs[repo] = prs
            total_open += len(prs)

    # ── Gather merge report ─────────────────────────────────────
    merge_info = ""
    if merge_report.exists():
        with open(merge_report) as f:
            mr = json.load(f)
        waves = mr.get("waves", [])
        conflicts = mr.get("conflicts", [])
        if waves:
            merge_info += f"**Wave 1 (safe to merge):** {len(waves[0]) if waves else 0} PRs\n"
        if conflicts:
            merge_info += f"**Conflicts detected:** {len(conflicts)} PRs need manual resolution\n"
            for c in conflicts:
                merge_info += f"  - #{c.get('number', '?')}: {c.get('conflicting_files', ['unknown'])}\n"
    else:
        merge_info = "No merge analysis available (run merge-wave-analyzer first)"

    # ── Build report ────────────────────────────────────────────
    queue_count = len(queue.get("queue", []))
    completed_count = len(queue.get("completed", []))
    in_progress = queue.get("inProgress", [])

    report = f"""# 🌅 Morning Report — {today}

## Summary
| Metric | Count |
|--------|-------|
| Open automation PRs | {total_open} |
| Tasks in queue | {queue_count} |
| Tasks completed (all time) | {completed_count} |
| Tasks in progress | {len(in_progress)} |

## Open PRs by Repo
"""

    if not all_prs:
        report += "\n_No open automation PRs found._\n"
    else:
        for repo, prs in all_prs.items():
            repo_short = repo.split("/")[-1]
            report += f"\n### {repo_short}\n"
            for pr in prs:
                ci = get_ci_status(pr, repo)
                report += f"- **#{pr['number']}** {pr['title']} {ci}\n"

    report += f"""
## Merge Analysis
{merge_info}

## Queue Status
"""
    if queue_count > 0:
        report += "**Next up:**\n"
        for t in queue["queue"][:5]:
            report += f"- {t['id']}: {t['title']} ({t.get('service', 'mobile_dejtingapp')})\n"
    else:
        report += "_Queue empty — refill script should run before next automation cycle._\n"

    if in_progress:
        report += "\n**In progress (may be stale):**\n"
        for t in in_progress:
            report += f"- {t['id']}: {t['title']} (started: {t.get('startedAt', 'unknown')})\n"

    report += f"""
## 👤 Action Items
1. Review open PRs above — merge those with ✅
2. Test merged screens on device/emulator
3. Resolve any ❌ CI failures
4. Check merge conflicts if flagged

---
*Auto-generated at {datetime.now().strftime('%H:%M')} by morning-report.py*
"""

    # ── Post as GitHub Issue ────────────────────────────────────
    title = f"🌅 Morning Report — {today}"
    
    # Write report to temp file to avoid shell escaping issues
    report_file = root / ".ai-workspace/morning-report.md"
    report_file.write_text(report)
    
    r = run(f'gh issue create --repo {CONTROLLER_REPO} --title "{title}" --body-file {report_file} --label "morning-report"')
    
    if r.returncode == 0:
        print(f"Morning report posted: {r.stdout.strip()}")
    else:
        # Label might not exist yet, try without
        r = run(f'gh issue create --repo {CONTROLLER_REPO} --title "{title}" --body-file {report_file}')
        if r.returncode == 0:
            print(f"Morning report posted (no label): {r.stdout.strip()}")
        else:
            print(f"WARNING: Could not create issue. Report saved to {report_file}")
            print(f"Error: {r.stderr}")

    # Also print to stdout for workflow logs
    print("\n" + "=" * 60)
    print(report)

if __name__ == "__main__":
    main()
