#!/usr/bin/env python3
"""
Enhanced task processor for DatingApp overnight automation.
Supports:
  - Flutter UI screens (template-based or description-based)
  - Backend .NET service tasks (stub generation)
  - Companion test file creation
  - Multi-repo routing via task 'service' field

Resilience: Build/test failures are recorded gracefully (exit 0)
            so parallel matrix jobs are never cancelled by one bad task.
"""
import json, subprocess, sys, textwrap
from datetime import datetime
from pathlib import Path

# Import eval system
sys.path.insert(0, str(Path(__file__).parent))
from eval_screen import eval_file  # noqa: E402
from smart_generate import smart_generate, smart_generate_test  # noqa: E402

# ── Repo routing map ─────────────────────────────────────────────────
SERVICE_REPO = {
    "mobile_dejtingapp": "repos/mobile_dejtingapp",
    "UserService":       "repos/UserService",
    "MatchmakingService":"repos/MatchmakingService",
    "swipe-service":     "repos/swipe-service",
    "photo-service":     "repos/photo-service",
    "messaging-service": "repos/messaging-service",
    "dejting-yarp":      "repos/dejting-yarp",
}

def run(cmd, cwd=None, check=True):
    """Run a shell command, abort on failure unless check=False."""
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        print(f"FAIL: {cmd}\n{r.stderr}")
        sys.exit(1)
    return r

def sanitize_branch(tid, title):
    slug = title.lower().replace(" ", "-").replace("'", "")
    slug = "".join(c for c in slug if c.isalnum() or c == "-")[:40]
    return f"automation/{tid.lower()}-{slug}"

def fail_task(queue, queue_file, task, reason, root):
    """Record a task failure gracefully and exit 0 so other matrix jobs continue."""
    tid = task["id"]
    queue["queue"].pop(0)
    queue.setdefault("failed", [])
    queue["failed"].append({**task, "failedAt": datetime.now().isoformat(), "reason": reason})
    with open(queue_file, "w") as f:
        json.dump(queue, f, indent=2)
    run(f"git add {queue_file}", cwd=root)
    run(f'git commit -m "ci: {tid} FAILED — {reason}"', cwd=root)
    run("git push origin main", cwd=root)
    print(f"TASK_FAILED: {tid} — {reason} (recorded, continuing pipeline)")
    sys.exit(0)  # EXIT 0 — task failed but pipeline continues

# ── Flutter screen generator (from description) ─────────────────────
def generate_flutter_screen(task):
    """Generate a minimal Flutter StatefulWidget from task description."""
    tid = task["id"]
    title = task["title"]
    class_name = "".join(w.capitalize() for w in title.replace("-", " ").split()) + "Screen"
    file_stem = task["filePath"].split("/")[-1].replace(".dart", "")

    criteria = "\n".join(f"  // - {c}" for c in task.get("acceptanceCriteria", []))
    progress_pct = "0.5"  # default; can be overridden

    return textwrap.dedent(f'''\
    import 'package:flutter/material.dart';

    /// {title} ({tid})
    /// Auto-generated from task queue. Acceptance criteria:
    {criteria}
    class {class_name} extends StatefulWidget {{
      const {class_name}({{super.key}});

      @override
      State<{class_name}> createState() => _{class_name}State();
    }}

    class _{class_name}State extends State<{class_name}> {{
      bool _isValid = false;

      @override
      Widget build(BuildContext context) {{
        return Scaffold(
          backgroundColor: Colors.white,
          appBar: AppBar(
            backgroundColor: Colors.transparent,
            elevation: 0,
            leading: IconButton(
              icon: const Icon(Icons.arrow_back, color: Colors.black),
              onPressed: () => Navigator.of(context).pop(),
            ),
            actions: [
              IconButton(
                icon: const Icon(Icons.close, color: Colors.black),
                onPressed: () => Navigator.of(context).popUntil((r) => r.isFirst),
              ),
            ],
          ),
          body: SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Progress bar
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: {progress_pct},
                      backgroundColor: Colors.grey[200],
                      valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFFFF6B6B)),
                      minHeight: 4,
                    ),
                  ),
                  const SizedBox(height: 32),
                  Text(
                    '{title}',
                    style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  // TODO: Implement screen body per acceptance criteria
                  const Expanded(
                    child: Center(
                      child: Text('TODO: Implement {tid} body'),
                    ),
                  ),
                  // Next button
                  SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: ElevatedButton(
                      onPressed: _isValid ? () {{}} : null,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFFF6B6B),
                        foregroundColor: Colors.white,
                        disabledBackgroundColor: Colors.grey[300],
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(26),
                        ),
                      ),
                      child: const Text('Next', style: TextStyle(fontSize: 18)),
                    ),
                  ),
                  const SizedBox(height: 24),
                ],
              ),
            ),
          ),
        );
      }}
    }}
    ''')

