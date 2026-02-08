#!/usr/bin/env python3
"""
Queue refill script for DatingApp overnight automation.
Scans ONBOARDING_IMPLEMENTATION_TASKS.md for uncompleted tasks,
respects dependencies, and fills the queue up to BATCH_SIZE.
"""
import json, re, sys
from datetime import datetime
from pathlib import Path

BATCH_SIZE = 4  # Max tasks to queue per run
TASK_SOURCE = "repos/mobile_dejtingapp/ONBOARDING_IMPLEMENTATION_TASKS.md"

# ── Task definitions (hardcoded from task doc) ───────────────────────
# These map TASK-xxx IDs to full queue entries.
# Only onboarding UI tasks (Tier 1, safety-tier 1) for now.
TASK_CATALOG = {
    "ONB-090": {
        "id": "ONB-090",
        "type": "screen",
        "tier": 1,
        "service": "mobile_dejtingapp",
        "title": "Sexual Orientation Screen",
        "filePath": "lib/screens/wizard/orientation_screen.dart",
        "description": "Multi-select orientation screen with toggle chips and privacy control",
        "acceptanceCriteria": [
            "Progress bar (50%)",
            "Header: 'What's your sexual orientation?'",
            "Multi-select toggle chips (Straight, Gay, Lesbian, Bisexual, Asexual, Demisexual, Pansexual, Queer, Questioning)",
            "Can select up to 3 options",
            "Privacy toggle: 'Show my orientation on my profile' (default OFF)",
            "Next button (disabled until >= 1 selection)",
            "Back arrow + close X navigation"
        ],
        "estimatedHours": 4,
        "priority": "high",
        "dependencies": ["ONB-080"],
        "safetyTier": 1,
        "safetyNotes": "Pure UI, hardcoded options, no backend calls",
        "testCommand": "flutter analyze lib/screens/wizard/orientation_screen.dart",
        "referenceFiles": ["lib/screens/wizard/gender_screen.dart"]
    },
    "ONB-100": {
        "id": "ONB-100",
        "type": "screen",
        "tier": 1,
        "service": "mobile_dejtingapp",
        "title": "Match Preferences Screen",
        "filePath": "lib/screens/wizard/match_preferences_screen.dart",
        "description": "Who do you want to match with? Select gender preferences",
        "acceptanceCriteria": [
            "Progress bar (55%)",
            "Header: 'Show me'",
            "3 large selection buttons: Men, Women, Everyone",
            "Single selection (radio behavior)",
            "Next button (disabled until selection made)",
            "No privacy toggle (this is always private)",
            "Back arrow + close X navigation"
        ],
        "estimatedHours": 3,
        "priority": "high",
        "dependencies": ["ONB-090"],
        "safetyTier": 1,
        "safetyNotes": "Simple single selection, hardcoded options",
        "testCommand": "flutter analyze lib/screens/wizard/match_preferences_screen.dart",
        "referenceFiles": ["lib/screens/wizard/gender_screen.dart"]
    },
    "ONB-110": {
        "id": "ONB-110",
        "type": "screen",
        "tier": 1,
        "service": "mobile_dejtingapp",
        "title": "Relationship Goals Screen",
        "filePath": "lib/screens/wizard/relationship_goals_screen.dart",
        "description": "Card grid for selecting relationship goal with emoji icons",
        "acceptanceCriteria": [
            "Progress bar (60%)",
            "Header: 'What are you looking for?'",
            "2x2 card grid with emoji + label: Long-term partner 💑, Long-term open to short 🌊, Short-term open to long 🎯, Short-term fun 🎉, New friends 👋, Still figuring it out 🤔",
            "Single selection with highlight ring",
            "Next button (disabled until selection)",
            "Subtle note: 'Not shown on profile unless you choose'",
            "Back arrow + close X navigation"
        ],
        "estimatedHours": 4,
        "priority": "high",
        "dependencies": ["ONB-100"],
        "safetyTier": 1,
        "safetyNotes": "Pure UI card layout, no API calls",
        "testCommand": "flutter analyze lib/screens/wizard/relationship_goals_screen.dart",
        "referenceFiles": ["lib/screens/wizard/gender_screen.dart"]
    },
    "ONB-120": {
        "id": "ONB-120",
        "type": "screen",
        "tier": 1,
        "service": "mobile_dejtingapp",
        "title": "Interests Selection Screen",
        "filePath": "lib/screens/wizard/interests_screen.dart",
        "description": "Tag cloud / chip selection for user interests with minimum requirement",
        "acceptanceCriteria": [
            "Progress bar (65%)",
            "Header: 'What are you into?'",
            "Scrollable grid of interest chips (30+ options in categories)",
            "Categories: Sports, Creative, Going out, Staying in, Pets, Values, Food & Drink",
            "Multi-select with color toggle (coral border when selected)",
            "Counter showing 'X/5 selected' (minimum 5 required)",
            "Next button disabled until >= 5 selected",
            "Optional search/filter bar at top",
            "Back arrow + close X navigation"
        ],
        "estimatedHours": 5,
        "priority": "high",
        "dependencies": ["ONB-110"],
        "safetyTier": 1,
        "safetyNotes": "Hardcoded interest list, pure UI, no calls",
        "testCommand": "flutter analyze lib/screens/wizard/interests_screen.dart",
        "referenceFiles": ["lib/screens/wizard/orientation_screen.dart"]
    },
    "ONB-130": {
        "id": "ONB-130",
        "type": "screen",
        "tier": 1,
        "service": "mobile_dejtingapp",
        "title": "Photo Upload Grid Screen",
        "filePath": "lib/screens/wizard/photo_upload_screen.dart",
        "description": "6-slot photo grid for uploading profile photos with drag-reorder",
        "acceptanceCriteria": [
            "Progress bar (75%)",
            "Header: 'Add your best photos'",
            "2x3 grid of photo slots (first slot has camera icon, rest have + icon)",
            "Tap slot to open image picker (camera or gallery)",
            "Minimum 2 photos required to proceed",
            "Drag & drop to reorder (optional for MVP, placeholder OK)",
            "Delete button (X) on filled slots",
            "Next button disabled until >= 2 photos",
            "Subtitle: 'Tip: Start with your best close-up 📸'",
            "Back arrow + close X navigation"
        ],
        "estimatedHours": 6,
        "priority": "high",
        "dependencies": ["ONB-120"],
        "safetyTier": 1,
        "safetyNotes": "Uses image_picker package, local files only for MVP, no upload",
        "testCommand": "flutter analyze lib/screens/wizard/photo_upload_screen.dart",
        "referenceFiles": ["lib/screens/wizard/interests_screen.dart"]
    },
    "ONB-140": {
        "id": "ONB-140",
        "type": "screen",
        "tier": 1,
        "service": "mobile_dejtingapp",
        "title": "Location Permission Screen",
        "filePath": "lib/screens/wizard/location_permission_screen.dart",
        "description": "Friendly location permission request with map illustration",
        "acceptanceCriteria": [
            "Progress bar (85%)",
            "Header: 'Where are you?'",
            "Map pin illustration or icon (placeholder image OK)",
            "Body text: 'We use your location to show people nearby. We never share your exact location.'",
            "Large coral 'Allow Location' button",
            "Small 'Enter manually' link underneath",
            "On tap: request system location permission",
            "If denied: show 'Enter manually' city input field",
            "Back arrow + close X navigation"
        ],
        "estimatedHours": 4,
        "priority": "high",
        "dependencies": ["ONB-130"],
        "safetyTier": 1,
        "safetyNotes": "Permission request only; actual geo logic comes in later task",
        "testCommand": "flutter analyze lib/screens/wizard/location_permission_screen.dart",
        "referenceFiles": ["lib/screens/wizard/photo_upload_screen.dart"]
    },
    "ONB-150": {
        "id": "ONB-150",
        "type": "screen",
        "tier": 1,
        "service": "mobile_dejtingapp",
        "title": "Notification Permission Screen",
        "filePath": "lib/screens/wizard/notification_permission_screen.dart",
        "description": "Push notification opt-in screen",
        "acceptanceCriteria": [
            "Progress bar (90%)",
            "Header: 'Never miss a match!'",
            "Bell icon illustration",
            "Body: 'Turn on notifications so you know when someone likes you or sends a message.'",
            "Large coral 'Turn on notifications' button",
            "Small 'Not now' skip link",
            "On tap: request system notification permission",
            "Skip always allowed (non-blocking)",
            "Back arrow + close X navigation"
        ],
        "estimatedHours": 3,
        "priority": "medium",
        "dependencies": ["ONB-140"],
        "safetyTier": 1,
        "safetyNotes": "Permission request only, non-blocking skip",
        "testCommand": "flutter analyze lib/screens/wizard/notification_permission_screen.dart",
        "referenceFiles": ["lib/screens/wizard/location_permission_screen.dart"]
    },
    "ONB-160": {
        "id": "ONB-160",
        "type": "screen",
        "tier": 1,
        "service": "mobile_dejtingapp",
        "title": "Onboarding Complete Screen",
        "filePath": "lib/screens/wizard/onboarding_complete_screen.dart",
        "description": "Success/celebration screen at end of onboarding wizard",
        "acceptanceCriteria": [
            "Progress bar (100%)",
            "Celebration emoji/animation 🎉",
            "Header: 'You are all set!'",
            "Body: 'Your profile is ready. Time to start swiping!'",
            "Large coral 'Start Exploring' button",
            "Button navigates to main app (home/swipe screen placeholder)",
            "No back navigation (final step)",
            "Confetti animation (optional, placeholder OK)"
        ],
        "estimatedHours": 3,
        "priority": "high",
        "dependencies": ["ONB-150"],
        "safetyTier": 1,
        "safetyNotes": "Pure UI celebration, navigates to app root",
        "testCommand": "flutter analyze lib/screens/wizard/onboarding_complete_screen.dart",
        "referenceFiles": ["lib/screens/wizard/notification_permission_screen.dart"]
    },
}

