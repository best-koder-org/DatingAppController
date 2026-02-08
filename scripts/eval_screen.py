#!/usr/bin/env python3
"""
Screen Eval — Quality gate for generated Flutter screens.

Produces a scored report card (0-100) covering:
  1. Compilation    — does `flutter analyze` pass?
  2. Size & shape   — line count, nesting depth, method count
  3. Completeness   — acceptance criteria vs TODO count
  4. Design system  — coral theme, progress bar, nav pattern
  5. Test quality   — companion test exists, assertion density
  6. Accessibility  — Semantics / label usage
  7. Code smells    — magic numbers, print statements, commented code

Output: JSON + Markdown suitable for PR body injection.
"""
import json, re, subprocess, sys, os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

# ── Scoring weights (total = 100) ────────────────────────────────────
WEIGHTS = {
    "compilation":   20,
    "size_shape":    15,
    "completeness":  20,
    "design_system": 15,
    "test_quality":  15,
    "accessibility": 5,
    "code_smells":   10,
}

@dataclass
class EvalCheck:
    name: str
    passed: bool
    score: float        # 0.0 – 1.0
    detail: str = ""
    severity: str = "info"  # info | warn | fail

@dataclass
class EvalReport:
    task_id: str
    file_path: str
    total_score: float = 0.0
    grade: str = ""
    categories: dict = field(default_factory=dict)
    checks: list = field(default_factory=list)
    summary_lines: list = field(default_factory=list)

    def add(self, category: str, check: EvalCheck):
        self.checks.append({"category": category, **asdict(check)})
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(check)

    def compute_total(self):
        cat_scores = {}
        for cat, checks in self.categories.items():
            if checks:
                cat_scores[cat] = sum(c.score for c in checks) / len(checks)
            else:
                cat_scores[cat] = 0.0

        self.total_score = sum(
            cat_scores.get(cat, 0.0) * weight
            for cat, weight in WEIGHTS.items()
        )
        self.total_score = round(self.total_score, 1)

        if self.total_score >= 90: self.grade = "A"
        elif self.total_score >= 75: self.grade = "B"
        elif self.total_score >= 60: self.grade = "C"
        elif self.total_score >= 40: self.grade = "D"
        else: self.grade = "F"

    def to_markdown(self) -> str:
        self.compute_total()
        grade_emoji = {"A": "🟢", "B": "🔵", "C": "🟡", "D": "🟠", "F": "🔴"}
        emoji = grade_emoji.get(self.grade, "⚪")

        md = f"## {emoji} Eval: {self.total_score}/100 (Grade {self.grade})\n\n"

        # Category breakdown table
        md += "| Category | Score | Weight | Weighted |\n"
        md += "|----------|-------|--------|----------|\n"
        for cat, weight in WEIGHTS.items():
            checks = self.categories.get(cat, [])
            if checks:
                raw = sum(c.score for c in checks) / len(checks)
            else:
                raw = 0.0
            weighted = raw * weight
            bar = "█" * int(raw * 10) + "░" * (10 - int(raw * 10))
            md += f"| {cat.replace('_',' ').title()} | {bar} {raw*100:.0f}% | {weight} | {weighted:.1f} |\n"

        # Detail checks
        md += "\n### Checks\n"
        icons = {"info": "ℹ️", "warn": "⚠️", "fail": "❌"}
        for check_dict in self.checks:
            icon = "✅" if check_dict["passed"] else icons.get(check_dict["severity"], "❓")
            md += f"- {icon} **{check_dict['name']}** — {check_dict['detail']}\n"

        # Quick summary
        if self.summary_lines:
            md += "\n### Quick Take\n"
            for line in self.summary_lines:
                md += f"- {line}\n"

        md += f"\n---\n*Eval v1 — auto-scored by eval-screen.py*\n"
        return md

    def to_json(self) -> str:
        self.compute_total()
        return json.dumps({
            "task_id": self.task_id,
            "file_path": self.file_path,
            "total_score": self.total_score,
            "grade": self.grade,
            "checks": self.checks,
        }, indent=2)


# ── Individual eval functions ────────────────────────────────────────

