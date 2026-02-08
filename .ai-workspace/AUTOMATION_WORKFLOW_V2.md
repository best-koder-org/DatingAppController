# Automation Workflow V2 - Branch-Based with PRs

## Problem with V1
- Direct commits to main (merge conflict risk)
- Terminal file creation requiring "Allow" prompts
- No PR review process

## V2 Solution

### 1. Feature Branch Per Task
Each task creates a feature branch:
```
automation/onb-050-community-guidelines
automation/onb-060-first-name-screen
automation/onb-070-birthday-screen
automation/onb-080-gender-screen
```

### 2. Workflow Per Task
```
A. Create feature branch
   git checkout -b automation/onb-XXX-task-name

B. Implement screen using create_file tool (NO PROMPTS!)

C. Validate with flutter analyze

D. Commit to feature branch

E. Push feature branch to GitHub

F. Create PR (or auto-merge if clean)

G. Update task queue

H. Move to next task
```

### 3. Merge Strategy Options

**Option A: Auto-merge (if no conflicts)**
- Check for conflicts
- If clean, merge immediately
- Continue to next task

**Option B: Create PR for review**
- Create PR on GitHub
- Add labels: automation, onboarding
- User reviews later
- Continue to next task

**Option C: Stack PRs (recommended)**
- Create all 4 PRs
- User reviews and merges together
- No blocking between tasks

## Implementation

Update execute-task-queue.sh to:
1. Create feature branch before each task
2. Use create_file tool instead of cat >
3. Push to origin after commit
4. Create PR or auto-merge
5. Log everything

## User Control

User can choose merge strategy in task-queue.json:
```json
{
  "automationSettings": {
    "mergeStrategy": "auto|create-pr|stack-prs",
    "requireReview": false,
    "branchPrefix": "automation/"
  }
}
```
