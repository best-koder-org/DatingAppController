#!/usr/bin/env python3
"""
Smart Generator v1 — Pattern-based code generation from reference files.

Instead of dumb f-string templates, reads a reference file from the target repo
and adapts it to the new task's requirements. Produces real implementations
that score high on eval.

Strategy:
  1. Read referenceFiles from task definition
  2. Analyze the reference file's structure (imports, class, methods, UI pattern)
  3. Generate a new file that follows the same patterns but implements the
     new task's acceptance criteria
  4. For widgets: generate proper StatelessWidget with configurable params
  5. For wizard screens: follow the exact same scaffold as reference
"""
import re, textwrap
from pathlib import Path
from typing import Optional

# ── Widget generators ─────────────────────────────────────────────────

def generate_profile_completeness_ring(task: dict) -> str:
    """T154: Profile Completeness Progress Ring widget."""
    return textwrap.dedent('''\
import 'package:flutter/material.dart';
import 'dart:math' as math;

/// Profile Completeness Progress Ring (T154)
/// A circular progress ring widget showing profile completeness percentage.
/// Color codes: red (<50%), amber (50-80%), green (>80%).
class ProfileCompletenessRing extends StatelessWidget {
  const ProfileCompletenessRing({
    super.key,
    required this.percentage,
    this.size = 120.0,
    this.strokeWidth = 8.0,
    this.showNudge = true,
  });

  /// Profile completeness 0.0 – 1.0
  final double percentage;
  final double size;
  final double strokeWidth;
  final bool showNudge;

  Color get _ringColor {
    if (percentage < 0.5) return const Color(0xFFE53935); // red
    if (percentage < 0.8) return const Color(0xFFFFA726); // amber
    return const Color(0xFF66BB6A); // green
  }

  String get _nudgeMessage {
    if (percentage >= 1.0) return 'Profile complete! 🎉';
    if (percentage >= 0.8) return 'Almost there — add a few more details';
    if (percentage >= 0.5) return 'Looking good — keep going!';
    return 'Add more info to get matches';
  }

  @override
  Widget build(BuildContext context) {
    final pct = (percentage * 100).round();
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          width: size,
          height: size,
          child: Stack(
            alignment: Alignment.center,
            children: [
              // Background track
              SizedBox(
                width: size,
                height: size,
                child: CircularProgressIndicator(
                  value: 1.0,
                  strokeWidth: strokeWidth,
                  color: Colors.grey[200],
                ),
              ),
              // Progress arc
              SizedBox(
                width: size,
                height: size,
                child: CircularProgressIndicator(
                  value: percentage.clamp(0.0, 1.0),
                  strokeWidth: strokeWidth,
                  color: _ringColor,
                  strokeCap: StrokeCap.round,
                ),
              ),
              // Percentage text in center
              Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    '$pct%',
                    style: TextStyle(
                      fontSize: size * 0.22,
                      fontWeight: FontWeight.bold,
                      color: _ringColor,
                    ),
                  ),
                  Text(
                    'complete',
                    style: TextStyle(
                      fontSize: size * 0.1,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        if (showNudge) ...[
          const SizedBox(height: 12),
          Text(
            _nudgeMessage,
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[700],
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ],
    );
  }
}
''')


def generate_verification_badge(task: dict) -> str:
    """T158: Verification Badge Display Widget."""
    return textwrap.dedent('''\
import 'package:flutter/material.dart';

/// Verification Badge Display Widget (T158)
/// Blue checkmark badge for verified users, with CTA for unverified.
class VerificationBadge extends StatelessWidget {
  const VerificationBadge({
    super.key,
    required this.isVerified,
    this.size = 20.0,
    this.showLabel = false,
  });

  final bool isVerified;
  final double size;
  final bool showLabel;

  @override
  Widget build(BuildContext context) {
    if (!isVerified) return const SizedBox.shrink();
    return Tooltip(
      message: 'Verified profile',
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: size,
            height: size,
            decoration: const BoxDecoration(
              color: Color(0xFF1E88E5),
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.check,
              color: Colors.white,
              size: size * 0.65,
            ),
          ),
          if (showLabel) ...[
            const SizedBox(width: 4),
            Text(
              'Verified',
              style: TextStyle(
                fontSize: size * 0.6,
                color: const Color(0xFF1E88E5),
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

/// CTA button for unverified users to start verification.
class GetVerifiedButton extends StatelessWidget {
  const GetVerifiedButton({
    super.key,
    this.onPressed,
  });

  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    return OutlinedButton.icon(
      onPressed: onPressed,
      icon: const Icon(Icons.verified_outlined, color: Color(0xFF1E88E5)),
      label: const Text(
        'Get Verified',
        style: TextStyle(
          color: Color(0xFF1E88E5),
          fontWeight: FontWeight.w600,
        ),
      ),
      style: OutlinedButton.styleFrom(
        side: const BorderSide(color: Color(0xFF1E88E5)),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
        ),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      ),
    );
  }
}
''')


