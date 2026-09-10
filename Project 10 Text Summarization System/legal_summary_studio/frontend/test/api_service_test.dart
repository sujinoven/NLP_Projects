import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:legal_summary_studio/services/api_service.dart';

void main() {
  test('sends API fields and handles nullable evaluation', () async {
    final service = ApiService(
      client: MockClient((request) async {
        final body = jsonDecode(request.body) as Map;
        expect(body['text'], 'Document');
        expect(body['target_ratio'], 0.3);
        expect(body.containsKey('reference'), false);
        return http.Response(
          jsonEncode({
            'summary': 'Summary',
            'input_tokens': 100,
            'summary_tokens': 25,
            'chunks': 1,
            'passes': 1,
            'compression_ratio': 0.25,
            'elapsed_seconds': 1.2,
            'facts': {'match_precision': null},
            'rouge': null,
            'warnings': <String>[],
          }),
          200,
        );
      }),
    );
    final result = await service.summarize(
      text: 'Document',
      ratio: 0.3,
      maxTokens: 220,
    );
    expect(result.summary, 'Summary');
    expect(result.rouge, isNull);
    service.dispose();
  });

  test('surfaces API busy response', () async {
    final service = ApiService(
      client: MockClient(
        (request) async => http.Response('{"error":"Model busy"}', 429),
      ),
    );
    await expectLater(
      service.summarize(text: 'Document', ratio: 0.3, maxTokens: 220),
      throwsA(
        isA<ApiException>().having((e) => e.message, 'message', 'Model busy'),
      ),
    );
    service.dispose();
  });
}
