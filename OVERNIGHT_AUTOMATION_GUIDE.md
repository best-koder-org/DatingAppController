# Overnight AI Automation - First Run Guide

**Created:** February 8, 2026  
**Status:** Ready for first test run  
**Est. Duration:** 6-8 hours  
**Review Time:** 30 minutes (morning)

---

## 🎯 Tonight's Goals

Test autonomous overnight development with **4 safe Tier 1 tasks**:

1. ✅ **TASK-050**: Community Guidelines screen (4 hours)
2. ✅ **TASK-060**: First Name entry screen (3 hours)
3. ✅ **TASK-070**: Birthday entry screen (4 hours)
4. ✅ **TASK-080**: Gender selection screen (5 hours)

**Total:** ~16 estimated hours → Expect 4-6 hours with AI assistance

---

## 🛡️ Safety Checklist (Before Starting)

### Step 1: Create Snapshot (CRITICAL!)
```bash
cd /home/m/development/DatingAppController
./scripts/snapshot.sh "Before overnight run - Feb 8 evening"
```

**Expected output:**
```
✅ Snapshot created: Before overnight run - Feb 8 evening
📝 To rollback: ./scripts/rollback.sh "Before overnight run - Feb 8 evening"
```

### Step 2: Verify Snapshot Created
```bash
cd repos/mobile_dejtingapp
git tag | grep "Before overnight"
```

Should show the tag!

### Step 3: Verify Working Directory Clean
```bash
cd /home/m/development/DatingAppController
./scripts/status-all.sh
```

Should show minimal uncommitted changes (or clean)

---

## 📋 Task Queue (Loaded)

Location: `.ai-workspace/task-queue.json`

```json
{
  "queue": [
    {
      "id": "ONB-050",
      "type": "screen",
      "tier": 1,
      "service": "mobile_dejtingapp",
      "title": "Community Guidelines Screen",
      "description": "Create lib/screens/wizard/community_guidelines_screen.dart",
      "acceptanceCriteria": [
        "Header: 'Welcome to DejTing. Please follow these House Rules.'",
        "4 rules with checkmark icons (Be yourself, Stay safe, Play it cool, Be proactive)",
        "Large white 'I agree' button",
        "Bilingual content (English/Swedish toggle optional for now)",
        "Navigation from phone verification success",
        "Stores acceptance timestamp in backend (stub for now)"
      ],
      "estimatedHours": 4,
      "safetyNotes": "Pure UI work, no auth/payment logic",
      "testCommand": "flutter run -d chrome -t lib/main.dart"
    },
    {
      "id": "ONB-060",
      "type": "screen",
      "tier": 1,
      "service": "mobile_dejtingapp",
      "title": "First Name Entry Screen",
      "description": "Create lib/screens/wizard/first_name_screen.dart",
      "acceptanceCriteria": [
        "Progress bar at top (20% filled)",
        "Header: 'What's your first name?'",
        "Single text input field",
        "Warning: 'This is how it'll appear on your profile. Can't change it later.'",
        "Next button (disabled until valid input)",
        "Validation: 2-50 chars, letters/spaces/hyphens only, auto-capitalize",
        "Back arrow + close X navigation"
      ],
      "estimatedHours": 3,
      "safetyNotes": "Simple form validation, no backend calls yet",
      "testCommand": "flutter analyze lib/screens/wizard/first_name_screen.dart"
    },
    {
      "id": "ONB-070",
      "type": "screen",
      "tier": 1,
      "service": "mobile_dejtingapp",
      "title": "Birthday Entry Screen",
      "description": "Create lib/screens/wizard/birthday_screen.dart",
      "acceptanceCriteria": [
        "Progress bar (30%)",
        "Header: 'Your b-day?'",
        "Three inputs: Month (dropdown), Day (input), Year (input)",
        "Privacy note: 'Your profile shows your age, not your birthdate'",
        "18+ validation (show error if under 18)",
        "Real date validation (Feb 30 = invalid, leap years)",
        "Next button",
        "Under-18 error modal with 'Go back' option"
      ],
      "estimatedHours": 4,
      "safetyNotes": "Date validation only, no user data stored yet",
      "testCommand": "flutter analyze lib/screens/wizard/birthday_screen.dart"
    },
    {
      "id": "ONB-080",
      "type": "screen",
      "tier": 1,
      "service": "mobile_dejtingapp",
      "title": "Gender Selection Screen",
      "description": "Create lib/screens/wizard/gender_screen.dart",
      "acceptanceCriteria": [
        "Progress bar (40%)",
        "Header: 'What's your gender?'",
        "3 large buttons: Man, Woman, More →",
        "Privacy toggle: 'Show my gender on my profile'",
        "Next button (disabled until selection)",
        "More button opens modal with 10+ options (Man, Woman, Trans Man, Trans Woman, Non-binary, etc.)",
        "Search bar in modal (optional - can be placeholder)",
        "Single selection behavior"
      ],
      "estimatedHours": 5,
      "safetyNotes": "UI only, reference data hardcoded for now (backend later)",
      "testCommand": "flutter analyze lib/screens/wizard/gender_screen.dart"
    }
  ],
  "inProgress": [],
  "completed": []
}
```

---

## 🤖 AI Execution Instructions (For AI Agent)

### For Each Task:

1. **Read specification** from `task-queue.json`
2. **Check existing code** in `repos/mobile_dejtingapp/lib/screens/wizard/`
3. **Create new file** following Flutter best practices
4. **Use existing components**:
   - Colors from `welcome_screen.dart` (coralColor, purpleColor)
   - Button styles should match existing patterns
   - Navigation patterns from `phone_entry_screen.dart`