def generate_flutter_test(task):
    """Generate a basic widget test for a Flutter screen."""
    tid = task["id"]
    title = task["title"]
    class_name = "".join(w.capitalize() for w in title.replace("-", " ").split()) + "Screen"
    import_path = task["filePath"].replace("lib/", "package:dejtingapp/")

    return textwrap.dedent(f'''\
    import 'package:flutter/material.dart';
    import 'package:flutter_test/flutter_test.dart';
    import '{import_path}';

    void main() {{
      group('{title} ({tid})', () {{
        testWidgets('renders without errors', (tester) async {{
          await tester.pumpWidget(
            const MaterialApp(home: {class_name}()),
          );
          await tester.pumpAndSettle();
          expect(find.byType({class_name}), findsOneWidget);
        }});

        testWidgets('has a Next button', (tester) async {{
          await tester.pumpWidget(
            const MaterialApp(home: {class_name}()),
          );
          expect(find.text('Next'), findsOneWidget);
        }});

        testWidgets('Next button is initially disabled', (tester) async {{
          await tester.pumpWidget(
            const MaterialApp(home: {class_name}()),
          );
          final button = tester.widget<ElevatedButton>(find.byType(ElevatedButton));
          expect(button.onPressed, isNull);
        }});
      }});
    }}
    ''')

# ── Backend stub generator (for .NET services) ──────────────────────
def generate_dotnet_stub(task):
    """Generate a minimal C# file skeleton for a backend task."""
    tid = task["id"]
    title = task["title"]
    service = task["service"]
    class_name = "".join(w.capitalize() for w in title.replace("-", " ").split())
    namespace = service.replace("-", "_")

    criteria = "\n".join(f"    // - {c}" for c in task.get("acceptanceCriteria", []))

    return textwrap.dedent(f'''\
    // {title} ({tid})
    // Auto-generated stub from task queue
    // Acceptance criteria:
    {criteria}

    namespace {namespace};

    /// <summary>
    /// TODO: Implement {title}
    /// </summary>
    public class {class_name}
    {{
        // TODO: Implement per acceptance criteria above
    }}
    ''')

