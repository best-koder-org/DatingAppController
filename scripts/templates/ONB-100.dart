import 'package:flutter/material.dart';

/// Match Preferences Screen (ONB-100)
/// Single-select: who do you want to see?
class MatchPreferencesScreen extends StatefulWidget {
  const MatchPreferencesScreen({super.key});

  @override
  State<MatchPreferencesScreen> createState() => _MatchPreferencesScreenState();
}

class _MatchPreferencesScreenState extends State<MatchPreferencesScreen> {
  String? _selected;

  static const List<Map<String, dynamic>> _options = [
    {'label': 'Men', 'icon': Icons.male},
    {'label': 'Women', 'icon': Icons.female},
    {'label': 'Everyone', 'icon': Icons.people},
  ];

  bool get _isValid => _selected != null;

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
              // Progress bar (55%)
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: 0.55,
                  backgroundColor: Colors.grey[200],
                  valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFFFF6B6B)),
                  minHeight: 4,
                ),
              ),
              const SizedBox(height: 32),
              const Text(
                'Show me',
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 32),
              // Selection buttons
              ..._options.map((opt) {
                final isSelected = _selected == opt['label'];
                return Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: SizedBox(
                    width: double.infinity,
                    height: 64,
                    child: OutlinedButton.icon(
                      onPressed: () => setState(() => _selected = opt['label'] as String),
                      icon: Icon(
                        opt['icon'] as IconData,
                        color: isSelected ? const Color(0xFFFF6B6B) : Colors.grey[700],
                      ),
                      label: Text(
                        opt['label'] as String,
                        style: TextStyle(
                          fontSize: 18,
                          color: isSelected ? const Color(0xFFFF6B6B) : Colors.black87,
                          fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                        ),
                      ),
                      style: OutlinedButton.styleFrom(
                        side: BorderSide(
                          color: isSelected ? const Color(0xFFFF6B6B) : Colors.grey[300]!,
                          width: isSelected ? 2 : 1,
                        ),
                        backgroundColor: isSelected
                            ? const Color(0xFFFF6B6B).withAlpha(26)
                            : Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ),
                );
              }),
              const Spacer(),
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