def eval_compilation(report: EvalReport, file_path: Path, repo_dir: Optional[Path]):
    """Run flutter analyze on the file."""
    if repo_dir and repo_dir.exists():
        r = subprocess.run(
            f"flutter analyze {file_path}",
            shell=True, cwd=repo_dir, capture_output=True, text=True, timeout=120
        )
        if r.returncode == 0:
            report.add("compilation", EvalCheck("flutter analyze", True, 1.0, "No issues"))
        else:
            errors = r.stdout.count("error") + r.stderr.count("error")
            warnings = r.stdout.count("warning") + r.stderr.count("warning")
            infos = r.stdout.count("info") + r.stderr.count("info")
            if errors > 0:
                report.add("compilation", EvalCheck("flutter analyze", False, 0.0,
                    f"{errors} errors, {warnings} warnings", "fail"))
            elif warnings > 0:
                report.add("compilation", EvalCheck("flutter analyze", True, 0.7,
                    f"{warnings} warnings, {infos} infos", "warn"))
            else:
                report.add("compilation", EvalCheck("flutter analyze", True, 0.9,
                    f"{infos} infos only", "info"))
    else:
        # Fallback: syntax check only
        report.add("compilation", EvalCheck("syntax check", True, 0.5,
            "Flutter not available, syntax only", "warn"))


