# DatingAppController

Automation and orchestration toolkit for multi-repository development in the DatingApp ecosystem.

## What It Does

- Coordinates work across many repos
- Runs scripted automation flows (including overnight batches)
- Tracks task queue state and execution logs
- Supports rollback and safety checkpoints

## Why It Is Interesting

This repo demonstrates practical developer productivity engineering:
- Multi-repo orchestration patterns
- Repeatable automation with rollback strategy
- Operational scripting for complex development workflows

## Quick Start

### Start automated run

```bash
./start-overnight-run.sh
```

### Follow execution

```bash
tail -f .ai-workspace/execution.log
```

### Rollback example

```bash
./scripts/rollback.sh "Before overnight run"
```

## Project Layout

```text
DatingAppController/
  scripts/             # Automation and safety scripts
  templates/           # Task/automation templates
  repos/               # Linked repositories and pointers
  docs/                # Internal documentation and dashboards
  .ai-workspace/       # Queue and execution state
```

## Typical Use Cases

- Batch updates across service repos
- Controlled overnight automation
- State snapshots before risky operations
- Daily review and operator workflows

## Related Repositories

- `best-koder-org/UserService`
- `best-koder-org/MatchmakingService`
- `best-koder-org/messaging-service`
- `best-koder-org/swipe-service`
- `best-koder-org/mobile_dejtingapp`

## Status

Active support repository for orchestrating platform development.
