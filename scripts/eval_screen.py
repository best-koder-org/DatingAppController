#!/usr/bin/env python3
"""
Eval v2 — Quality gate for generated Flutter & backend code.

Produces a scored report card (0-100) covering:
  1. Compilation    — does flutter analyze / dotnet build pass?
  2. Size & shape   — line count, nesting depth, method count
  3. Completeness   — acceptance criteria vs TODO count
  4. Design system  — theme, patterns appropriate to file TYPE
  5. Test quality   — companion test exists, assertion density
  6. Accessibility  — Semantics / label usage
  7. Code smells    — magic numbers, print statements, commented code

Supports task type detection:
  - "wizard-screen" → full onboarding eval (progress bar, nav, Next button)
  - "widget"        → standalone widget eval (no wizard chrome required)
  - "backend"       → .NET eval (namespace, DI pattern, XML docs)
  - "screen"        → generic screen eval

Output: JSON + Markdown suitable for PR body injection.
"""
import json, re, subprocess, sys, os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

# ── Scoring weights (total = 100) ────────────────────────────────────
WEIGHTS = {
    "compilation":   25,
    "size_shape":    10,
    "completeness":  25,
    "design_system": 15,
    "test_quality":  10,
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
    file_type: str = "screen"  # wizard-screen | widget | backend | screen
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
        elif self.total_score >= 80: self.grade = "B"
        elif self.total_score >= 65: self.grade = "C"
        elif self.total_score >= 40: self.grade = "D"
        else: self.grade = "F"

    def to_markdown(self) -> str:
        self.compute_total()
        grade_emoji = {"A": "🟢", "B": "🔵", "C": "🟡", "D": "🟠", "F": "🔴"}
        emoji = grade_emoji.get(self.grade, "⚪")

        md = f"## {emoji} Eval: {self.total_score}/100 (Grade {self.grade})\n"
        md += f"*File type: {self.file_type}*\n\n"

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

        md += f"\n---\n*Eval v2 — auto-scored by eval_screen.py*\n"
        return md

    def to_json(self) -> str:
        self.compute_total()
        return json.dumps({
            "task_id": self.task_id,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "total_score": self.total_score,
            "grade": self.grade,
            "checks": self.checks,
        }, indent=2)


# ── File type detection ──────────────────────────────────────────────

def detect_file_type(file_path: str, task: Optional[dict] = None) -> str:
    """Detect type: wizard-screen, widget, backend, or screen."""
    p = file_path.lower()
    if task:
        t = task.get("type", "").lower()
        title = task.get("title", "").lower()
        fp = task.get("filePath", "").lower()

        if t == "backend" or p.endswith(".cs"):
            return "backend"
        # Widget = lives in lib/widgets/ or title says widget/ring/badge/button
        if "widget" in fp or "/widgets/" in fp:
            return "widget"
        if any(w in title for w in ["widget", "ring", "badge", "button", "card", "indicator"]):
            return "widget"
        # Wizard screen = lives in screens/wizard/ or screens/onboarding/
        if "wizard" in fp or "onboarding" in fp:
            return "wizard-screen"

    if p.endswith(".cs"):
        return "backend"
    if "/widgets/" in p:
        return "widget"
    if "/wizard/" in p or "/onboarding/" in p:
        return "wizard-screen"
    return "screen"


# ── Individual eval functions ────────────────────────────────────────

def eval_compilation(report: EvalReport, file_path: Path, repo_dir: Optional[Path]):
    """Run flutter analyze or dotnet build on the file."""
    if report.file_type == "backend":
        if repo_dir and repo_dir.exists():
            # Auto-detect .sln or .csproj to avoid ambiguity in multi-project repos
            sln_files = list(repo_dir.glob("*.sln"))
            csproj_files = list(repo_dir.glob("*.csproj"))
            # Use .name only since we cwd into repo_dir
            build_target = sln_files[0].name if sln_files else (csproj_files[0].name if csproj_files else "")
            build_cmd = f'dotnet build "{build_target}" --configuration Release' if build_target else "dotnet build --configuration Release"
            r = subprocess.run(
                build_cmd,
                shell=True, cwd=repo_dir, capture_output=True, text=True, timeout=180
            )
            if r.returncode == 0:
                report.add("compilation", EvalCheck("dotnet build", True, 1.0, "Build succeeded"))
            else:
                errors = r.stderr.count("error") + r.stdout.count(": error")
                report.add("compilation", EvalCheck("dotnet build", False, 0.0,
                    f"Build failed with {errors} errors", "fail"))
        else:
            report.add("compilation", EvalCheck("build check", True, 0.5,
                "No repo dir available for build", "warn"))
        return

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
        report.add("compilation", EvalCheck("syntax check", True, 0.5,
            "Flutter not available, syntax only", "warn"))


def eval_size_shape(report: EvalReport, content: str, lines: list):
    """Check file size, nesting depth, method count."""
    line_count = len(lines)

    # Size thresholds depend on file type
    if report.file_type == "widget":
        ideal, acceptable, too_large = 100, 200, 350
    elif report.file_type == "backend":
        ideal, acceptable, too_large = 200, 400, 600
    else:
        ideal, acceptable, too_large = 150, 300, 500

    if line_count <= ideal:
        report.add("size_shape", EvalCheck("line count", True, 1.0,
            f"{line_count} lines (ideal: ≤{ideal})"))
    elif line_count <= acceptable:
        report.add("size_shape", EvalCheck("line count", True, 0.7,
            f"{line_count} lines (acceptable: ≤{acceptable})", "warn"))
    elif line_count <= too_large:
        report.add("size_shape", EvalCheck("line count", False, 0.4,
            f"{line_count} lines (consider splitting)", "warn"))
    else:
        report.add("size_shape", EvalCheck("line count", False, 0.1,
            f"{line_count} lines (way too large!)", "fail"))

    # Max nesting depth
    max_indent = 0
    for line in lines:
        stripped = line.lstrip()
        if stripped:
            indent = len(line) - len(stripped)
            max_indent = max(max_indent, indent // 2)

    if max_indent <= 8:
        report.add("size_shape", EvalCheck("nesting depth", True, 1.0,
            f"Max {max_indent} levels (good)"))
    elif max_indent <= 12:
        report.add("size_shape", EvalCheck("nesting depth", True, 0.7,
            f"Max {max_indent} levels (acceptable)", "info"))
    else:
        report.add("size_shape", EvalCheck("nesting depth", False, 0.3,
            f"Max {max_indent} levels (too deep!)", "fail"))

    # Method/function count — improved regex for Dart and C#
    if report.file_type == "backend":
        methods = len(re.findall(r'(?:public|private|protected|internal|async)\s+\w+.*?\(', content))
    else:
        # Dart: match actual method/function declarations
        methods = len(re.findall(r'(?:void|Widget|State|Future|String|int|double|bool|List|Map|dynamic|@override)\s+\w+\s*\(', content))

    limit_good, limit_ok = (12, 20) if report.file_type == "backend" else (8, 15)
    report.add("size_shape", EvalCheck("method count", methods <= limit_ok,
        1.0 if methods <= limit_good else 0.7 if methods <= limit_ok else 0.3,
        f"{methods} methods/functions"))


def eval_completeness(report: EvalReport, content: str, task: Optional[dict]):
    """Check acceptance criteria coverage and TODO count."""
    todo_count = content.lower().count("todo")
    if todo_count == 0:
        report.add("completeness", EvalCheck("no TODOs", True, 1.0, "Zero TODOs — fully implemented"))
    elif todo_count <= 1:
        report.add("completeness", EvalCheck("TODOs remaining", True, 0.7,
            f"{todo_count} TODO found (minor gap)", "info"))
    elif todo_count <= 3:
        report.add("completeness", EvalCheck("TODOs remaining", False, 0.4,
            f"{todo_count} TODOs found (needs work)", "warn"))
    else:
        report.add("completeness", EvalCheck("TODOs remaining", False, 0.1,
            f"{todo_count} TODOs found (mostly unimplemented)", "fail"))

    if task:
        criteria = task.get("acceptanceCriteria", [])
        if criteria:
            hits = 0
            for c in criteria:
                # Multi-strategy matching:
                # 1. PascalCase identifiers (ProfileCompletenessRing, StatelessWidget)
                pascal_words = re.findall(r'[A-Z][a-zA-Z]+(?:[A-Z][a-z]+)+', c)
                # 2. Quoted terms ('Show me')
                quoted = re.findall(r"'([^']+)'", c)
                # 3. Key technical terms (3+ char words, skip articles/prepositions)
                skip = {'the','and','for','with','from','that','this','are','was','has','have',
                        'not','but','all','can','should','must','does','pass','without','errors'}
                words = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', c)
                         if w.lower() not in skip]

                # Try PascalCase identifiers first (most specific)
                matched = False
                for pw in pascal_words:
                    if pw.lower() in content.lower():
                        matched = True
                        break
                # Then quoted terms
                if not matched:
                    for qt in quoted:
                        if qt.lower() in content.lower():
                            matched = True
                            break
                # Then any 2+ key words present
                if not matched:
                    word_hits = sum(1 for w in words if w.lower() in content.lower())
                    if word_hits >= 2:
                        matched = True
                if matched:
                    hits += 1

            ratio = hits / len(criteria) if criteria else 0
            report.add("completeness", EvalCheck("acceptance criteria",
                ratio >= 0.5, ratio,
                f"{hits}/{len(criteria)} criteria have matching code"))
    else:
        report.add("completeness", EvalCheck("acceptance criteria", True, 0.5,
            "No task definition to check against", "info"))


def eval_design_system(report: EvalReport, content: str):
    """Check design system adherence — context-aware by file type."""

    if report.file_type == "backend":
        # .NET design system: namespace, DI, XML docs
        has_namespace = "namespace " in content
        report.add("design_system", EvalCheck("namespace declaration", has_namespace,
            1.0 if has_namespace else 0.0, 
            "Has namespace" if has_namespace else "Missing namespace", "fail" if not has_namespace else "info"))
        has_xml_doc = "/// <summary>" in content or "/// " in content
        report.add("design_system", EvalCheck("XML documentation", has_xml_doc,
            1.0 if has_xml_doc else 0.3,
            "Has XML docs" if has_xml_doc else "Missing XML documentation", "warn"))
        # Interface / DI pattern
        has_interface = re.search(r'(?:interface|I[A-Z]\w+Service|I[A-Z]\w+Repository)', content) is not None
        report.add("design_system", EvalCheck("interface/DI pattern", has_interface,
            1.0 if has_interface else 0.5,
            "Has interface for DI" if has_interface else "No interface found (consider DI)", "info"))
        return

    # ── Flutter: coral theme is universal ──
    has_coral = "0xFFFF6B6B" in content or "FF6B6B" in content or "Color(0xFF" in content
    report.add("design_system", EvalCheck("theme colors", has_coral,
        1.0 if has_coral else 0.3,
        "Uses app theme colors" if has_coral else "No theme colors found",
        "info" if has_coral else "warn"))

    if report.file_type == "widget":
        # Widgets: check for proper widget structure, no wizard chrome needed
        is_stateless = "StatelessWidget" in content
        is_stateful = "StatefulWidget" in content
        has_widget = is_stateless or is_stateful
        report.add("design_system", EvalCheck("widget class", has_widget,
            1.0 if has_widget else 0.0,
            f"{'Stateless' if is_stateless else 'Stateful'} widget" if has_widget else "No widget class found",
            "fail" if not has_widget else "info"))

        # Reusable API: takes parameters
        has_constructor_params = re.search(r'const \w+\(\{.*\}\)', content, re.DOTALL) is not None
        report.add("design_system", EvalCheck("configurable API", has_constructor_params,
            1.0 if has_constructor_params else 0.5,
            "Widget accepts parameters" if has_constructor_params else "No constructor params (not reusable?)",
            "info"))

    elif report.file_type == "wizard-screen":
        # Full wizard: progress bar, nav, Next button
        has_progress = "LinearProgressIndicator" in content or "ProgressBar" in content
        report.add("design_system", EvalCheck("progress bar", has_progress,
            1.0 if has_progress else 0.0,
            "Has progress indicator" if has_progress else "Missing progress bar", "warn"))

        has_back = "arrow_back" in content or "Icons.arrow_back" in content
        has_close = "Icons.close" in content
        has_nav = has_back and has_close
        report.add("design_system", EvalCheck("back + close nav", has_nav,
            1.0 if has_nav else 0.5 if (has_back or has_close) else 0.0,
            f"{'✓ back' if has_back else '✗ back'}, {'✓ close' if has_close else '✗ close'}"))

        has_next = "Next" in content and ("ElevatedButton" in content or "TextButton" in content)
        report.add("design_system", EvalCheck("Next button", has_next,
            1.0 if has_next else 0.0,
            "Has Next button" if has_next else "Missing Next button pattern"))

        has_validation = "onPressed:" in content and "null" in content
        report.add("design_system", EvalCheck("validation gating", has_validation,
            1.0 if has_validation else 0.3,
            "Button disables when invalid" if has_validation else "No disable pattern found", "warn"))

    else:
        # Generic screen: just check for Scaffold + basic structure
        has_scaffold = "Scaffold" in content
        report.add("design_system", EvalCheck("Scaffold usage", has_scaffold,
            1.0 if has_scaffold else 0.3,
            "Has Scaffold" if has_scaffold else "No Scaffold found"))


def eval_test_quality(report: EvalReport, file_path: Path, repo_dir: Optional[Path]):
    """Check companion test file quality."""
    if report.file_type == "backend":
        # Backend: just check if test project exists (we don't generate backend tests yet)
        report.add("test_quality", EvalCheck("build passes as test", True, 0.8,
            "Backend: build success = baseline quality gate", "info"))
        return

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

    test_count = test_content.count("testWidgets") + test_content.count("test(")
    report.add("test_quality", EvalCheck("test count", test_count >= 3,
        1.0 if test_count >= 5 else 0.7 if test_count >= 3 else 0.3,
        f"{test_count} tests"))

    expect_count = test_content.count("expect(")
    report.add("test_quality", EvalCheck("assertions", expect_count >= 3,
        1.0 if expect_count >= 6 else 0.7 if expect_count >= 3 else 0.2,
        f"{expect_count} expect() assertions"))

    # Check tests are feature-specific (not just "renders" and "has Next button")
    generic_patterns = ["findsOneWidget", "find.text('Next')", "isNull"]
    feature_tests = [line for line in test_content.splitlines()
                     if "expect(" in line and not any(gp in line for gp in generic_patterns)]
    feature_score = min(1.0, len(feature_tests) / 3)
    report.add("test_quality", EvalCheck("feature-specific tests",
        len(feature_tests) >= 2, feature_score,
        f"{len(feature_tests)} feature-specific assertions (not just boilerplate)"))


def eval_accessibility(report: EvalReport, content: str):
    """Check accessibility basics."""
    if report.file_type == "backend":
        report.add("accessibility", EvalCheck("N/A for backend", True, 1.0,
            "Accessibility not applicable to backend code"))
        return

    has_semantics = "Semantics" in content or "semanticsLabel" in content or "tooltip" in content.lower()
    report.add("accessibility", EvalCheck("semantics", has_semantics,
        1.0 if has_semantics else 0.4,
        "Has Semantics/labels" if has_semantics else "No Semantics widgets (screen reader gap)",
        "info" if has_semantics else "warn"))

    has_text_style = "TextStyle" in content or "Theme.of" in content
    report.add("accessibility", EvalCheck("text styling", has_text_style,
        1.0 if has_text_style else 0.5,
        "Uses TextStyle/Theme" if has_text_style else "No text styling found"))


def eval_code_smells(report: EvalReport, content: str, lines: list):
    """Check for common code smells."""
    # Magic numbers
    magic_re = re.findall(r'(?<!const\s)(?:=|:)\s*(\d+\.?\d*)', content)
    common = {"0", "0.0", "1", "1.0", "2", "2.0", "3", "4", "5", "6", "8", "10",
              "12", "14", "16", "18", "20", "24", "26", "27", "28", "32", "40",
              "48", "52", "54", "56", "64", "100", "200", "300", "0.5", "0.7", "0.45"}
    magic = [m for m in magic_re if m not in common and float(m) > 2]
    report.add("code_smells", EvalCheck("magic numbers", len(magic) <= 5,
        1.0 if len(magic) == 0 else 0.8 if len(magic) <= 5 else 0.4,
        f"{len(magic)} uncommon literal numbers" + (f" ({', '.join(magic[:5])})" if magic else "")))

    # Print/debug statements
    prints = content.count("print(")
    report.add("code_smells", EvalCheck("no print()", prints <= 1,
        1.0 if prints == 0 else 0.7 if prints <= 1 else 0.3,
        f"{prints} print() calls" + (" (consider removing)" if prints else ""),
        "info" if prints == 0 else "warn"))

    # Commented-out code
    commented = sum(1 for l in lines if l.strip().startswith("//") and
                    not l.strip().startswith("///") and
                    any(kw in l for kw in ["=", "(", ")", "{", "}", "return", "import"]))
    report.add("code_smells", EvalCheck("commented code", commented <= 3,
        1.0 if commented == 0 else 0.8 if commented <= 3 else 0.3,
        f"{commented} lines of commented-out code"))


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

    file_type = detect_file_type(file_path, task)

    report = EvalReport(
        task_id=task["id"] if task else path.stem,
        file_path=str(file_path),
        file_type=file_type,
    )

    eval_compilation(report, path, repo)
    eval_size_shape(report, content, lines)
    eval_completeness(report, content, task)
    eval_design_system(report, content)
    eval_test_quality(report, Path(file_path), repo)
    eval_accessibility(report, content)
    eval_code_smells(report, content, lines)

    report.compute_total()
    if report.total_score >= 85:
        report.summary_lines.append("🏆 High quality — ready for review")
    elif report.total_score >= 70:
        report.summary_lines.append("👍 Solid implementation — minor improvements possible")
    elif report.total_score >= 50:
        report.summary_lines.append("🔨 Functional but needs refinement")
    else:
        report.summary_lines.append("⚠️ Scaffold only — needs real implementation")

    failed = [c for c in report.checks if not c["passed"]]
    if failed:
        report.summary_lines.append(f"📋 {len(failed)} checks need attention")
        for f in failed[:3]:
            report.summary_lines.append(f"  → {f['name']}: {f['detail']}")

    return report


def main():
    """CLI: eval_screen.py <file> [--task-json <file>] [--repo-dir <dir>] [--format md|json]"""
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate a Flutter/backend file")
    parser.add_argument("file", help="Path to the file to evaluate")
    parser.add_argument("--task-json", help="Path to task-queue.json")
    parser.add_argument("--task-id", help="Specific task ID to match in queue")
    parser.add_argument("--repo-dir", help="Path to the repo root")
    parser.add_argument("--format", choices=["md", "json", "both"], default="both")
    parser.add_argument("--output", help="Write report to file (otherwise stdout)")
    args = parser.parse_args()

    task = None
    if args.task_json:
        with open(args.task_json) as f:
            queue_data = json.load(f)
        all_tasks = queue_data.get("queue", []) + queue_data.get("inProgress", []) + queue_data.get("completed", [])
        if args.task_id:
            task = next((t for t in all_tasks if t["id"] == args.task_id), None)
        else:
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
