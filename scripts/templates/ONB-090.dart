import 'package:flutter/material.dart';

/// Sexual Orientation Screen (ONB-090)
/// Multi-select toggle chips with privacy control
class OrientationScreen extends StatefulWidget {
  const OrientationScreen({super.key});

  @override
  State<OrientationScreen> createState() => _OrientationScreenState();
}

class _OrientationScreenState extends State<OrientationScreen> {
  final Set<String> _selected = {};
  bool _showOnProfile = false;
  static const int _maxSelections = 3;

  static const List<String> _orientations = [
    'Straight',
    'Gay',
    'Lesbian',
    'Bisexual',
    'Asexual',
    'Demisexual',
    'Pansexual',
    'Queer',
    'Questioning',
  ];

  bool get _isValid => _selected.isNotEmpty;

  void _toggleOrientation(String orientation) {
    setState(() {
      if (_selected.contains(orientation)) {
        _selected.remove(orientation);
      } else if (_selected.length < _maxSelections) {
        _selected.add(orientation);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.black),
          onPressed: () => Navigator.of(context).pop(),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.close, color: Colors.black),
            onPressed: () => Navigator.of(context).popUntil((r) => r.isFirst),
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Progress bar (50%)
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: 0.50,
                  backgroundColor: Colors.grey[200],
                  valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFFFF6B6B)),
                  minHeight: 4,
                ),
              ),
              const SizedBox(height: 32),
              const Text(
                "What's your sexual\norientation?",
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Text(
                'Select up to $_maxSelections',
                style: TextStyle(fontSize: 14, color: Colors.grey[600]),
              ),
              const SizedBox(height: 24),
              // Orientation chips
              Expanded(
                child: SingleChildScrollView(
                  child: Wrap(
                    spacing: 10,
                    runSpacing: 10,
                    children: _orientations.map((o) {
                      final isSelected = _selected.contains(o);
                      return ChoiceChip(
                        label: Text(o),
                        selected: isSelected,
                        onSelected: (_) => _toggleOrientation(o),
                        selectedColor: const Color(0xFFFF6B6B).withAlpha(51),
                        backgroundColor: Colors.grey[100],
                        side: BorderSide(
                          color: isSelected ? const Color(0xFFFF6B6B) : Colors.grey[300]!,
                          width: isSelected ? 2 : 1,
                        ),
                        labelStyle: TextStyle(
                          color: isSelected ? const Color(0xFFFF6B6B) : Colors.black87,
                          fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                        ),
                        showCheckmark: false,
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                      );
                    }).toList(),
                  ),
                ),
              ),
              // Privacy toggle
              Row(
                children: [
                  Checkbox(
                    value: _showOnProfile,
                    onChanged: (v) => setState(() => _showOnProfile = v ?? false),
                    activeColor: const Color(0xFFFF6B6B),
                  ),
                  const Expanded(
                    child: Text(
                      'Show my orientation on my profile',
                      style: TextStyle(fontSize: 14),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              // Next button
              SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton(
                  onPressed: _isValid ? () {} : null,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFFF6B6B),
                    foregroundColor: Colors.white,
                    disabledBackgroundColor: Colors.grey[300],
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(26),
                    ),
                  ),
                  child: const Text('Next', style: TextStyle(fontSize: 18)),
                ),
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}
