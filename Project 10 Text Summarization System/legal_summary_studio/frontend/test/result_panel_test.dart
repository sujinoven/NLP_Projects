import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:legal_summary_studio/widgets/result_panel.dart';

void main() {
  testWidgets('shows empty result state', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(child: ResultPanel(busy: false)),
        ),
      ),
    );
    expect(find.text('A clearer view starts here.'), findsOneWidget);
  });

  testWidgets('shows loading state', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(child: ResultPanel(busy: true)),
        ),
      ),
    );
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });
}
