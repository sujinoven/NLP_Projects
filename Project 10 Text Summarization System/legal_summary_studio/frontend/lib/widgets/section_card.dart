import 'package:flutter/material.dart';

class SectionCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final Widget child;
  const SectionCard({
    super.key,
    required this.title,
    required this.subtitle,
    required this.child,
  });

  @override
  Widget build(BuildContext context) => Material(
    color: Colors.white,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(20),
      side: const BorderSide(color: Color(0xFFE0E7E3)),
    ),
    child: Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 6),
          Text(subtitle, style: const TextStyle(color: Color(0xFF63736C))),
          const SizedBox(height: 20),
          child,
        ],
      ),
    ),
  );
}
