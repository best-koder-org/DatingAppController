#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

TEMPLATES = {
    "ONB-060": '''import 'package:flutter/material.dart';

class FirstNameScreen extends StatefulWidget {
  const FirstNameScreen({super.key});
  @override
  State<FirstNameScreen> createState() => _FirstNameScreenState();
}

class _FirstNameScreenState extends State<FirstNameScreen> {
  final _controller = TextEditingController();
  bool _isValid = false;
  
 @override
  void initState() {
    super.initState();
    _controller.addListener(_validate);
  }
  
  void _validate() {
    final text = _controller.text.trim();
    setState(() => _isValid = RegExp(r"^[a-zA-Z '-]{2,50}$").hasMatch(text));
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(icon: Icon(Icons.arrow_back, color: Colors.black), onPressed: () => Navigator.pop(context)),
        actions: [IconButton(icon: Icon(Icons.close, color: Colors.black), onPressed: () => Navigator.popUntil(context, (route) => route.isFirst))],
      ),
      body: Column(
        children: [
          LinearProgressIndicator(value: 0.2, backgroundColor: Colors.grey[200], valueColor: AlwaysStoppedAnimation(Color(0xFFFF6B6B))),
          Expanded(
            child: Padding(
              padding: EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text("What's your first name?", style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold)),
                  SizedBox(height: 40),
                  TextField(
                    controller: _controller,
                    autofocus: true,
                    textCapitalization: TextCapitalization.words,
                    decoration: InputDecoration(labelText: "First name", border: OutlineInputBorder()),
                  ),
                  SizedBox(height: 16),
                  Text("This is how it'll appear on your profile. Can't change it later.", style: TextStyle(fontSize: 14, color: Colors.grey[600])),
                  Spacer(),
                  SizedBox(
                    width: double.infinity,
                    height: 54,
                    child: ElevatedButton(
                      onPressed: _isValid ? () => Navigator.pushNamed(context, '/onboarding/birthday') : null,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _isValid ? Color(0xFFFF6B6B) : Colors.grey,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(27)),
                      ),
                      child: Text("Next", style: TextStyle(fontSize: 18, color: Colors.white)),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}'''
}

def run(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Failed: {cmd}\\n{result.stderr}")
        sys.exit(1)
    return result.stdout

def main():
    root = Path(__file__).parent.parent
    queue_file = root / ".ai-workspace/task-queue.json"
    
    with open(queue_file) as f:
        queue = json.load(f)
    
    if not queue["queue"]:
        print("✅ No tasks left!")
        return
    
    task = queue["queue"][0]
    task_id = task["id"]
    print(f"🚀 Processing: {task_id} - {task['title']}")
    
    branch = f"automation/{task_id.lower()}-{task['title'].lower().replace(' ', '-')[:30]}"
    mobile_repo = root / "repos/mobile_dejtingapp"
    
    run("git config pull.rebase false", cwd=mobile_repo)
    run("git checkout main && git pull origin main", cwd=mobile_repo)
    run(f"git checkout -b {branch}", cwd=mobile_repo)
    
    file_path = mobile_repo / task["filePath"]
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    if task_id in TEMPLATES:
        file_path.write_text(TEMPLATES[task_id])
        print(f"✅ Created {file_path.name}")
    else:
        print(f"⚠️ No template for {task_id}")
        return
    
    run(f"flutter analyze {file_path}", cwd=mobile_repo)
    print("✅ flutter analyze passed")
    
    run(f"git add {file_path}", cwd=mobile_repo)
    run(f'git commit -m "feat(onboarding): Add {task["title"]} ({task_id})"', cwd=mobile_repo)
    run(f"git push origin {branch}", cwd=mobile_repo)
    run(f'gh pr create --base main --head {branch} --title "feat(onboarding): {task["title"]}" --body "Auto-generated from task queue"', cwd=mobile_repo)
    
    print(f"✅ PR created for {task_id}")
    
    queue["queue"].pop(0)
    queue["completed"].append({**task, "completedAt": datetime.now().isoformat()})
    
    with open(queue_file, "w") as f:
        json.dump(queue, f, indent=2)
    
    print("✅ Done!")

if __name__ == "__main__":
    main()