def main():
    root = Path(__file__).parent.parent
    queue_file = root / ".ai-workspace/task-queue.json"

    with open(queue_file) as f:
        queue = json.load(f)

    # Collect all known IDs (completed + in-progress + already queued)
    done_ids = {t["id"] for t in queue.get("completed", [])}
    progress_ids = {t["id"] for t in queue.get("inProgress", [])}
    queued_ids = {t["id"] for t in queue.get("queue", [])}
    known_ids = done_ids | progress_ids | queued_ids

    print(f"Queue state: {len(queue.get('queue',[]))} queued, {len(progress_ids)} in-progress, {len(done_ids)} completed")
    print(f"Known IDs: {sorted(known_ids)}")

    # Find eligible tasks (not known + dependencies met)
    eligible = []
    for tid, task in TASK_CATALOG.items():
        if tid in known_ids:
            continue
        deps = task.get("dependencies", [])
        if all(d in done_ids for d in deps):
            eligible.append(task)

    if not eligible:
        print("NO_ELIGIBLE_TASKS")
        return

    # Sort by priority, then by ID number
    def sort_key(t):
        p = {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(t.get("priority", "medium"), 2)
        num = int(re.search(r'\d+', t["id"]).group()) if re.search(r'\d+', t["id"]) else 999
        return (p, num)

    eligible.sort(key=sort_key)
    batch = eligible[:BATCH_SIZE]

    print(f"\nRefilling queue with {len(batch)} tasks:")
    for t in batch:
        print(f"  + {t['id']}: {t['title']} (deps: {t.get('dependencies', [])})")
        queue["queue"].append(t)

    queue["lastUpdated"] = datetime.now().isoformat()

    with open(queue_file, "w") as f:
        json.dump(queue, f, indent=2)

    print(f"\nQueue now has {len(queue['queue'])} tasks ready to process")

if __name__ == "__main__":
    main()