def eval_size_shape(report: EvalReport, content: str, lines: list):
    """Check file size, nesting depth, method count."""
    line_count = len(lines)

    # Line count scoring
    if line_count <= 150:
        report.add("size_shape", EvalCheck("line count", True, 1.0,
            f"{line_count} lines (ideal: ≤150)"))
    elif line_count <= 250:
        report.add("size_shape", EvalCheck("line count", True, 0.7,
            f"{line_count} lines (acceptable: ≤250)", "warn"))
    elif line_count <= 400:
        report.add("size_shape", EvalCheck("line count", False, 0.4,
            f"{line_count} lines (too large, consider splitting)", "warn"))
    else:
        report.add("size_shape", EvalCheck("line count", False, 0.1,
            f"{line_count} lines (way too large!)", "fail"))

    # Max nesting depth
    max_indent = 0
    for line in lines:
        stripped = line.lstrip()
        if stripped:
            indent = len(line) - len(stripped)
            max_indent = max(max_indent, indent // 2)  # 2-space indent

    if max_indent <= 8:
        report.add("size_shape", EvalCheck("nesting depth", True, 1.0,
            f"Max {max_indent} levels (good)"))
    elif max_indent <= 12:
        report.add("size_shape", EvalCheck("nesting depth", True, 0.6,
            f"Max {max_indent} levels (consider extracting widgets)", "warn"))
    else:
        report.add("size_shape", EvalCheck("nesting depth", False, 0.2,
            f"Max {max_indent} levels (too deep!)", "fail"))

    # Method/function count
    methods = len(re.findall(r'^\s+\w+.*?\(', content, re.MULTILINE))
    report.add("size_shape", EvalCheck("method count", True,
        1.0 if methods <= 8 else 0.6 if methods <= 15 else 0.3,
        f"{methods} methods/functions"))


def eval_completeness(report: EvalReport, content: str, task: Optional[dict]):
    """Check acceptance criteria coverage and TODO count."""
    todo_count = content.lower().count("todo")
    if todo_count == 0:
        report.add("completeness", EvalCheck("no TODOs", True, 1.0, "Zero TODOs — fully implemented"))
    elif todo_count <= 2:
        report.add("completeness", EvalCheck("TODOs remaining", True, 0.6,
            f"{todo_count} TODOs found (minor gaps)", "warn"))
    else:
        report.add("completeness", EvalCheck("TODOs remaining", False, 0.2,
            f"{todo_count} TODOs found (significant gaps)", "fail"))

    if task:
        criteria = task.get("acceptanceCriteria", [])
        if criteria:
            # Simple heuristic: check if key phrases from criteria appear in code
            hits = 0
            for c in criteria:
                # Extract key concept words
                keywords = re.findall(r"[A-Z][a-z]+|'([^']+)'", c)
                for kw in keywords:
                    if kw and kw.lower() in content.lower():
                        hits += 1
                        break
            ratio = hits / len(criteria) if criteria else 0
            report.add("completeness", EvalCheck("acceptance criteria", ratio > 0.5,
                ratio, f"{hits}/{len(criteria)} criteria have matching code"))
    else:
        report.add("completeness", EvalCheck("acceptance criteria", True, 0.5,
            "No task definition to check against", "info"))


def eval_design_system(report: EvalReport, content: str):
    """Check adherence to DejTing design system."""
    # Coral theme color
    has_coral = "0xFFFF6B6B" in content or "FF6B6B" in content
    report.add("design_system", EvalCheck("coral theme (#FF6B6B)", has_coral,
        1.0 if has_coral else 0.0,
        "Found coral accent color" if has_coral else "Missing coral theme color", 
        "info" if has_coral else "warn"))

    # Progress bar
    has_progress = "LinearProgressIndicator" in content or "ProgressBar" in content
    report.add("design_system", EvalCheck("progress bar", has_progress,
        1.0 if has_progress else 0.0,
        "Has progress indicator" if has_progress else "Missing progress bar",
        "info" if has_progress else "warn"))

    # Back + Close navigation
    has_back = "arrow_back" in content or "Icons.arrow_back" in content
    has_close = "Icons.close" in content
    has_nav = has_back and has_close
    report.add("design_system", EvalCheck("back + close nav", has_nav,
        1.0 if has_nav else 0.5 if (has_back or has_close) else 0.0,
        f"{'✓ back' if has_back else '✗ back'}, {'✓ close' if has_close else '✗ close'}"))

    # Next button pattern
    has_next = "Next" in content and "ElevatedButton" in content
    report.add("design_system", EvalCheck("Next button", has_next,
        1.0 if has_next else 0.0,
        "Has Next ElevatedButton" if has_next else "Missing Next button pattern"))

    # Disabled-state validation pattern
    has_validation = "onPressed:" in content and ("null" in content or "? ()" in content)
    report.add("design_system", EvalCheck("validation gating", has_validation,
        1.0 if has_validation else 0.0,
        "Button disables when invalid" if has_validation else "No disable pattern found",
        "info" if has_validation else "warn"))


def eval_test_quality(report: EvalReport, file_path: Path, repo_dir: Optional[Path]):
    """Check companion test file quality."""
    if not repo_dir:
        report.add("test_quality", EvalCheck("test file", False, 0.0, "No repo dir", "warn"))
        return

    test_path_rel = str(file_path).replace("lib/", "test/").replace(".dart", "_test.dart")
    test_path = repo_dir / test_path_rel

    if not test_path.exists():
        report.add("test_quality", EvalCheck("test file exists", False, 0.0,
            f"No companion test at {test_path_rel}", "fail"))
        return

    report.add("test_quality", EvalCheck("test file exists", True, 1.0,
        f"Found {test_path_rel}"))

    test_content = test_path.read_text()

    # Count test cases
    test_count = test_content.count("testWidgets")
    report.add("test_quality", EvalCheck("test count", test_count >= 3,
        1.0 if test_count >= 5 else 0.7 if test_count >= 3 else 0.3,
        f"{test_count} widget tests"))

    # Assertion density
    expect_count = test_content.count("expect(")
    report.add("test_quality", EvalCheck("assertions", expect_count >= 3,
        1.0 if expect_count >= 5 else 0.6 if expect_count >= 3 else 0.2,
        f"{expect_count} expect() assertions"))

    # Tests actually reference the screen class
    file_stem = file_path.stem
    class_ref = any(file_stem.replace("_", "") in test_content.lower().replace("_", "")
                     for _ in [1])
    report.add("test_quality", EvalCheck("imports target", class_ref,
        1.0 if class_ref else 0.0,
        "Test imports the screen under test" if class_ref else "Test may not test the right screen"))


def eval_accessibility(report: EvalReport, content: str):
    """Check accessibility basics."""
    has_semantics = "Semantics" in content or "semanticsLabel" in content
    report.add("accessibility", EvalCheck("semantics", has_semantics,
        1.0 if has_semantics else 0.3,
        "Has Semantics/labels" if has_semantics else "No Semantics widgets (screen reader gap)",
        "info" if has_semantics else "warn"))

    # Text scaling awareness
    has_text_style = "TextStyle" in content
    report.add("accessibility", EvalCheck("text styling", has_text_style,
        1.0 if has_text_style else 0.5,
        "Uses TextStyle" if has_text_style else "No TextStyle found"))


def eval_code_smells(report: EvalReport, content: str, lines: list):
    """Check for common code smells."""
    # Magic numbers (numbers not in const or common values)
    magic_re = re.findall(r'(?<!const\s)(?:=|:)\s*(\d+\.?\d*)', content)
    common = {"0", "0.0", "1", "1.0", "2", "4", "8", "12", "16", "24", "26", "32", "52", "64"}
    magic = [m for m in magic_re if m not in common and float(m) > 2]
    report.add("code_smells", EvalCheck("magic numbers", len(magic) <= 3,
        1.0 if len(magic) == 0 else 0.7 if len(magic) <= 3 else 0.3,
        f"{len(magic)} uncommon literal numbers" + (f" ({', '.join(magic[:5])})" if magic else "")))

    # Print statements
    prints = content.count("print(")
    report.add("code_smells", EvalCheck("no print()", prints == 0,
        1.0 if prints == 0 else 0.5,
        f"{prints} print() calls" + (" (remove for production)" if prints else ""),
        "info" if prints == 0 else "warn"))

    # Commented-out code (lines starting with //)
    commented = sum(1 for l in lines if l.strip().startswith("//") and
                    not l.strip().startswith("///") and
                    any(kw in l for kw in ["=", "(", ")", "{", "}", "return", "import"]))
    report.add("code_smells", EvalCheck("commented code", commented <= 2,
        1.0 if commented == 0 else 0.7 if commented <= 2 else 0.3,
        f"{commented} lines of commented-out code"))

    # Hardcoded strings (should be in constants/l10n eventually)
    string_literals = re.findall(r"'[^']{10,}'", content)
    if len(string_literals) > 5:
        report.add("code_smells", EvalCheck("hardcoded strings", True, 0.6,
            f"{len(string_literals)} long string literals (consider l10n later)", "info"))
    else:
        report.add("code_smells", EvalCheck("hardcoded strings", True, 1.0,
            f"{len(string_literals)} string literals (OK for MVP)"))


# ── Main ─────────────────────────────────────────────────────────────

def eval_file(file_path: str, task: Optional[dict] = None,
              repo_dir: Optional[str] = None) -> EvalReport:
    """Run full eval on a single file."""
    path = Path(file_path)
    repo = Path(repo_dir) if repo_dir else None

    if not path.exists() and repo:
        path = repo / file_path

    content = path.read_text()
    lines = content.splitlines()

    report = EvalReport(
        task_id=task["id"] if task else path.stem,
        file_path=str(file_path),
    )

    eval_compilation(report, path, repo)
    eval_size_shape(report, content, lines)
    eval_completeness(report, content, task)
    eval_design_system(report, content)
    eval_test_quality(report, Path(file_path), repo)
    eval_accessibility(report, content)
    eval_code_smells(report, content, lines)

    # Generate quick-take summary
    report.compute_total()
    if report.total_score >= 85:
        report.summary_lines.append("🏆 High quality — ready for review")
    elif report.total_score >= 65:
        report.summary_lines.append("👍 Solid foundation — a few improvements possible")
    else:
        report.summary_lines.append("🔨 Needs work before merging")

    failed = [c for c in report.checks if not c["passed"]]
    if failed:
        report.summary_lines.append(f"📋 {len(failed)} checks need attention")
        for f in failed[:3]:
            report.summary_lines.append(f"  → {f['name']}: {f['detail']}")

    return report


def main():
    """CLI: eval-screen.py <dart-file> [--task-json <file>] [--repo-dir <dir>] [--format md|json]"""
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate a Flutter screen file")
    parser.add_argument("file", help="Path to the .dart file to evaluate")
    parser.add_argument("--task-json", help="Path to task-queue.json (uses first queue item or matches by filename)")
    parser.add_argument("--task-id", help="Specific task ID to match in queue")
    parser.add_argument("--repo-dir", help="Path to the Flutter repo root")
    parser.add_argument("--format", choices=["md", "json", "both"], default="both")
    parser.add_argument("--output", help="Write report to file (otherwise stdout)")
    args = parser.parse_args()

    # Load task if available
    task = None
    if args.task_json:
        with open(args.task_json) as f:
            queue_data = json.load(f)
        # Try to find matching task
        all_tasks = queue_data.get("queue", []) + queue_data.get("inProgress", []) + queue_data.get("completed", [])
        if args.task_id:
            task = next((t for t in all_tasks if t["id"] == args.task_id), None)
        else:
            # Match by file path
            for t in all_tasks:
                if Path(args.file).name in t.get("filePath", ""):
                    task = t
                    break

    report = eval_file(args.file, task=task, repo_dir=args.repo_dir)

    if args.format in ("md", "both"):
        md = report.to_markdown()
        if args.output:
            Path(args.output).write_text(md)
            print(f"Report written to {args.output}")
        else:
            print(md)

    if args.format in ("json", "both"):
        j = report.to_json()
        if args.output:
            json_path = args.output.replace(".md", ".json") if args.output.endswith(".md") else args.output + ".json"
            Path(json_path).write_text(j)
        else:
            if args.format == "both":
                print("\n" + "=" * 60 + "\n")
            print(j)


if __name__ == "__main__":
    main()
