#!/usr/bin/env python3
"""
Merge Safe Wave
Runs the wave analyzer first, then merges all PRs in the first safe wave.
If conflicts exist, stops before them and reports.
"""
import json, subprocess, sys
from pathlib import Path

def run(cmd, cwd=None, check=True):
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        print(f"FAIL: {cmd}\n{r.stderr}")
        sys.exit(1)
    return r

def main():
    root = Path(__file__).parent.parent
    mobile = root / "repos/mobile_dejtingapp"

    # Step 1: Run analyzer
    print("Step 1: Analyzing merge waves...")
    r = run(f"python3 {root}/scripts/merge-wave-analyzer.py", cwd=root, check=False)
    print(r.stdout)

    report_file = root / ".ai-workspace/merge-report.json"
    if not report_file.exists():
        print("No merge report generated")
        sys.exit(1)

    report = json.loads(report_file.read_text())

    if not report["waves"]:
        print("No safe waves to merge.")
        if report["conflicts"]:
            print("\nConflicts found:")
            for c in report["conflicts"]:
                print(f"  ❌ #{c['number']} {c['title']} — {', '.join(c['conflictFiles'])}")
        sys.exit(1)

    # Step 2: Merge wave 1
    wave = report["waves"][0]
    print(f"\nStep 2: Merging Wave {wave['waveNumber']} ({len(wave['prs'])} PRs)...")

    merged = []
    for pr in wave["prs"]:
        print(f"  Merging PR #{pr['number']}: {pr['title']}...")
        r = run(f"gh pr merge {pr['number']} --merge --delete-branch", cwd=mobile, check=False)
        if r.returncode == 0:
            print(f"  ✅ Merged #{pr['number']}")
            merged.append(pr)
        else:
            print(f"  ❌ Failed to merge #{pr['number']}: {r.stderr.strip()}")
            break

    # Step 3: Summary
    print(f"\n{'='*60}")
    print(f"MERGE RESULTS")
    print(f"{'='*60}")
    print(f"Merged: {len(merged)}/{len(wave['prs'])} PRs in Wave 1")
    for m in merged:
        print(f"  ✅ #{m['number']} {m['title']}")

    if report["conflicts"]:
        print(f"\n⚠️  {len(report['conflicts'])} PRs need attention (conflict):")
        for c in report["conflicts"]:
            print(f"  ❌ #{c['number']} {c['title']}")
            print(f"     Files: {', '.join(c['conflictFiles'])}")
            print(f"     → Needs rebase onto updated main")

    remaining_waves = report["waves"][1:]
    if remaining_waves:
        total_remaining = sum(len(w["prs"]) for w in remaining_waves)
        print(f"\n📋 {total_remaining} more PRs in {len(remaining_waves)} wave(s) — run again to merge next wave")

    # Update report with merge results
    report["waves"][0]["status"] = "merged"
    report["mergedPRs"] = merged
    report_file.write_text(json.dumps(report, indent=2))

    if not merged:
        sys.exit(1)

if __name__ == "__main__":
    main()