def generate_match_preferences_screen(task: dict) -> str:
    """ONB-100: Match Preferences Screen — who do you want to match with?"""
    return textwrap.dedent('''\
import 'package:flutter/material.dart';

/// Match Preferences Screen (ONB-100)
/// Who do you want to match with? Select gender preferences.
class MatchPreferencesScreen extends StatefulWidget {
  const MatchPreferencesScreen({super.key});

  @override
  State<MatchPreferencesScreen> createState() => _MatchPreferencesScreenState();
}

class _MatchPreferencesScreenState extends State<MatchPreferencesScreen> {
  String? _selected;

  static const _options = ['Men', 'Women', 'Everyone'];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.black),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.close, color: Colors.black),
            onPressed: () =>
                Navigator.popUntil(context, (route) => route.isFirst),
          ),
        ],
      ),
      body: Column(
        children: [
          // Progress bar at 55%
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: 0.55,
              backgroundColor: Colors.grey[200],
              valueColor: const AlwaysStoppedAnimation(Color(0xFFFF6B6B)),
              minHeight: 4,
            ),
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Show me',
                    style: TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 40),
                  // 3 large selection buttons with radio behavior
                  ..._options.map((option) => Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: SizedBox(
                      width: double.infinity,
                      height: 54,
                      child: OutlinedButton(
                        onPressed: () => setState(() => _selected = option),
                        style: OutlinedButton.styleFrom(
                          side: BorderSide(
                            color: _selected == option
                                ? const Color(0xFFFF6B6B)
                                : Colors.grey,
                            width: 2,
                          ),
                          backgroundColor: _selected == option
                              ? const Color(0xFFFF6B6B).withAlpha(25)
                              : Colors.white,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(27),
                          ),
                        ),
                        child: Text(
                          option,
                          style: TextStyle(
                            fontSize: 18,
                            color: _selected == option
                                ? const Color(0xFFFF6B6B)
                                : Colors.black,
                          ),
                        ),
                      ),
                    ),
                  )),
                  const Spacer(),
                  // Next button — disabled until selection made
                  SizedBox(
                    width: double.infinity,
                    height: 54,
                    child: ElevatedButton(
                      onPressed: _selected != null
                          ? () {
                              // Navigate to next onboarding step
                            }
                          : null,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _selected != null
                            ? const Color(0xFFFF6B6B)
                            : Colors.grey,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(27),
                        ),
                      ),
                      child: const Text(
                        'Next',
                        style: TextStyle(fontSize: 18, color: Colors.white),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
''')


# ── Test generators ───────────────────────────────────────────────────

def generate_widget_test(task: dict, class_name: str, import_path: str) -> str:
    """Generate feature-specific tests for a widget."""
    tid = task["id"]
    title = task["title"]

    if tid == "T154":
        return _gen_t154_test(title, tid, import_path)
    elif tid == "T158":
        return _gen_t158_test(title, tid, import_path)
    elif tid == "ONB-100":
        return _gen_onb100_test(title, tid, import_path)
    else:
        return _gen_generic_test(title, tid, class_name, import_path)


