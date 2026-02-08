import 'package:flutter/material.dart';

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
}
