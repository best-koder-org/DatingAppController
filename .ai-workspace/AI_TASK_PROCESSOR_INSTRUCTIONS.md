# AI Task Processor Instructions

## Mission
You are an autonomous task processor. When you detect `automation-active.txt` exists, you MUST process all tasks in the queue without waiting for user input.

## Detection Method
Check for: `.ai-workspace/automation-active.txt`
If exists: AUTOMATION MODE - execute tasks immediately

## Processing Workflow

### 1. Read Task Queue
```bash
cat .ai-workspace/task-queue.json
```

### 2. For Each Task in queue[]

#### A. Move to In-Progress
Update task-queue.json:
- Remove from `queue[]`
- Add to `inProgress[]`

#### B. Implement Task
Based on task specification:
- Create file at `filePath` (in repos/mobile_dejtingapp/)
- Follow all `acceptanceCriteria`
- Reference `referenceFiles` for pattern consistency
- Use proper Flutter/Dart conventions

#### C. Validate
```bash
cd repos/mobile_dejtingapp
flutter analyze lib/screens/wizard/[filename].dart
```

#### D. Commit
```bash
cd repos/mobile_dejtingapp
git add lib/screens/wizard/[filename].dart
git commit -m "feat(onboarding): Add [title] ([id])"
```

#### E. Move to Completed
Update task-queue.json:
- Remove from `inProgress[]`
- Add to `completed[]` with completion timestamp

#### F. Update Queue File
```bash
# Write updated JSON back to task-queue.json
```

### 3. Repeat Until queue[] is Empty

### 4. Final Report
Log to `.ai-workspace/execution.log`:
- Total tasks completed
- Time taken per task
- Any errors encountered
- Files created
- Commits made

## Example Task Implementation

Task: ONB-050 (Community Guidelines Screen)

**File**: `repos/mobile_dejtingapp/lib/screens/wizard/community_guidelines_screen.dart`

**Content Structure**:
```dart
import 'package:flutter/material.dart';

class CommunityGuidelinesScreen extends StatelessWidget {
  const CommunityGuidelinesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        // No back button - user must accept
        automaticallyImplyLeading: false,
        title: const Text('Welcome to DejTing'),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Please follow these House Rules.',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 32),
              // 4 rules with checkmark icons
              _buildRule('Be yourself', 'Use authentic photos and info'),
              _buildRule('Stay safe', 'Report suspicious behavior'),
              _buildRule('Play it cool', 'Treat others with respect'),
              _buildRule('Be proactive', 'Make the first move'),
              const Spacer(),
              // I agree button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () {
                    // Navigate to next screen
                    Navigator.pushNamed(context, '/onboarding/first-name');
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: Colors.black,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                  child: const Text('I agree', style: TextStyle(fontSize: 18)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRule(String title, String description) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 24.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.check_circle, color: Colors.green, size: 24),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 4),
                Text(
                  description,
                  style: const TextStyle(fontSize: 14, color: Colors.grey),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
```

## Task Queue JSON Update Pattern

Moving task from queue to inProgress:
```json
{
  "queue": [
    // Remove task ONB-050 from here
  ],
  "inProgress": [
    {
      "id": "ONB-050",
      "startedAt": "2026-02-08T01:00:00Z",
      ...task data...
    }
  ]
}
```

Moving task from inProgress to completed:
```json
{
  "inProgress": [],
  "completed": [
    {
      "id": "ONB-050",
      "completedAt": "2026-02-08T01:15:00Z",
      "durationMinutes": 15,
      "filesCreated": ["lib/screens/wizard/community_guidelines_screen.dart"],
      "commitHash": "abc1234",
      ...task data...
    }
  ]
}
```

## Critical Rules

1. **NO USER INTERACTION**: Process all tasks without waiting
2. **COMMIT AFTER EACH TASK**: Don't batch commits
3. **UPDATE JSON AFTER EACH TASK**: Keep state synchronized
4. **LOG EVERYTHING**: Write to execution.log
5. **STOP ON ERROR**: Don't continue if flutter analyze fails
6. **USE REFERENCE FILES**: Match existing patterns exactly

## Automation Detection

```bash
# Check if automation mode is active
if [ -f .ai-workspace/automation-active.txt ]; then
  echo "AUTOMATION MODE DETECTED"
  # Begin autonomous execution
fi
```

When you see this file, START PROCESSING IMMEDIATELY.