# ── Main pipeline ────────────────────────────────────────────────────
def main():
    root = Path(__file__).parent.parent
    queue_file = root / ".ai-workspace/task-queue.json"
    templates_dir = root / "scripts/templates"

    with open(queue_file) as f:
        queue = json.load(f)

    if not queue["queue"]:
        print("QUEUE_EMPTY")
        return

    # ── Check pause flag ────────────────────────────────────────
    pause_flag = root / ".ai-workspace/pause.flag"
    if pause_flag.exists():
        reason = pause_flag.read_text().strip() or "Manual pause"
        print(f"PAUSED: {reason}")
        print("Remove .ai-workspace/pause.flag to resume")
        return

    task = queue["queue"][0]
    tid = task["id"]
    service = task.get("service", "mobile_dejtingapp")
    task_type = task.get("type", "screen")
    print(f"Processing: {tid} - {task['title']} (service={service}, type={task_type})")

    # Resolve target repo
    repo_rel = SERVICE_REPO.get(service)
    if not repo_rel:
        print(f"ERROR: Unknown service '{service}'. Supported: {list(SERVICE_REPO.keys())}")
        fail_task(queue, queue_file, task, f"unknown service: {service}", root)
    repo_dir = root / repo_rel

    if not repo_dir.exists():
        print(f"ERROR: Repo dir not found: {repo_dir}")
        fail_task(queue, queue_file, task, f"repo dir not found: {repo_dir}", root)

    # ── Determine source content ────────────────────────────────
    template_file = templates_dir / f"{tid}.dart"
    is_flutter = service == "mobile_dejtingapp"

    # Check for backend multi-file templates (e.g. scripts/templates/backend/T156-*.cs)
    backend_templates_dir = templates_dir / "backend"
    backend_templates = sorted(backend_templates_dir.glob(f"{tid}-*.cs")) if backend_templates_dir.exists() else []

    if backend_templates:
        # Multi-file backend template — deploy all files
        content = backend_templates[0].read_text()  # Primary file
        source = "template"
        print(f"Using {len(backend_templates)} pre-built backend templates for {tid}")
    elif template_file.exists():
        # Pre-built template (highest quality)
        content = template_file.read_text()
        source = "template"
        print(f"Using pre-built template: {template_file.name}")
    elif is_flutter:
        # Try smart generator first (real implementations), fall back to generic template
        smart_content, smart_label = smart_generate(task, repo_dir)
        if smart_content:
            content = smart_content
            source = smart_label
            print(f"Smart-generated Flutter code ({smart_label}) for {tid}")
        elif task_type == "screen":
            content = generate_flutter_screen(task)
            source = "generated-flutter"
            print(f"Generated Flutter screen from description (fallback)")
        else:
            content = generate_flutter_screen(task)
            source = "generated-flutter"
            print(f"Generated Flutter widget from description (fallback)")
    elif not is_flutter:
        # Generate backend stub
        content = generate_dotnet_stub(task)
        source = "generated-dotnet"
        print(f"Generated .NET stub from description")
    else:
        print(f"ERROR: No template and can't generate for type={task_type}")
        fail_task(queue, queue_file, task, f"no template for type={task_type}", root)

    # ── Create branch ───────────────────────────────────────────
    branch = sanitize_branch(tid, task["title"])
    run("git config pull.rebase false", cwd=repo_dir)
    # Clean any dirty state from previous matrix job on same self-hosted runner
    run("git checkout main", cwd=repo_dir, check=False)
    run("git clean -fd", cwd=repo_dir, check=False)
    run("git checkout .", cwd=repo_dir, check=False)
    run("git pull origin main", cwd=repo_dir)
    run(f"git checkout -b {branch}", cwd=repo_dir)

    # ── Write feature file(s) ────────────────────────────────────
    dest = repo_dir / task["filePath"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content)
    print(f"Created: {dest}")

    # Deploy additional backend template files
    if backend_templates and len(backend_templates) > 1:
        additional_paths = task.get("additionalFiles", [])
        remaining_templates = backend_templates[1:]
        for i, tmpl in enumerate(remaining_templates):
            if i < len(additional_paths):
                add_dest = repo_dir / additional_paths[i]
            else:
                fname = tmpl.name.split("-", 2)[-1]
                if "Controller" in fname:
                    add_dest = repo_dir / "Controllers" / fname
                elif "Service" in fname:
                    add_dest = repo_dir / "Services" / fname
                elif "Dto" in fname:
                    add_dest = repo_dir / "DTOs" / fname
                else:
                    add_dest = repo_dir / fname
            add_dest.parent.mkdir(parents=True, exist_ok=True)
            add_dest.write_text(tmpl.read_text())
            print(f"Created: {add_dest}")

    # ── Write companion test (Flutter only) ─────────────────────
    test_file = None
    if is_flutter and not backend_templates:
        test_rel = task["filePath"].replace("lib/", "test/").replace(".dart", "_test.dart")
        test_dest = repo_dir / test_rel
        test_dest.parent.mkdir(parents=True, exist_ok=True)

        test_template = templates_dir / f"{tid}-TEST.dart"
        if test_template.exists():
            test_content = test_template.read_text()
            print(f"Using pre-built test template: {test_template.name}")
        else:
            # Try smart test generator first
            smart_test = smart_generate_test(task, repo_dir)
            if smart_test:
                test_content = smart_test
                print(f"Smart-generated companion test for {tid}")
            else:
                test_content = generate_flutter_test(task)
                print(f"Generated companion test (fallback)")

        test_dest.write_text(test_content)
        test_file = test_dest
        print(f"Created test: {test_dest}")

    # ── Validate ────────────────────────────────────────────────
    if is_flutter:
        # flutter analyze — HARD GATE for errors, warn for hints/infos
        print("Running flutter pub get...")
        run("flutter pub get", cwd=repo_dir, check=False)
        print("Running flutter analyze...")
        r = run("flutter analyze --no-fatal-infos --no-fatal-warnings", cwd=repo_dir, check=False)
        if r.returncode != 0:
            print(f"FLUTTER ANALYZE FAILED — aborting PR creation for {tid}")
            print(f"Output:\n{r.stdout[-1000:]}")
            # Revert: checkout main, delete branch
            run("git checkout main", cwd=repo_dir, check=False)
            run(f"git branch -D {branch}", cwd=repo_dir, check=False)
            fail_task(queue, queue_file, task, "flutter analyze failed", root)
        else:
            print("flutter analyze: PASS ✅")
        # Also run flutter test if test file exists
        if test_file and test_file.exists():
            print("Running flutter test...")
            r_test = run(f"flutter test {test_file.relative_to(repo_dir)}", cwd=repo_dir, check=False)
            if r_test.returncode != 0:
                print(f"FLUTTER TEST FAILED — aborting PR creation for {tid}")
                print(f"Output:\n{r_test.stdout[-1000:]}")
                run("git checkout main", cwd=repo_dir, check=False)
                run(f"git branch -D {branch}", cwd=repo_dir, check=False)
                fail_task(queue, queue_file, task, "flutter test failed", root)
            else:
                print("flutter test: PASS ✅")
    elif not is_flutter:
        # dotnet build — HARD GATE, PR not created if build fails
        print("Running dotnet restore...")
        r_restore = run("dotnet restore", cwd=repo_dir, check=False)
        if r_restore.returncode != 0:
            print(f"WARNING: dotnet restore failed, trying build anyway")
        print("Running dotnet build...")
        r = run("dotnet build --configuration Release", cwd=repo_dir, check=False)
        if r.returncode != 0:
            print(f"BUILD FAILED — aborting PR creation for {tid}")
            print(f"Build output:\n{r.stdout[-1000:]}")
            print(f"Build errors:\n{r.stderr[-1000:]}")
            # Revert: checkout main, delete branch
            run("git checkout main", cwd=repo_dir, check=False)
            run(f"git branch -D {branch}", cwd=repo_dir, check=False)
            fail_task(queue, queue_file, task, "dotnet build failed", root)
        else:
            print("dotnet build: PASS ✅")

    # ── Eval quality gate ───────────────────────────────────────
    eval_md = ""
    if is_flutter:
        try:
            report = eval_file(
                str(dest.relative_to(repo_dir)),
                task=task,
                repo_dir=str(repo_dir),
            )
            eval_md = report.to_markdown()
            report_json = report.to_json()
            # Write eval artifact for morning report
            eval_dir = root / ".ai-workspace/evals"
            eval_dir.mkdir(parents=True, exist_ok=True)
            (eval_dir / f"{tid}.json").write_text(report_json)
            (eval_dir / f"{tid}.md").write_text(eval_md)
            print(f"Eval: {report.total_score}/100 (Grade {report.grade})")
            if report.total_score < 40:
                print(f"WARNING: Low eval score ({report.total_score}). PR created but flagged.")
        except Exception as e:
            print(f"WARNING: Eval failed (non-blocking): {e}")
            eval_md = f"*Eval skipped: {e}*"

    # ── Commit & push ───────────────────────────────────────────
    run("git add -A", cwd=repo_dir)

    commit_msg = f'feat({service}): Add {task["title"]} ({tid})'
    if source.startswith("generated"):
        commit_msg += "\n\nAuto-generated from task description. Needs human review."

    run(f'git commit -m "{commit_msg}"', cwd=repo_dir)
    run(f"git push origin {branch}", cwd=repo_dir)

    # ── Create PR ───────────────────────────────────────────────
    pr_body = f"""## {task['title']} ({tid})

**Service:** {service}
**Type:** {task_type}
**Source:** {source}
**Safety Tier:** {task.get('safetyTier', 'N/A')}

### Description
{task.get('description', 'See task definition.')}

### Acceptance Criteria
{"".join(f"- [ ] {c}" + chr(10) for c in task.get('acceptanceCriteria', []))}

### Files Changed
- `{task['filePath']}`{f"{chr(10)}- `{test_file.relative_to(repo_dir)}`" if test_file else ""}

### Safety Notes
{task.get('safetyNotes', 'No safety notes.')}

{eval_md if eval_md else ""}

---
*Auto-generated by overnight automation pipeline*
"""

    run(
        f'gh pr create --base main --head {branch} '
        f'--title "{commit_msg.split(chr(10))[0]}" '
        f'--body "{pr_body.replace(chr(34), chr(39))}"',
        cwd=repo_dir
    )
    print(f"PR created for {tid}")

    # ── Update queue ────────────────────────────────────────────
    completed_task = {**task, "completedAt": datetime.now().isoformat(), "source": source}
    queue["queue"].pop(0)

    # Move from inProgress or add to completed
    queue.setdefault("inProgress", [])
    queue["inProgress"] = [t for t in queue["inProgress"] if t["id"] != tid]
    queue["completed"].append(completed_task)

    with open(queue_file, "w") as f:
        json.dump(queue, f, indent=2)

    run(f"git add {queue_file}", cwd=root)
    run(f'git commit -m "ci: Mark {tid} as completed"', cwd=root)
    run("git push origin main", cwd=root)
    print(f"DONE: {tid} processed successfully (source={source})")

if __name__ == "__main__":
    main()