5. **Write tests** (optional for first run - focus on working UI)
6. **Commit with conventional format**:
   ```
   feat(onboarding): Add [screen name]
   
   ONB-XXX: [Task title]
   - Acceptance criteria 1
   - Acceptance criteria 2
   - etc.
   ```
7. **Run flutter analyze** to catch errors
8. **Move task** from `queue` to `completed` in task-queue.json

### Code Quality Requirements:

- ✅ Follow existing code style in `phone_entry_screen.dart`
- ✅ Use `const` constructors where possible
- ✅ Add helpful comments
- ✅ No external package additions (use built-in Flutter widgets)
- ✅ Handle all error states
- ✅ Responsive design (works on mobile + web)

### What NOT to do:

- ❌ Don't push to GitHub (we'll review first!)
- ❌ Don't modify existing files except for navigation wiring
- ❌ Don't add new packages without explicit approval
- ❌ Don't implement backend calls (stub them with TODOs)
- ❌ Don't skip error handling

---

## 🌅 Morning Review Checklist

### Step 1: Check What Changed
```bash
cd /home/m/development/DatingAppController
./scripts/status-all.sh
```

**Look for:**
- ✅ Only `mobile_dejtingapp` repo has changes?
- ✅ Number of changed files reasonable (4-8 files)?
- ✅ No changes to critical files (main.dart, auth files)?

### Step 2: Review Code Quality
```bash
cd repos/mobile_dejtingapp
git log --oneline -10
git diff HEAD~4..HEAD
```

**Check:**
- ✅ Commit messages follow conventional format?
- ✅ Code looks clean and well-formatted?
- ✅ No sensitive data or API keys?
- ✅ Follows existing patterns?

### Step 3: Run Tests
```bash
cd repos/mobile_dejtingapp
flutter analyze
flutter test
```

**Expected:**
- ✅ No analysis errors (warnings OK)
- ✅ All tests passing (if any written)

### Step 4: Visual Test
```bash
cd repos/mobile_dejtingapp
flutter run -d chrome
```

**Manual checks:**
1. Navigate to each new screen
2. Fill out forms
3. Test validation rules
4. Verify buttons enable/disable correctly
5. Check error messages appear

### Step 5: Decision Time

**Option A: Approve ✅**
```bash
cd /home/m/development/DatingAppController
./scripts/push-all.sh
```
→ Pushes all commits to GitHub

**Option B: Rollback ❌**
```bash
cd /home/m/development/DatingAppController
./scripts/rollback.sh "Before overnight run - Feb 8 evening"
```
→ Undoes all changes in 30 seconds

**Option C: Keep but don't push 🤔**
→ Leave changes local, iterate manually, push later

---

## 📊 Success Metrics

**Measure these in the morning:**

| Metric | Target | How to Check |
|--------|--------|-------------|
| Tasks completed | 3-4 / 4 | Check task-queue.json completed[] |
| Code quality | 0 errors | `flutter analyze` |
| Build success | ✅ | `flutter build web --release` |
| Commit quality | All conventional | `git log --oneline` |
| Time saved | 10+ hours | Compare estimated vs actual |
| Rollback needed? | No | Did code meet standards? |

**First run expectations:**
- 75% success rate is GREAT (3/4 tasks)
- Some manual fixes expected
- Learn what works for next run

---

## 🔧 Troubleshooting

### If AI gets stuck on a task:

1. **Check logs** (if AI leaves any)
2. **Partial work is OK** - finish manually
3. **Skip to next task** - don't block on one issue

### If code won't compile:

```bash
cd repos/mobile_dejtingapp
flutter clean
flutter pub get
flutter analyze
```

Fix compilation errors manually, then proceed.

### If you want to abort mid-run:

```bash
# Stop AI process (Ctrl+C or kill process)
cd /home/m/development/DatingAppController
./scripts/rollback.sh "Before overnight run - Feb 8 evening"
```

---

## 📝 Post-Run Notes Template

Copy this after reviewing:

```
# Overnight Run Report - Feb 8-9, 2026

## Results
- Tasks attempted: X/4
- Tasks completed: X/4
- Tasks needing fixes: X
- Rollback needed: Yes/No

## What Worked
- [List what AI did well]

## What Needs Improvement  
- [List issues encountered]

## Manual Fixes Required
- [ ] Fix X in file Y
- [ ] Add validation to Z

## Lessons for Next Run
- [Insights for better automation]

## Time Saved
- Estimated manual effort: 16 hours
- AI time: X hours
- Review + fixes: X hours
- NET SAVINGS: X hours
```

---

## 🚀 Ready to Start?

**Pre-flight checklist:**
- ✅ Snapshot created?
- ✅ Task queue loaded?
- ✅ Workspace clean?
- ✅ Understand rollback process?

**Start command:**
```bash
# AI: Read and execute tasks from:
cat /home/m/development/DatingAppController/.ai-workspace/task-queue.json

# Work in:
cd /home/m/development/DatingAppController/repos/mobile_dejtingapp

# When done, update:
echo "Update task-queue.json with completed tasks"
```

**Good night! See you in the morning! 🌙**

---

## 🎓 Why These Tasks Are Safe

1. **No external dependencies** - All Flutter built-ins
2. **No backend calls** - Pure frontend UI
3. **No auth/payment** - Just form validation
4. **Easy to verify** - Visual testing
5. **Easy to rollback** - One command
6. **Clear specs** - Detailed acceptance criteria
7. **Isolated work** - New files, minimal existing file changes
8. **Tier 1 classified** - Lowest risk category

**Philosophy:** "Make mistakes cheap, learning valuable"
