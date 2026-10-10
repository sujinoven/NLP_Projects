import 'package:flutter/material.dart';
import '../models/summary_result.dart';
import '../services/api_service.dart';
import '../widgets/result_panel.dart';
import '../widgets/section_card.dart';

class SummarizerScreen extends StatefulWidget {
  const SummarizerScreen({super.key});
  @override
  State<SummarizerScreen> createState() => _SummarizerScreenState();
}

class _SummarizerScreenState extends State<SummarizerScreen> {
  final _document = TextEditingController();
  final _reference = TextEditingController();
  final _api = ApiService();
  bool _busy = false;
  double _ratio = 0.30;
  int _maxTokens = 220;
  String _connection = 'Checking API…';
  String? _error;
  SummaryResult? _result;

  static const _sample =
      'Acme Corporation agrees to provide software maintenance to Globex Limited '
      'from 1 July 2026 to 30 June 2027. Globex Limited must pay an annual fee of \$50,000 '
      'in four equal quarterly instalments. Acme Corporation must acknowledge critical incidents '
      'within four hours and provide a resolution plan within two business days. '
      'Both parties must protect confidential information and restrict access to authorized staff. '
      'Either party may terminate the agreement with thirty days of written notice. '
      'Termination does not remove the obligation to pay outstanding invoices or protect '
      'confidential information. Neither party may assign this agreement without prior written consent.';

  @override
  void initState() {
    super.initState();
    _checkHealth();
  }

  Future<void> _checkHealth() async {
    try {
      final health = await _api.health();
      if (mounted) {
        setState(
          () => _connection = 'API connected · Model ${health['model_state']}',
        );
      }
    } catch (_) {
      if (mounted) {
        setState(() => _connection = 'API offline · Start the Flask backend');
      }
    }
  }

  Future<void> _summarize() async {
    if (_document.text.trim().isEmpty) {
      setState(() => _error = 'Please paste a document first.');
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
      _result = null;
    });
    try {
      final result = await _api.summarize(
        text: _document.text,
        ratio: _ratio,
        maxTokens: _maxTokens,
        reference: _reference.text,
      );
      if (mounted) setState(() => _result = result);
    } catch (error) {
      if (mounted) setState(() => _error = error.toString());
    } finally {
      if (mounted) {
        setState(() => _busy = false);
        _checkHealth();
      }
    }
  }

  @override
  void dispose() {
    _document.dispose();
    _reference.dispose();
    _api.dispose();
    super.dispose();
  }

  Widget _editor() => SectionCard(
    title: 'Source document',
    subtitle: 'Paste an English contract, clause or compliance notice.',
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Wrap(
          spacing: 8,
          children: [
            TextButton.icon(
              onPressed: _busy
                  ? null
                  : () => setState(() {
                      _document.text = _sample;
                      _result = null;
                      _error = null;
                    }),
              icon: const Icon(Icons.description_outlined),
              label: const Text('Try a sample'),
            ),
            TextButton(
              onPressed: _busy
                  ? null
                  : () => setState(() {
                      _document.clear();
                      _reference.clear();
                      _result = null;
                      _error = null;
                    }),
              child: const Text('Clear'),
            ),
          ],
        ),
        const SizedBox(height: 8),
        TextField(
          controller: _document,
          enabled: !_busy,
          minLines: 12,
          maxLines: 18,
          maxLength: 60000,
          onChanged: (_) => setState(() => _result = null),
          decoration: const InputDecoration(
            hintText: 'Paste your document here…',
            alignLabelWithHint: true,
            labelText: 'Document text',
          ),
        ),
        const SizedBox(height: 16),
        Text('Target summary length: ${(_ratio * 100).round()}% of source'),
        Slider(
          value: _ratio,
          min: 0.1,
          max: 0.6,
          divisions: 10,
          label: '${(_ratio * 100).round()}%',
          onChanged: _busy
              ? null
              : (value) => setState(() {
                  _ratio = value;
                  _result = null;
                }),
        ),
        const Text(
          'Approximate target. Long documents may be compressed further.',
        ),
        const SizedBox(height: 16),
        DropdownButtonFormField<int>(
          initialValue: _maxTokens,
          decoration: const InputDecoration(
            labelText: 'Maximum summary tokens',
          ),
          items: [120, 220, 320, 400]
              .map((n) => DropdownMenuItem(value: n, child: Text('$n tokens')))
              .toList(),
          onChanged: _busy
              ? null
              : (value) => setState(() {
                  _maxTokens = value!;
                  _result = null;
                }),
        ),
        const SizedBox(height: 12),
        ExpansionTile(
          tilePadding: EdgeInsets.zero,
          title: const Text('Optional: evaluate with ROUGE'),
          subtitle: const Text('Add a human-written reference summary.'),
          children: [
            TextField(
              controller: _reference,
              enabled: !_busy,
              minLines: 3,
              maxLines: 6,
              maxLength: 20000,
              onChanged: (_) => setState(() => _result = null),
              decoration: const InputDecoration(labelText: 'Reference summary'),
            ),
          ],
        ),
        const SizedBox(height: 20),
        SizedBox(
          width: double.infinity,
          child: FilledButton.icon(
            onPressed: _busy ? null : _summarize,
            icon: const Icon(Icons.auto_awesome),
            label: Padding(
              padding: const EdgeInsets.symmetric(vertical: 15),
              child: Text(_busy ? 'Summarizing…' : 'Summarize document'),
            ),
          ),
        ),
        if (_error != null)
          Padding(
            padding: const EdgeInsets.only(top: 16),
            child: SelectableText(
              _error!,
              style: const TextStyle(color: Color(0xFFB3261E)),
            ),
          ),
      ],
    ),
  );

  @override
  Widget build(BuildContext context) => Scaffold(
    body: SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1280),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Wrap(
                  spacing: 16,
                  runSpacing: 12,
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: [
                    const Icon(
                      Icons.account_balance_outlined,
                      color: Color(0xFF146B62),
                      size: 30,
                    ),
                    Text(
                      'Legal Summary Studio',
                      style: Theme.of(context).textTheme.headlineSmall
                          ?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    ActionChip(
                      label: Text(_connection),
                      onPressed: _checkHealth,
                    ),
                  ],
                ),
                const SizedBox(height: 32),
                Text(
                  'Less reading. More clarity.',
                  style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 10),
                const Text(
                  'Turn lengthy documents into focused summaries. Review every important obligation against the original.',
                ),
                const SizedBox(height: 28),
                LayoutBuilder(
                  builder: (context, constraints) {
                    final output = ResultPanel(result: _result, busy: _busy);
                    if (constraints.maxWidth < 900) {
                      return Column(
                        children: [
                          _editor(),
                          const SizedBox(height: 20),
                          output,
                        ],
                      );
                    }
                    return Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(child: _editor()),
                        const SizedBox(width: 20),
                        Expanded(child: output),
                      ],
                    );
                  },
                ),
                const SizedBox(height: 24),
                const Text(
                  'English text · BART summarization · Local API',
                  style: TextStyle(color: Color(0xFF63736C)),
                ),
              ],
            ),
          ),
        ),
      ),
    ),
  );
}