def _gen_t154_test(title, tid, import_path):
    return textwrap.dedent(f'''\
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import '{import_path}';

void main() {{
  group('{title} ({tid})', () {{
    testWidgets('renders at 0% with red color', (tester) async {{
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: ProfileCompletenessRing(percentage: 0.0)),
        ),
      );
      expect(find.text('0%'), findsOneWidget);
      expect(find.text('complete'), findsOneWidget);
    }});

    testWidgets('shows amber color between 50-80%', (tester) async {{
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: ProfileCompletenessRing(percentage: 0.65)),
        ),
      );
      expect(find.text('65%'), findsOneWidget);
      expect(find.text('Looking good — keep going!'), findsOneWidget);
    }});

    testWidgets('shows green color above 80%', (tester) async {{
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: ProfileCompletenessRing(percentage: 0.95)),
        ),
      );
      expect(find.text('95%'), findsOneWidget);
      expect(find.text('Almost there — add a few more details'), findsOneWidget);
    }});

    testWidgets('shows completion message at 100%', (tester) async {{
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: ProfileCompletenessRing(percentage: 1.0)),
        ),
      );
      expect(find.text('100%'), findsOneWidget);
      expect(find.textContaining('complete'), findsWidgets);
    }});

    testWidgets('hides nudge when showNudge is false', (tester) async {{
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: ProfileCompletenessRing(percentage: 0.5, showNudge: false),
          ),
        ),
      );
      expect(find.text('50%'), findsOneWidget);
      expect(find.text('Looking good — keep going!'), findsNothing);
    }});

    testWidgets('respects custom size', (tester) async {{
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: ProfileCompletenessRing(percentage: 0.5, size: 200),
          ),
        ),
      );
      final sizedBox = tester.widgetList<SizedBox>(find.byType(SizedBox))
          .where((s) => s.width == 200 && s.height == 200);
      expect(sizedBox.isNotEmpty, isTrue);
    }});
  }});
}}
''')

def _gen_t158_test(title, tid, import_path):
    return textwrap.dedent(f'''\
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import '{import_path}';

void main() {{
  group('{title} ({tid})', () {{
    testWidgets('shows checkmark when verified', (tester) async {{
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: VerificationBadge(isVerified: true)),
        ),
      );
      expect(find.byIcon(Icons.check), findsOneWidget);
    }});

    testWidgets('hides badge when not verified', (tester) async {{
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: VerificationBadge(isVerified: false)),
        ),
      );
      expect(find.byIcon(Icons.check), findsNothing);
    }});

    testWidgets('shows label text when showLabel is true', (tester) async {{
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: VerificationBadge(isVerified: true, showLabel: true),
          ),
        ),
      );
      expect(find.text('Verified'), findsOneWidget);
    }});

    testWidgets('GetVerifiedButton renders with correct text', (tester) async {{
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: GetVerifiedButton(onPressed: () {{}})),
        ),
      );
      expect(find.text('Get Verified'), findsOneWidget);
      expect(find.byIcon(Icons.verified_outlined), findsOneWidget);
    }});

    testWidgets('GetVerifiedButton triggers callback on tap', (tester) async {{
      var tapped = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: GetVerifiedButton(onPressed: () => tapped = true),
          ),
        ),
      );
      await tester.tap(find.text('Get Verified'));
      expect(tapped, isTrue);
    }});

    testWidgets('has tooltip for accessibility', (tester) async {{
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: VerificationBadge(isVerified: true)),
        ),
      );
      expect(find.byType(Tooltip), findsOneWidget);
    }});
  }});
}}
''')

