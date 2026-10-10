import 'package:flutter/material.dart';
import 'screens/summarizer_screen.dart';

class LegalSummaryApp extends StatelessWidget {
  const LegalSummaryApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'Legal Summary Studio',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF146B62)),
      scaffoldBackgroundColor: const Color(0xFFF4F6F5),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: const Color(0xFFF8FAF9),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
      ),
    ),
    home: const SummarizerScreen(),
  );
}
