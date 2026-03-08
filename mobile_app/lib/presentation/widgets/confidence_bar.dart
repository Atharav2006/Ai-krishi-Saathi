import 'package:flutter/material.dart';

class ConfidenceBar extends StatelessWidget {
  final double confidence;

  const ConfidenceBar({super.key, required this.confidence});

  @override
  Widget build(BuildContext context) {
    Color barColor;
    if (confidence > 0.8) {
      barColor = Colors.green;
    } else if (confidence > 0.5) {
      barColor = Colors.orange;
    } else {
      barColor = Colors.red;
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'Confidence Score',
              style: TextStyle(fontSize: 14, color: Colors.black54),
            ),
            Text(
              '${(confidence * 100).toStringAsFixed(1)}%',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                color: barColor,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: confidence,
            minHeight: 8,
            backgroundColor: barColor.withOpacity(0.1),
            valueColor: AlwaysStoppedAnimation<Color>(barColor),
          ),
        ),
      ],
    );
  }
}
