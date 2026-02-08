import 'package:flutter/material.dart';

/// Interests Selection Screen (ONB-120)
/// Tag cloud with categorized chips, min 5 selection
class InterestsScreen extends StatefulWidget {
  const InterestsScreen({super.key});

  @override
  State<InterestsScreen> createState() => _InterestsScreenState();
}

class _InterestsScreenState extends State<InterestsScreen> {
  final Set<String> _selected = {};
  static const int _minRequired = 5;

  static const Map<String, List<String>> _categories = {
    'Sports': ['Running', 'Yoga', 'Gym', 'Swimming', 'Cycling', 'Hiking'],
    'Creative': ['Photography', 'Art', 'Music', 'Writing', 'Dancing'],
    'Going out': ['Restaurants', 'Bars', 'Concerts', 'Theater', 'Festivals'],
    'Staying in': ['Netflix', 'Gaming', 'Cooking', 'Reading', 'Board Games'],
    'Pets': ['Dogs', 'Cats', 'Plants'],
    'Values': ['Environmentalism', 'Volunteering', 'Family', 'Spirituality'],
    'Food & Drink': ['Coffee', 'Wine', 'Vegan', 'Foodie', 'Baking'],
  };

  bool get _isValid => _selected.length >= _minRequired;

  void _toggleInterest(String interest) {
    setState(() {
      if (_selected.contains(interest)) {
        _selected.remove(interest);
      } else {
        _selected.add(interest);
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
              // Progress bar (65%)
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: 0.65,
                  backgroundColor: Colors.grey[200],
                  valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFFFF6B6B)),
                  minHeight: 4,
                ),
              ),
              const SizedBox(height: 32),
              const Text(
                'What are you into?',
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Text(
                '${_selected.length}/$_minRequired selected',
                style: TextStyle(
                  fontSize: 14,
                  color: _isValid ? const Color(0xFF4CAF50) : Colors.grey[600],
                  fontWeight: _isValid ? FontWeight.w600 : FontWeight.normal,
                ),
              ),
              const SizedBox(height: 16),
              // Scrollable interest categories
              Expanded(
                child: SingleChildScrollView(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: _categories.entries.map((entry) {
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              entry.key,
                              style: TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.w600,
                                color: Colors.grey[700],
                              ),
                            ),
                            const SizedBox(height: 8),
                            Wrap(
                              spacing: 8,
                              runSpacing: 8,
                              children: entry.value.map((interest) {
                                final isSelected = _selected.contains(interest);
                                return ChoiceChip(
                                  label: Text(interest),
                                  selected: isSelected,
                                  onSelected: (_) => _toggleInterest(interest),
                                  selectedColor: const Color(0xFFFF6B6B).withAlpha(51),
                                  backgroundColor: Colors.grey[100],
                                  side: BorderSide(
                                    color: isSelected ? const Color(0xFFFF6B6B) : Colors.grey[300]!,
                                    width: isSelected ? 2 : 1,
                                  ),
                                  labelStyle: TextStyle(
                                    color: isSelected ? const Color(0xFFFF6B6B) : Colors.black87,
                                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                                    fontSize: 13,
                                  ),
                                  showCheckmark: false,
                                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                                );
                              }).toList(),
                            ),
                          ],
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ),
              const SizedBox(height: 12),
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
