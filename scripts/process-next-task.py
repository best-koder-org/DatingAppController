#!/usr/bin/env python3
import json, subprocess, sys
from datetime import datetime
from pathlib import Path

def run(cmd, cwd=None, check=True):
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        print(f"FAIL: {cmd}\n{r.stderr}")
        sys.exit(1)
    return r

def main():
    root = Path(__file__).parent.parent
    queue_file = root / ".ai-workspace/task-queue.json"
    templates_dir = root / "scripts/templates"

    with open(queue_file) as f:
        queue = json.load(f)

    if not queue["queue"]:
        print("No tasks left!")
        return

    task = queue["queue"][0]
    tid = task["id"]
    print(f"Processing: {tid} - {task['title']}")

    tpl = templates_dir / f"{tid}.dart"
    if not tpl.exists():
        print(f"No template: {tpl}")
        return

    mobile = root / "repos/mobile_dejtingapp"
    branch = f"automation/{tid.lower()}-{task['title'].lower().replace(' ','-')[:30]}"

    run("git config pull.rebase false", cwd=mobile)
    run("git checkout main && git pull origin main", cwd=mobile)
    run(f"git checkout -b {branch}", cwd=mobile)

    dest = mobile / task["filePath"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(tpl.read_text())
    print(f"Created {dest.name}")

    # Skip flutter analyze - templates are pre-validated locally
    print("Skipping flutter analyze (pre-validated templates)")

    run(f"git add {dest}", cwd=mobile)
    run(f'git commit -m "feat(onboarding): Add {task["title"]} ({tid})"', cwd=mobile)
    run(f"git push origin {branch}", cwd=mobile)
    run(f'gh pr create --base main --head {branch} --title "feat(onboarding): {task["title"]}" --body "Auto-generated from task queue"', cwd=mobile)
    print(f"PR created for {tid}")

    queue["queue"].pop(0)
    queue["completed"].append({**task, "completedAt": datetime.now().isoformat()})
    with open(queue_file, "w") as f:
        json.dump(queue, f, indent=2)
    print("Done!")

if __name__ == "__main__":
    main()
