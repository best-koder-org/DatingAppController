#!/usr/bin/env python3
"""
Merge Wave Analyzer
Analyzes open automation PRs for merge conflicts and groups them into safe merge waves.

Wave logic:
  1. Sort PRs by dependency order (ONB-050 before ONB-060 before ONB-070 etc.)
  2. Simulate merging each PR into main (in order) using git merge --no-commit
  3. If clean → add to current wave
  4. If conflict → stop wave, report conflict details, suggest fix
  5. Output a merge plan as JSON + human-readable summary
"""
import json, subprocess, sys, os, re
from pathlib import Path

def run(cmd, cwd=None, check=True):
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        print(f"CMD FAIL: {cmd}\n{r.stderr.strip()}")
    return r

def get_open_prs(cwd):
    """Get all open automation PRs sorted by number."""
    r = run('gh pr list --json number,title,headRefName,url --limit 20', cwd=cwd)
    if r.returncode != 0:
        return []
    prs = json.loads(r.stdout)
    # Only automation PRs
    prs = [p for p in prs if p['headRefName'].startswith('automation/')]
    # Sort by PR number (creation order = dependency order)
    prs.sort(key=lambda p: p['number'])
    return prs

def test_merge(pr, cwd):
    """Test if a PR can merge cleanly into current HEAD. Returns (clean, conflict_files)."""
    branch = pr['headRefName']
    # Try merge --no-commit to test
    r = run(f'git merge --no-commit --no-ff origin/{branch}', cwd=cwd, check=False)
    if r.returncode == 0:
        # Clean merge - commit it so next PR tests against this state
        run('git commit -m "test merge"', cwd=cwd, check=False)
        return True, []
    else:
        # Conflict! Find which files
        conflicts = []
        r2 = run('git diff --name-only --diff-filter=U', cwd=cwd, check=False)
        if r2.stdout.strip():
            conflicts = r2.stdout.strip().split('\n')
        # Abort the merge
        run('git merge --abort', cwd=cwd, check=False)
        return False, conflicts

def main():
    root = Path(__file__).parent.parent
    mobile = root / "repos/mobile_dejtingapp"
    report_file = root / ".ai-workspace/merge-report.json"

    print("=" * 60)
    print("MERGE WAVE ANALYZER")
    print("=" * 60)

    # Fetch latest
    run("git fetch origin", cwd=mobile)

    prs = get_open_prs(cwd=mobile)
    if not prs:
        print("No open automation PRs found.")
        report = {"waves": [], "conflicts": [], "summary": "No PRs to merge"}
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        return

    print(f"\nFound {len(prs)} open automation PRs:")
    for p in prs:
        print(f"  #{p['number']} {p['title']} ({p['headRefName']})")

    # Create a temporary test branch from main
    run("git checkout main", cwd=mobile)
    run("git pull origin main", cwd=mobile)
    run("git branch -D merge-test 2>/dev/null; git checkout -b merge-test", cwd=mobile)

    waves = []
    current_wave = []
    conflicts = []

    for pr in prs:
        print(f"\nTesting PR #{pr['number']}: {pr['title']}...")
        clean, conflict_files = test_merge(pr, cwd=mobile)

        if clean:
            print(f"  ✅ Clean merge")
            current_wave.append({
                "number": pr["number"],
                "title": pr["title"],
                "url": pr["url"],
                "branch": pr["headRefName"],
                "status": "safe"
            })
        else:
            print(f"  ❌ CONFLICT in: {', '.join(conflict_files)}")
            # End current wave, start conflict tracking
            if current_wave:
                waves.append(current_wave)
                current_wave = []
            conflicts.append({
                "number": pr["number"],
                "title": pr["title"],
                "url": pr["url"],
                "branch": pr["headRefName"],
                "conflictFiles": conflict_files,
                "status": "conflict",
                "needsRebase": True
            })

    if current_wave:
        waves.append(current_wave)

    # Clean up test branch
    run("git checkout main", cwd=mobile)
    run("git branch -D merge-test", cwd=mobile, check=False)

    # Build report
    report = {
        "analyzedAt": subprocess.run("date -Iseconds", shell=True, capture_output=True, text=True).stdout.strip(),
        "totalPRs": len(prs),
        "waves": [],
        "conflicts": conflicts,
        "summary": ""
    }

    for i, wave in enumerate(waves):
        report["waves"].append({
            "waveNumber": i + 1,
            "prs": wave,
            "status": "ready",
            "mergeCommand": " && ".join([f"gh pr merge {p['number']} --merge" for p in wave])
        })

    # Summary
    safe_count = sum(len(w) for w in waves)
    conflict_count = len(conflicts)
    lines = []
    lines.append(f"{safe_count} PRs safe to merge, {conflict_count} have conflicts")
    for i, wave in enumerate(report["waves"]):
        pr_list = ", ".join([f"#{p['number']} {p['title']}" for p in wave["prs"]])
        lines.append(f"Wave {i+1}: {pr_list}")
    for c in conflicts:
        lines.append(f"CONFLICT: #{c['number']} {c['title']} — files: {', '.join(c['conflictFiles'])}")
        lines.append(f"  → Needs rebase onto main after Wave {len(waves)} is merged")
    report["summary"] = "\n".join(lines)

    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 60)
    print("MERGE PLAN")
    print("=" * 60)
    print(report["summary"])
    print(f"\nFull report: {report_file}")

    # Exit code: 0 = all clean, 1 = has conflicts (not a failure, just informational)
    sys.exit(0)

if __name__ == "__main__":
    main()
