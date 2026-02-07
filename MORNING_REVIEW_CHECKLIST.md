# ☀️ Morning Review Checklist - Overnight AI Run

**Date:** February 9, 2026  
**Snapshot:** "Before overnight run - Feb 8 evening"  
**Tasks queued:** 4 (ONB-050, ONB-060, ONB-070, ONB-080)

---

## ⏱️ Quick 5-Minute Review

### 1. What Changed?
```bash
cd /home/m/development/DatingAppController
./scripts/status-all.sh
```

**Record:**
- Repos with changes: _______________
- Number of files changed: _______________
- Commits made: _______________

---

### 2. Code Quick Scan
```bash
cd repos/mobile_dejtingapp
git log --oneline -10
```

**Check:**
- [ ] Commit messages look good? (conventional format)
- [ ] Only expected files changed? (lib/screens/wizard/*.dart)
- [ ] No changes to auth/payment/sensitive files?

---

### 3. Does it Compile?
```bash
cd repos/mobile_dejtingapp
flutter analyze
```

**Result:**
- Errors: _____(count)
- Warnings: _____(count)
- Pass? ☐ YES  ☐ NO

---

### 4. Visual Test (2 minutes)
```bash
cd repos/mobile_dejtingapp
flutter run -d chrome
```

For each new screen:
- [ ] Community Guidelines: Shows 4 rules + I agree button?
- [ ] First Name: Input works, validation works, Next enables?
- [ ] Birthday: Date inputs work, 18+ validation blocks correctly?
- [ ] Gender: 3 buttons work, More opens modal, toggle works?

---

### 5. Decision Matrix

| Scenario | Action |
|----------|--------|
| ✅ All looks great, 0-2 minor issues | **APPROVE** → `./scripts/push-all.sh` |
| 🤔 Works but needs 30-60 min of fixes | **KEEP LOCAL** → Fix manually, then push |
| ❌ Major issues, >1 hour of rework | **ROLLBACK** → `./scripts/rollback.sh "Before overnight run - Feb 8 evening"` |
| ⏸️ Need more time to review | **DO NOTHING** → Review later, changes stay local |

---

## 📊 Detailed Review (15 minutes)

### Task Completion Status

Check `.ai-workspace/task-queue.json`:

| Task | Status | Files Created | Notes |
|------|--------|---------------|-------|
| ONB-050 | ☐ Done ☐ Partial ☐ Not started | | |
| ONB-060 | ☐ Done ☐ Partial ☐ Not started | | |
| ONB-070 | ☐ Done ☐ Partial ☐ Not started | | |
| ONB-080 | ☐ Done ☐ Partial ☐ Not started | | |

**Completion rate: ___/4 (____%)**

---

### Code Quality Review

```bash
cd repos/mobile_dejtingapp
git diff HEAD~4..HEAD | wc -l  # Lines changed
```

**Lines changed:** _______________

Review sample code (pick one file):
```bash
cat lib/screens/wizard/first_name_screen.dart | head -50
```

**Quality checks:**
- [ ] Uses existing colors (coralColor, purpleColor)?
- [ ] Follows existing patterns (like phone_entry_screen.dart)?
- [ ] Has comments explaining logic?
- [ ] Uses const constructors?
- [ ] Handles edge cases?
- [ ] Error messages user-friendly?

---

### Test Each Screen

#### Community Guidelines Screen
```bash
# Navigate in app to this screen
```
- [ ] Header displays correctly?
- [ ] 4 rules visible with icons?
- [ ] 'I agree' button works?
- [ ] Can't go back without accepting?
- [ ] Navigates to first name screen after accept?

**Issues found:**
- _______________________________________________

---

#### First Name Screen
- [ ] Progress bar shows (should be ~20%)?
- [ ] Input auto-focuses?
- [ ] Can type letters/spaces?
- [ ] Blocks numbers/special chars?
- [ ] Next button disabled when empty?
- [ ] Next button enables with valid input?
- [ ] Warning text visible?
- [ ] Back button works?

**Test cases:**
- "a" → Should reject (too short)
- "ab" → Should accept (min 2 chars)
- "John123" → Should reject (numbers)
- "Mary-Jane" → Should accept (hyphen OK)
- "José" → Should accept (accents OK)

**Issues found:**
- _______________________________________________

---

#### Birthday Screen
- [ ] Progress bar shows (~30%)?
- [ ] Month dropdown has 1-12?
- [ ] Day/Year are number inputs?
- [ ] Privacy note visible?
- [ ] Can select valid date (e.g. 1990-05-15)?
- [ ] Rejects invalid date (e.g. 1990-02-30)?
- [ ] Rejects under-18 (e.g. 2010-01-01)?
- [ ] Error modal shows for under-18?
- [ ] Next button enables only for valid 18+ date?

**Test cases:**
- 2010-01-01 → Should show under-18 error
- 2008-02-08 → Should accept (18 today!)
- 1990-02-30 → Should show invalid date error
- 1992-02-29 → Should accept (leap year)
- 1993-02-29 → Should reject (not leap year)

**Issues found:**
- _______________________________________________

---

#### Gender Screen
- [ ] Progress bar shows (~40%)?
- [ ] 3 buttons visible (Man, Woman, More)?
- [ ] Can select Man or Woman?
- [ ] More button opens modal?
- [ ] Modal shows 10+ gender options?
- [ ] Can select from modal?
- [ ] Search bar visible (even if non-functional)?
- [ ] Privacy toggle works?
- [ ] Next button enables after selection?

**Test cases:**
- Select "Man" → Next should enable
- Select "Woman" → Next should enable
- Click "More" → Modal opens
- Select "Non-binary" from modal → Modal closes, Next enables
- Toggle privacy on/off → State persists

**Issues found:**
- _______________________________________________

---

## 🐛 Common Issues & Quick Fixes

### Issue: Compilation errors
**Fix:**
```bash
cd repos/mobile_dejtingapp
flutter clean
flutter pub get
flutter analyze
# Fix errors shown in output
```

### Issue: Navigation not wired
**Fix:** Add navigation in previous screen:
```dart
Navigator.push(context, MaterialPageRoute(
  builder: (context) => const FirstNameScreen()
));
```

### Issue: Colors not matching
**Fix:** Ensure using shared colors:
```dart
static const Color coralColor = Color(0xFFFF7F50);
static const Color purpleColor = Color(0xFF7f13ec);
```

### Issue: Validation too strict/loose
**Fix:** Adjust regex/logic in validation function

---

## ✅ Approval Process

If approving (quality is good):

```bash
cd /home/m/development/DatingAppController

# Final check
./scripts/status-all.sh

# Push all changes
./scripts/push-all.sh
```

**Confirmation prompts:**
- Review which repos will be pushed
- Type 'yes' to confirm

**Then:**
- Update task tracker
- Post summary in project notes
- Plan next overnight run

---

## 🔄 Rollback Process

If major issues found:

```bash
cd /home/m/development/DatingAppController

# Nuclear option - undo everything
./scripts/rollback.sh "Before overnight run - Feb 8 evening"
```

**Confirmation:**
- Type 'yes' to confirm

**Result:**
- All repos reset to snapshot
- Uncommitted changes deleted
- Back to clean state

**Then:**
- Review what went wrong
- Adjust task specifications
- Try again tomorrow with lessons learned

---

## 📝 Post-Review Report

```markdown
# Overnight Run Report - Feb 8-9, 2026

## Executive Summary
- **Tasks completed:** X/4
- **Code quality:** ⭐⭐⭐⭐☆ (4/5)
- **Decision:** APPROVED / ROLLBACK / PARTIAL
- **Time saved:** ~X hours

## Detailed Results

### ONB-050: Community Guidelines Screen
- Status: DONE / PARTIAL / FAILED
- Issues: [List any issues]
- Manual fixes needed: [Y/N + details]

### ONB-060: First Name Screen
- Status: DONE / PARTIAL / FAILED
- Issues: [List any issues]
- Manual fixes needed: [Y/N + details]

### ONB-070: Birthday Screen
- Status: DONE / PARTIAL / FAILED
- Issues: [List any issues]
- Manual fixes needed: [Y/N + details]

### ONB-080: Gender Screen
- Status: DONE / PARTIAL / FAILED
- Issues: [List any issues]
- Manual fixes needed: [Y/N + details]

## What Worked Well
1. [List successes]
2. 
3. 

## What Needs Improvement
1. [List gaps/issues]
2. 
3. 

## Lessons for Next Run
1. [Insights]
2. 
3. 

## Manual Work Remaining
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## Next Overnight Run
**When:** Feb 9-10
**Tasks:** [List next batch]
**Improvements:** [Based on lessons learned]
```

---

## 🎯 Success Criteria (First Run)

Realistic expectations:

| Metric | Target | Stretch Goal |
|--------|--------|--------------|
| Tasks completed | 3/4 (75%) | 4/4 (100%) |
| Compilation errors | 0 | 0 |
| Code quality issues | <5 minor | 0 |
| Manual fixes needed | <1 hour | 0 |
| Rollback needed | No | No |

**Remember:** This is a **learning run**. Even 2/4 tasks done well is a success!

---

## ⏭️ If This Goes Well

**Next overnight run could include:**
- ONB-090: Sexual orientation screen
- ONB-100: Match preferences screen
- ONB-110: Relationship goals screen
- Simple backend tasks (DTOs, simple endpoints)

**Gradually increase complexity:**
- Week 1: Pure UI screens (Tier 1)
- Week 2: UI + simple validation (Tier 1)
- Week 3: UI + backend stubs (Tier 1-2)
- Week 4: Full features with backend (Tier 2)

---

**Good morning! Time to see what AI built while you slept! ☕**