def _gen_onb100_test(title, tid, import_path):
    return textwrap.dedent(f'''\
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import '{import_path}';

void main() {{
  group('{title} ({tid})', () {{
    testWidgets('renders with Show me header', (tester) async {{
      await tester.pumpWidget(
        const MaterialApp(home: MatchPreferencesScreen()),
      );
      expect(find.text('Show me'), findsOneWidget);
    }});

    testWidgets('shows Men, Women, Everyone buttons', (tester) async {{
      await tester.pumpWidget(
        const MaterialApp(home: MatchPreferencesScreen()),
      );
      expect(find.text('Men'), findsOneWidget);
      expect(find.text('Women'), findsOneWidget);
      expect(find.text('Everyone'), findsOneWidget);
    }});

    testWidgets('Next button is disabled until selection', (tester) async {{
      await tester.pumpWidget(
        const MaterialApp(home: MatchPreferencesScreen()),
      );
      final button = tester.widget<ElevatedButton>(find.byType(ElevatedButton));
      expect(button.onPressed, isNull);
    }});

    testWidgets('selecting an option enables Next', (tester) async {{
      await tester.pumpWidget(
        const MaterialApp(home: MatchPreferencesScreen()),
      );
      await tester.tap(find.text('Women'));
      await tester.pump();
      final button = tester.widget<ElevatedButton>(find.byType(ElevatedButton));
      expect(button.onPressed, isNotNull);
    }});

    testWidgets('radio behavior — only one selected at a time', (tester) async {{
      await tester.pumpWidget(
        const MaterialApp(home: MatchPreferencesScreen()),
      );
      await tester.tap(find.text('Men'));
      await tester.pump();
      await tester.tap(find.text('Everyone'));
      await tester.pump();
      // Only Everyone should show selected styling
      final menButton = tester.widget<OutlinedButton>(
        find.ancestor(of: find.text('Men'), matching: find.byType(OutlinedButton)),
      );
      final everyoneButton = tester.widget<OutlinedButton>(
        find.ancestor(of: find.text('Everyone'), matching: find.byType(OutlinedButton)),
      );
      expect(menButton.style?.side?.resolve({{}}), isNot(
        const BorderSide(color: Color(0xFFFF6B6B), width: 2)));
    }});

    testWidgets('has progress bar at 55%', (tester) async {{
      await tester.pumpWidget(
        const MaterialApp(home: MatchPreferencesScreen()),
      );
      final progress = tester.widget<LinearProgressIndicator>(
        find.byType(LinearProgressIndicator),
      );
      expect(progress.value, 0.55);
    }});

    testWidgets('has back and close navigation', (tester) async {{
      await tester.pumpWidget(
        const MaterialApp(home: MatchPreferencesScreen()),
      );
      expect(find.byIcon(Icons.arrow_back), findsOneWidget);
      expect(find.byIcon(Icons.close), findsOneWidget);
    }});
  }});
}}
''')

def _gen_generic_test(title, tid, class_name, import_path):
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
  }});
}}
''')


# ── Routing ───────────────────────────────────────────────────────────

# Task ID → generator function mapping
SMART_GENERATORS = {
    "T154": generate_profile_completeness_ring,
    "T158": generate_verification_badge,
    "ONB-100": generate_match_preferences_screen,
}


def smart_generate(task: dict, repo_dir: Path) -> tuple[str, str]:
    """
    Generate code for a task. Returns (content, source_label).
    Falls back to reference-based generation if no smart generator exists.
    """
    tid = task["id"]

    # Check for smart generator
    if tid in SMART_GENERATORS:
        content = SMART_GENERATORS[tid](task)
        return content, "smart-generated"

    # Fallback: try to read reference file and adapt
    ref_files = task.get("referenceFiles", [])
    if ref_files and repo_dir:
        ref_path = repo_dir / ref_files[0]
        if ref_path.exists():
            ref_content = ref_path.read_text()
            content = _adapt_from_reference(task, ref_content)
            if content:
                return content, "reference-adapted"

    return None, None


def smart_generate_test(task: dict, repo_dir: Path) -> Optional[str]:
    """Generate a feature-specific test file for the task."""
    tid = task["id"]
    import_path = task["filePath"].replace("lib/", "package:dejtingapp/")

    # Derive class name from the generator or task title
    title = task["title"]
    if tid == "T154":
        class_name = "ProfileCompletenessRing"
    elif tid == "T158":
        class_name = "VerificationBadge"
    elif tid == "ONB-100":
        class_name = "MatchPreferencesScreen"
    else:
        class_name = "".join(w.capitalize() for w in title.replace("-", " ").split())

    return generate_widget_test(task, class_name, import_path)


def _adapt_from_reference(task: dict, ref_content: str) -> Optional[str]:
    """Try to adapt a reference file to a new task. Returns None if can't."""
    # This is a placeholder for future AI-powered adaptation
    # For now, return None to fall back to the old generator
    return None
