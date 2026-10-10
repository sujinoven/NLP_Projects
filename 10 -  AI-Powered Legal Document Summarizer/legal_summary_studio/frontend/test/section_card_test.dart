import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:legal_summary_studio/widgets/section_card.dart';

void main() {
  testWidgets('expansion tiles inside cards have a valid Material surface', (
    tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: SectionCard(
              title: 'Evaluation',
              subtitle: 'Optional reference',
              child: ExpansionTile(
                title: Text('Open details'),
                children: [Text('Details')],
              ),
            ),
          ),
        ),
      ),
    );
    expect(tester.takeException(), isNull);
    await tester.tap(find.text('Open details'));
    await tester.pumpAndSettle();
    expect(find.text('Details'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
