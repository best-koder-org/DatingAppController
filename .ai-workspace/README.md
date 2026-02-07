# AI Workspace

This directory contains AI automation configuration for overnight runs.

## Files

- `task-queue.json` - Tasks waiting for AI processing
- `completed-tasks.json` - Historical record of completed tasks

## Task Queue Format

```json
{
  "queue": [
    {
      "id": "mvp-001",
      "type": "feature",
      "service": "UserService",
      "description": "Implement profile update endpoint",
      "priority": "high",
      "estimatedFiles": 5
    }
  ]
}
```

## Safety Tiers

- **Tier 1 (100% safe)**: Database migrations, DTOs, models
- **Tier 2 (90% safe)**: Controllers with clear specs, service methods
- **Tier 3 (Never automate)**: Authentication, payments, complex business logic
