import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../models/summary_result.dart';
import 'section_card.dart';

class ResultPanel extends StatelessWidget {
  final SummaryResult? result;
  final bool busy;
  const ResultPanel({super.key, this.result, required this.busy});

  Widget items(String heading, List<dynamic> values) => ExpansionTile(
    tilePadding: EdgeInsets.zero,
    title: Text('$heading (${values.length})'),
    children: [
      Align(
        alignment: Alignment.centerLeft,
        child: Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: SelectableText(
            values.isEmpty ? 'None detected.' : values.join(' • '),
          ),
        ),
      ),
    ],
  );

  @override
  Widget build(BuildContext context) {
    final r = result;
    return SectionCard(
      title: 'Your summary',
      subtitle: 'The important details, in fewer words.',
      child: busy
          ? const Padding(
              padding: EdgeInsets.symmetric(vertical: 70),
              child: Center(
                child: Column(
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 24),
                    Text('Reading and summarizing…'),
                    SizedBox(height: 8),
                    Text(
                      'The first request may download the model.',
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            )
          : r == null
          ? const Padding(
              padding: EdgeInsets.symmetric(vertical: 80),
              child: Center(
                child: Column(
                  children: [
                    Icon(
                      Icons.auto_awesome_outlined,
                      size: 44,
                      color: Color(0xFF146B62),
                    ),
                    SizedBox(height: 16),
                    Text('A clearer view starts here.'),
                    SizedBox(height: 8),
                    Text(
                      'Add a document and select Summarize.',
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            )
          : Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    Chip(
                      label: Text(
                        '${r.inputTokens} → ${r.summaryTokens} tokens',
                      ),
                    ),
                    Chip(
                      label: Text(
                        '${(r.compressionRatio * 100).toStringAsFixed(0)}% of source',
                      ),
                    ),
                    Chip(
                      label: Text(
                        '${r.elapsedSeconds.toStringAsFixed(1)} seconds',
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                SelectableText(
                  r.summary,
                  style: const TextStyle(fontSize: 17, height: 1.65),
                ),
                const SizedBox(height: 12),
                OutlinedButton.icon(
                  onPressed: () async {
                    await Clipboard.setData(ClipboardData(text: r.summary));
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Summary copied.')),
                      );
                    }
                  },
                  icon: const Icon(Icons.copy_outlined),
                  label: const Text('Copy summary'),
                ),
                const Divider(height: 32),
                Text(
                  'Fact matches',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 8),
                Text(
                  r.facts['match_precision'] == null
                      ? 'Not assessed: no supported patterns were detected.'
                      : '${((r.facts['match_precision'] as num) * 100).toStringAsFixed(0)}% of extracted summary items matched the source.',
                ),
                items('Matched items', r.facts['matched'] as List),
                items(
                  'Not found in source',
                  r.facts['not_found_in_source'] as List,
                ),
                items(
                  'Source items absent from summary',
                  r.facts['source_items_not_in_summary'] as List,
                ),
                Text(
                  r.facts['note'] as String,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                if (r.rouge != null) ...[
                  const Divider(height: 32),
                  Text(
                    'ROUGE against your reference',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Reference overlap, not factual accuracy. Scores shown as percentages.',
                  ),
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: DataTable(
                      horizontalMargin: 0,
                      columnSpacing: 20,
                      columns: const [
                        DataColumn(label: Text('Metric')),
                        DataColumn(label: Text('Precision')),
                        DataColumn(label: Text('Recall')),
                        DataColumn(label: Text('F1')),
                      ],
                      rows: r.rouge!.entries
                          .map(
                            (entry) => DataRow(
                              cells: [
                                DataCell(Text(entry.key.toUpperCase())),
                                for (final key in ['precision', 'recall', 'f1'])
                                  DataCell(
                                    Text(
                                      '${((entry.value[key] as num) * 100).toStringAsFixed(1)}%',
                                    ),
                                  ),
                              ],
                            ),
                          )
                          .toList(),
                    ),
                  ),
                ],
                const SizedBox(height: 16),
                Text(
                  '${r.chunks} input chunk(s) · ${r.passes} generation pass(es)',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                for (final warning in r.warnings)
                  Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      warning,
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ),
              ],
            ),
    );
  }
}
