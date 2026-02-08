#!/usr/bin/env python3
"""
Autonomous Task Processor - NO AI CHAT NEEDED
Reads task-queue.json and implements the next screen
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

TEMPLATES = {'ONB-060': 'import \'package:flutter/material.dart\';\n\nclass FirstNameScreen extends StatefulWidget {\n  const FirstNameScreen({super.key});\n  @override\n  State<FirstNameScreen> createState() => _FirstNameScreenState();\n}\n\nclass _FirstNameScreenState extends State<FirstNameScreen> {\n  final _controller = TextEditingController();\n  bool _isValid = false;\n  \n  @override\n  void initState() {\n    super.initState();\n    _controller.addListener(_validate);\n  }\n  \n  void _validate() {\n    final text = _controller.text.trim();\n    setState(() => _isValid = RegExp(r"^[a-zA-Z \'-]{2,50}$").hasMatch(text));\n  }\n  \n  @override\n  Widget build(BuildContext context) {\n    return Scaffold(\n      backgroundColor: Colors.white,\n      appBar: AppBar(\n        backgroundColor: Colors.white,\n        elevation: 0,\n        leading: IconButton(icon: Icon(Icons.arrow_back, color: Colors.black), onPressed: () => Navigator.pop(context)),\n        actions: [IconButton(icon: Icon(Icons.close, color: Colors.black), onPressed: () => Navigator.popUntil(context, (route) => route.isFirst))],\n      ),\n      body: Column(\n        children: [\n          LinearProgressIndicator(value: 0.2, backgroundColor: Colors.grey[200], valueColor: AlwaysStoppedAnimation(Color(0xFFFF6B6B))),\n          Expanded(\n            child: Padding(\n              padding: EdgeInsets.all(24),\n              child: Column(\n                crossAxisAlignment: CrossAxisAlignment.start,\n                children: [\n                  Text("What\'s your first name?", style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold)),\n                  SizedBox(height: 40),\n                  TextField(\n                    controller: _controller,\n                    autofocus: true,\n                    textCapitalization: TextCapitalization.words,\n                    decoration: InputDecoration(labelText: "First name", border: OutlineInputBorder()),\n                  ),\n                  SizedBox(height: 16),\n                  Text("This is how it\'ll appear on your profile. Can\'t change it later.", style: TextStyle(fontSize: 14, color: Colors.grey[600])),\n                  Spacer(),\n                  SizedBox(\n                    width: double.infinity,\n                    height: 54,\n                    child: ElevatedButton(\n                      onPressed: _isValid ? () => Navigator.pushNamed(context, \'/onboarding/birthday\') : null,\n                      style: ElevatedButton.styleFrom(\n                        backgroundColor: _isValid ? Color(0xFFFF6B6B) : Colors.grey,\n                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(27)),\n                      ),\n                      child: Text("Next", style: TextStyle(fontSize: 18, color: Colors.white)),\n                    ),\n                  ),\n                ],\n              ),\n            ),\n          ),\n        ],\n      ),\n    );\n  }\n}', 'ONB-070': 'import \'package:flutter/material.dart\';\n\nclass BirthdayScreen extends StatefulWidget {\n  const BirthdayScreen({super.key});\n  @override\n  State<BirthdayScreen> createState() => _BirthdayScreenState();\n}\n\nclass _BirthdayScreenState extends State<BirthdayScreen> {\n  int? _month, _day, _year;\n  bool _isValid = false;\n  \n  void _validate() {\n    if (_month == null || _day == null || _year == null) {\n      setState(() => _isValid = false);\n      return;\n    }\n    \n    // Date validation\n    final daysInMonth = [31, (_year! % 4 == 0 && (_year! % 100 != 0 || _year! % 400 == 0)) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];\n    if (_day! > daysInMonth[_month! - 1]) {\n      setState(() => _isValid = false);\n      return;\n    }\n    \n    final now = DateTime.now();\n    if (birthDate.isAfter(now)) {\n      setState(() => _isValid = false);\n      return;\n    }\n    \n    final age = now.year - birthDate.year - ((now.month > birthDate.month || (now.month == birthDate.month && now.day >= birthDate.day)) ? 0 : 1);\n    setState(() => _isValid = age >= 18);\n    \n    if (age < 18) {\n      showDialog(\n        context: context,\n        builder: (ctx) => AlertDialog(\n          title: Text("Age Requirement"),\n          content: Text("You must be 18 or older to use this app."),\n          actions: [TextButton(onPressed: () => Navigator.pop(ctx), child: Text("Go back"))],\n        ),\n      );\n    }\n  }\n  \n  @override\n  Widget build(BuildContext context) {\n    return Scaffold(\n      backgroundColor: Colors.white,\n      appBar: AppBar(\n        backgroundColor: Colors.white,\n        elevation: 0,\n        leading: IconButton(icon: Icon(Icons.arrow_back, color: Colors.black), onPressed: () => Navigator.pop(context)),\n        actions: [IconButton(icon: Icon(Icons.close, color: Colors.black), onPressed: () => Navigator.popUntil(context, (route) => route.isFirst))],\n      ),\n      body: Column(\n        children: [\n          LinearProgressIndicator(value: 0.3, backgroundColor: Colors.grey[200], valueColor: AlwaysStoppedAnimation(Color(0xFFFF6B6B))),\n          Expanded(\n            child: Padding(\n              padding: EdgeInsets.all(24),\n              child: Column(\n                crossAxisAlignment: CrossAxisAlignment.start,\n                children: [\n                  Text("Your b-day?", style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold)),\n                  SizedBox(height: 40),\n                  Row(\n                    children: [\n                      Expanded(\n                        child: DropdownButtonFormField<int>(\n                          decoration: InputDecoration(labelText: "Month", border: OutlineInputBorder()),\n                          items: List.generate(12, (i) => DropdownMenuItem(value: i + 1, child: Text("${i + 1}"))),\n                          onChanged: (v) { _month = v; _validate(); },\n                        ),\n                      ),\n                      SizedBox(width: 8),\n                      Expanded(\n                        child: TextFormField(\n                          decoration: InputDecoration(labelText: "Day", border: OutlineInputBorder()),\n                          keyboardType: TextInputType.number,\n                          onChanged: (v) { _day = int.tryParse(v); _validate(); },\n                        ),\n                      ),\n                      SizedBox(width: 8),\n                      Expanded(\n                        child: TextFormField(\n                          decoration: InputDecoration(labelText: "Year", border: OutlineInputBorder()),\n                          keyboardType: TextInputType.number,\n                          onChanged: (v) { _year = int.tryParse(v); _validate(); },\n                        ),\n                      ),\n                    ],\n                  ),\n                  SizedBox(height: 16),\n                  Text("Your profile shows your age, not your birthdate", style: TextStyle(fontSize: 14, color: Colors.grey[600])),\n                  Spacer(),\n                  SizedBox(\n                    width: double.infinity,\n                    height: 54,\n                    child: ElevatedButton(\n                      onPressed: _isValid ? () => Navigator.pushNamed(context, \'/onboarding/gender\') : null,\n                      style: ElevatedButton.styleFrom(\n                        backgroundColor: _isValid ? Color(0xFFFF6B6B) : Colors.grey,\n                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(27)),\n                      ),\n                      child: Text("Next", style: TextStyle(fontSize: 18, color: Colors.white)),\n                    ),\n                  ),\n                ],\n              ),\n            ),\n          ),\n        ],\n      ),\n    );\n  }\n}', 'ONB-080': 'import \'package:flutter/material.dart\';\n\nclass GenderScreen extends StatefulWidget {\n  const GenderScreen({super.key});\n  @override\n  State<GenderScreen> createState() => _GenderScreenState();\n}\n\nclass _GenderScreenState extends State<GenderScreen> {\n  String? _selectedGender;\n  bool _showGenderOnProfile = false;\n  \n  final _genders = ["Man", "Woman", "Trans Man", "Trans Woman", "Non-binary", "Agender", "Genderfluid", "Genderqueer", "Two-Spirit", "Other"];\n  \n  void _showMoreGenders() {\n    showModalBottomSheet(\n      context: context,\n      isScrollControlled: true,\n      builder: (ctx) => DraggableScrollableSheet(\n        initialChildSize: 0.9,\n        builder: (_, controller) => Column(\n          children: [\n            Padding(\n              padding: EdgeInsets.all(16),\n              child: Text("Select one that best represents you", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),\n            ),\n            TextField(\n              decoration: InputDecoration(hintText: "Search", prefixIcon: Icon(Icons.search), border: OutlineInputBorder()),\n            ),\n            Expanded(\n              child: ListView(\n                controller: controller,\n                children: _genders.map((g) => RadioListTile<String>(\n                  value: g,\n                  groupValue: _selectedGender,\n                  title: Text(g),\n                  onChanged: (v) { setState(() => _selectedGender = v); Navigator.pop(ctx); },\n                )).toList(),\n              ),\n            ),\n          ],\n        ),\n      ),\n    );\n  }\n  \n  @override\n  Widget build(BuildContext context) {\n    return Scaffold(\n      backgroundColor: Colors.white,\n      appBar: AppBar(\n        backgroundColor: Colors.white,\n        elevation: 0,\n        leading: IconButton(icon: Icon(Icons.arrow_back, color: Colors.black), onPressed: () => Navigator.pop(context)),\n        actions: [IconButton(icon: Icon(Icons.close, color: Colors.black), onPressed: () => Navigator.popUntil(context, (route) => route.isFirst))],\n      ),\n      body: Column(\n        children: [\n          LinearProgressIndicator(value: 0.4, backgroundColor: Colors.grey[200], valueColor: AlwaysStoppedAnimation(Color(0xFFFF6B6B))),\n          Expanded(\n            child: Padding(\n              padding: EdgeInsets.all(24),\n              child: Column(\n                crossAxisAlignment: CrossAxisAlignment.start,\n                children: [\n                  Text("What\'s your gender?", style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold)),\n                  SizedBox(height: 40),\n                  _buildGenderButton("Man"),\n                  SizedBox(height: 12),\n                  _buildGenderButton("Woman"),\n                  SizedBox(height: 12),\n                  OutlinedButton(\n                    onPressed: _showMoreGenders,\n                    style: OutlinedButton.styleFrom(minimumSize: Size(double.infinity, 60), side: BorderSide(width: 2)),\n                    child: Text("More →", style: TextStyle(fontSize: 18)),\n                  ),\n                  SizedBox(height: 24),\n                  CheckboxListTile(\n                    value: _showGenderOnProfile,\n                    onChanged: (v) => setState(() => _showGenderOnProfile = v ?? false),\n                    title: Text("Show my gender on my profile"),\n                    controlAffinity: ListTileControlAffinity.leading,\n                  ),\n                  Spacer(),\n                  SizedBox(\n                    width: double.infinity,\n                    height: 54,\n                    child: ElevatedButton(\n                      onPressed: _selectedGender != null ? () => Navigator.pushNamed(context, \'/home\') : null,\n                      style: ElevatedButton.styleFrom(\n                        backgroundColor: _selectedGender != null ? Color(0xFFFF6B6B) : Colors.grey,\n                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(27)),\n                      ),\n                      child: Text("Next", style: TextStyle(fontSize: 18, color: Colors.white)),\n                    ),\n                  ),\n                ],\n              ),\n            ),\n          ),\n        ],\n      ),\n    );\n  }\n  \n  Widget _buildGenderButton(String gender) {\n    final isSelected = _selectedGender == gender;\n    return OutlinedButton(\n      onPressed: () => setState(() => _selectedGender = gender),\n      style: OutlinedButton.styleFrom(\n        minimumSize: Size(double.infinity, 60),\n        side: BorderSide(width: 2, color: isSelected ? Color(0xFFFF6B6B) : Colors.grey),\n        backgroundColor: isSelected ? Color(0xFFFF6B6B).withOpacity(0.1) : null,\n      ),\n      child: Text(gender, style: TextStyle(fontSize: 18, color: isSelected ? Color(0xFFFF6B6B) : Colors.black)),\n    );\n  }\n}'});
  
  @override
  State<FirstNameScreen> createState() => _FirstNameScreenState();
}

class _FirstNameScreenState extends State<FirstNameScreen> {
  final _nameController = TextEditingController();
  bool _isValid = false;
  
  @override
  void initState() {
    super.initState();
    _nameController.addListener(_validate);
  }
  
  void _validate() {
    final text = _nameController.text.trim();
    final valid = RegExp(r"^[a-zA-Z '-]{2,50}$").hasMatch(text);
    setState(() => _isValid = valid);
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(icon: Icon(Icons.arrow_back), onPressed: () => Navigator.pop(context)),
        actions: [IconButton(icon: Icon(Icons.close), onPressed: () => Navigator.popUntil(context, (route) => route.isFirst))],
      ),
      body: Column(
        children: [
          LinearProgressIndicator(value: 0.2, backgroundColor: Colors.grey[200], valueColor: AlwaysStoppedAnimation(Colors.pinkAccent)),
          Padding(
            padding: EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text("What's your first name?", style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold)),
                SizedBox(height: 40),
                TextField(
                  controller: _nameController,
                  autofocus: true,
                  textCapitalization: TextCapitalization.words,
                  decoration: InputDecoration(labelText: "First name"),
                ),
                SizedBox(height: 16),
                Text("This is how it'll appear on your profile. Can't change it later.", style: TextStyle(fontSize: 14, color: Colors.grey)),
                Spacer(),
                SizedBox(
                  width: double.infinity,
                  height: 54,
                  child: ElevatedButton(
                    onPressed: _isValid ? () => Navigator.pushNamed(context, '/onboarding/birthday') : null,
                    style: ElevatedButton.styleFrom(backgroundColor: _isValid ? Colors.pinkAccent : Colors.grey),
                    child: Text("Next"),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
""",
    # Add more templates here...
}

