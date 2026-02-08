# DatingApp Controller

Multi-repository orchestration for DatingApp development with autonomous task automation.

## Quick Start

### 1. Run Overnight Automation
```bash
./start-overnight-run.sh
```

This will:
- Create a safety snapshot
- Show queued tasks
- Activate AI automation mode
- Process all tasks in `.ai-workspace/task-queue.json`

### 2. Check Progress
```bash
tail -f .ai-workspace/execution.log
```

### 3. Rollback If Needed
```bash
./scripts/rollback.sh "Before overnight run - Feb 08 2026"
```

## How It Works

### Task Queue System
Tasks are defined in `.ai-workspace/task-queue.json` with:
- **Tier 1**: Safe UI work, no external dependencies
- **Tier 2**: Backend integration, requires services running
- **Tier 3**: Complex features, needs careful review

### Automation Workflow

1. **User runs**: `./start-overnight-run.sh`
2. **Script creates**: Atomic snapshot across all repos
3. **Script activates**: `.ai-workspace/automation-active.txt` marker
4. **AI detects marker**: Enters autonomous execution mode
5. **AI processes tasks**: One by one from queue
   - Moves task to `inProgress[]`
   - Implements screen per specification
   - Runs `flutter analyze` for validation
   - Commits with conventional format
   - Moves task to `completed[]`
6. **AI logs progress**: To `.ai-workspace/execution.log`
7. **User checks**: Results in morning, rollback if needed

### Safety Features

- **Atomic Snapshots**: Tag all 8 repos simultaneously
- **30-Second Rollback**: Undo all changes across repos
- **Validation Gates**: Each task runs `flutter analyze`
- **Tier System**: Only safe tasks run unattended
- **Execution Log**: Complete audit trail

## File Structure

```
DatingAppController/
├── .ai-workspace/
│   ├── task-queue.json              # Task definitions
│   ├── automation-active.txt        # AI detection marker
│   ├── execution.log                # Runtime progress log
│   └── AI_TASK_PROCESSOR_INSTRUCTIONS.md  # AI automation guide
├── repos/                           # Git submodules
│   ├── DatingApp-Config/
│   ├── UserService/
│   ├── MatchmakingService/
│   ├── swipe-service/
│   ├── photo-service/
│   ├── messaging-service/
│   ├── dejting-yarp/
│   └── mobile_dejtingapp/           # Flutter app (main workspace)
├── scripts/
│   ├── snapshot.sh                  # Create multi-repo snapshot
│   ├── rollback.sh                  # Rollback to snapshot
│   ├── status-all.sh                # Check all repo status
│   ├── push-all.sh                  # Push all repos
│   └── execute-task-queue.sh        # Task processor engine
├── start-overnight-run.sh           # Main automation entry point
├── OVERNIGHT_AUTOMATION_GUIDE.md    # Complete automation docs
└── MORNING_REVIEW_CHECKLIST.md      # Review workflow
```

## Scripts

### Main Workflow
- `./start-overnight-run.sh` - Start automation (snapshot + execute)
- `./scripts/execute-task-queue.sh` - Process task queue
- `tail -f .ai-workspace/execution.log` - Monitor progress

### Safety & Status
- `./scripts/snapshot.sh "message"` - Create snapshot
- `./scripts/rollback.sh "tag name"` - Rollback to snapshot
- `./scripts/status-all.sh` - Check all repos
- `./scripts/push-all.sh` - Push all repos

## Task Queue Format

```json
{
  "queue": [
    {
      "id": "ONB-050",
      "type": "screen",
      "tier": 1,
      "title": "Community Guidelines Screen",
      "filePath": "lib/screens/wizard/community_guidelines_screen.dart",
      "acceptanceCriteria": [...],
      "estimatedHours": 4,
      "testCommand": "flutter analyze ...",
      "referenceFiles": [...]
    }
  ],
  "inProgress": [],
  "completed": []
}
```

## AI Automation Mode

When `automation-active.txt` exists, the AI enters autonomous mode:

1. **Reads**: `.ai-workspace/task-queue.json`
2. **For each task**:
   - Move to `inProgress[]`
   - Create file in `repos/mobile_dejtingapp/`
   - Follow `acceptanceCriteria` exactly
   - Run `testCommand` for validation
   - Commit: `feat(onboarding): Add [title] ([id])`
   - Move to `completed[]` with metadata
3. **Logs**: Everything to `execution.log`
4. **Stops**: On first error (fail-fast)

## Morning Review

1. Check execution log:
   ```bash
   cat .ai-workspace/execution.log
   ```

2. Verify completed tasks:
   ```bash
   jq '.completed' .ai-workspace/task-queue.json
   ```

3. Test the implementations:
   ```bash
   cd repos/mobile_dejtingapp
   flutter analyze
   flutter test
   ```

4. If issues found, rollback:
   ```bash
   ./scripts/rollback.sh "Before overnight run - ..."
   ```

5. If all good, push:
   ```bash
   ./scripts/push-all.sh "feat: Complete overnight automation run"
   ```

## Documentation

- **OVERNIGHT_AUTOMATION_GUIDE.md** - Complete automation guide
- **MORNING_REVIEW_CHECKLIST.md** - Review workflow
- **.ai-workspace/AI_TASK_PROCESSOR_INSTRUCTIONS.md** - AI execution rules

## Contributing

Tasks should be Tier 1 safe:
- Pure UI work
- No external service dependencies
- No authentication logic
- Well-defined acceptance criteria
- Reference files for consistency

## License

Part of DatingApp project
