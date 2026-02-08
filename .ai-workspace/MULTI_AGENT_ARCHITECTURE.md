# Multi-Agent Architecture Design

> Status: **DESIGN ONLY** — not yet implemented. Current pipeline is single-agent.

## Current Architecture (Single Agent)

```
┌─────────────────────────────────────────────────┐
│          GitHub Actions Runner (ubuntu-latest)    │
│                                                   │
│  refill-queue ──► create-prs[0] ──► [1] ──► [2]  │
│                   (max-parallel: 1)               │
│                       │                           │
│                       ▼                           │
│              analyze-merges ──► merge-wave        │
│                       │                           │
│                       ▼                           │
│               morning-report                      │
└─────────────────────────────────────────────────┘
```

**Throughput:** 4 tasks/night, sequential, ~2 min per task.
**Cost:** Free (GitHub Actions, 2000 min/month on free tier).
**Risk:** Low — single writer to queue file, no race conditions.

## Why Multi-Agent?

Potential benefits:
- **Parallelism:** Process Flutter + Backend tasks simultaneously (different repos, no conflicts)
- **Specialization:** One agent knows Flutter/Dart, another knows .NET/C#
- **Speed:** 4 tasks in 8 min instead of 8 min

But our bottleneck is NOT speed — it's code quality and human review capacity.

## Proposed Multi-Agent Architecture (Future)

```
                    ┌───────────────┐
                    │  Coordinator  │
                    │  (Job 0)      │
                    └───────┬───────┘
                            │ reads build-plan.json
                            │ partitions tasks by repo type
                            │
              ┌─────────────┼─────────────────┐
              │             │                  │
              ▼             ▼                  ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │ Flutter Agent │ │ Backend      │ │ Infra Agent  │
     │ (Job 1)      │ │ Agent        │ │ (Job 3)      │
     │              │ │ (Job 2)      │ │              │
     │ ONB-xxx      │ │ BE-xxx       │ │ CI/CD, docs  │
     │ mobile repo  │ │ .NET repos   │ │ config repos │
     └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
            │                │                 │
            ▼                ▼                 ▼
     ┌──────────────────────────────────────────────┐
     │               Merge Analyzer (Job 4)          │
     │  - Cross-repo conflict detection              │
     │  - Wave-based safe merge                      │
     └──────────────┬───────────────────────────────┘
                    │
                    ▼
     ┌──────────────────────────────────────────────┐
     │             Morning Report (Job 5)            │
     │  - Unified report across all agents           │
     │  - Per-agent success/failure metrics           │
     └──────────────────────────────────────────────┘
```

### Key Design Decisions

**1. Queue Locking**
Each agent gets its OWN queue partition — no shared lock needed:
- `flutter-queue.json` for Flutter Agent
- `backend-queue.json` for Backend Agent
- `infra-queue.json` for Infra Agent

The Coordinator partitions `task-queue.json` into these on startup.

**2. No Cross-Repo Conflicts**
Flutter and Backend agents touch different repos entirely:
- Flutter → `repos/mobile_dejtingapp`
- Backend → `repos/UserService`, `repos/swipe-service`, etc.
- Infra → `repos/DatingApp-Config`, docs

So they CAN run in parallel safely.

**3. Shared State via Artifacts**
Instead of pushing to the same queue file, each agent uploads an artifact:
- `flutter-results.json` — PRs created, eval scores
- `backend-results.json` — PRs created, build status
- Morning Report downloads and merges all artifacts.

**4. Cost Consideration**
With 3 parallel agents, each running ~5 min:
- Single agent: 1 runner × 10 min = 10 min (free tier)
- Multi-agent: 3 runners × 5 min = 15 min total (free tier allows concurrent)
- Both well within 2000 min/month free limit

## Implementation Roadmap (When Ready)

### Phase 1: Queue Partitioning
- [ ] Add `partition-queue.py` that splits by service type
- [ ] Each agent reads its own queue partition
- [ ] Results merge via GitHub Actions artifacts

### Phase 2: Specialized Agents
- [ ] Flutter Agent gets Dart-specific tooling (flutter analyze, dart fix)
- [ ] Backend Agent gets dotnet-specific tooling (dotnet build, dotnet test)
- [ ] Each agent has its own eval criteria

### Phase 3: Coordination
- [ ] Dependency resolution across agents (e.g., "backend API must exist before Flutter calls it")
- [ ] Cross-repo integration testing
- [ ] Unified merge-wave across all repos

## When to Upgrade?

Stay single-agent until:
- [ ] Queue regularly has 8+ tasks and morning review takes too long
- [ ] Backend and Flutter tasks are interdependent (need integration tests)
- [ ] Build plan has strict time constraints (e.g., "must finish before 6 AM")

Current single-agent handles 4 tasks/night in ~8 min. That's plenty.

---
*Generated 2026-02-08 by overnight automation pipeline design session*