def run(cmd, cwd=None):
    """Run command and return output"""
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout

def main():
    root = Path(__file__).parent.parent
    queue_file = root / ".ai-workspace/task-queue.json"
    
    # Load queue
    with open(queue_file) as f:
        queue = json.load(f)
    
    if not queue["queue"]:
        print("✅ No tasks left!")
        return
    
    task = queue["queue"][0]
    task_id = task["id"]
    print(f"🚀 Processing: {task_id} - {task['title']}")
    
    # Create branch
    branch = f"automation/{task_id.lower()}-{task['title'].lower().replace(' ', '-')[:30]}"
    mobile_repo = root / "repos/mobile_dejtingapp"
    
    run("git checkout main && git pull origin main", cwd=mobile_repo)
    run(f"git checkout -b {branch}", cwd=mobile_repo)
    
    # Generate file
    file_path = mobile_repo / task["filePath"]
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    if task_id in TEMPLATES:
        file_path.write_text(TEMPLATES[task_id])
        print(f"✅ Created {file_path.name}")
    else:
        print(f"⚠️  No template for {task_id} - skipping")
        return
    
    # Validate
    run(f"flutter analyze {file_path}", cwd=mobile_repo)
    print("✅ flutter analyze passed")
    
    # Commit & PR
    run(f"git add {file_path}", cwd=mobile_repo)
    run(f'git commit -m "feat(onboarding): Add {task["title"]} ({task_id})"', cwd=mobile_repo)
    run(f"git push origin {branch}", cwd=mobile_repo)
    run(f'gh pr create --base main --head {branch} --title "feat(onboarding): {task["title"]}" --body "Auto-generated from task queue"', cwd=mobile_repo)
    
    print(f"✅ PR created for {task_id}")
    
    # Update queue
    queue["queue"].pop(0)
    queue["completed"].append({**task, "completedAt": datetime.now().isoformat()})
    
    with open(queue_file, "w") as f:
        json.dump(queue, f, indent=2)
    
    print("✅ Task completed!")

if __name__ == "__main__":
    main()
