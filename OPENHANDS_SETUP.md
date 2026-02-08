# OpenHands Setup - Ready to Run! 🚀

## ✅ You Have:
- Docker installed and running
- OpenHands image downloaded (1.9GB)
- Startup script ready
- Task queue with 3 screens to implement

## 🔑 Step 1: Set Your API Key

```bash
export ANTHROPIC_API_KEY='sk-ant-api03-...'  # Your actual key
```

## 🚀 Step 2: Launch OpenHands

```bash
cd /home/m/development/DatingAppController
./start-openhands.sh
```

This will:
- Pull the runtime container (one-time, ~2GB)
- Start OpenHands GUI on http://localhost:3000
- Mount your workspace at /workspace

## 📝 Step 3: Give It the Task

When the web UI opens, paste this into the chat:

```
Read .ai-workspace/task-queue.json and implement the next onboarding screen (ONB-060: First Name Entry Screen).

Steps:
1. cd repos/mobile_dejtingapp
2. git checkout main && git pull
3. Create branch: automation/onb-060-first-name-screen
4. Generate lib/screens/wizard/first_name_screen.dart following the spec
5. Run: flutter analyze lib/screens/wizard/first_name_screen.dart
6. Commit with message: "feat(onboarding): Add First Name Entry Screen (ONB-060)"
7. Push and create PR via: gh pr create --base main --head automation/onb-060-first-name-screen --title "feat(onboarding): First Name Entry Screen" --body "Implements ONB-060 from task queue"
8. Update .ai-workspace/task-queue.json: move ONB-060 from queue to completed
```

## 🎯 What Will Happen

OpenHands will:
- Read the task spec from JSON
- Generate Flutter code matching acceptance criteria
- Validate with flutter analyze  
- Create git branch, commit, push
- Create PR on GitHub
- Update the task queue

All autonomously! 🤖

## 📊 Monitor Progress

- Watch the terminal output
- Check http://localhost:3000 for the web UI
- PRs will appear at: https://github.com/best-koder-ever/mobile_dejtingapp/pulls

## 🛑 To Stop

Press Ctrl+C in the terminal

## 💰 Cost

~$0.03 per screen × 3 screens = **$0.09 total**

---

**Ready? Run: `./start-openhands.sh`**
