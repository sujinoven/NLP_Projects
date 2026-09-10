import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/summary_result.dart';

class ApiException implements Exception {
  final String message;
  ApiException(this.message);
  @override
  String toString() => message;
}

class ApiService {
  final http.Client _client;
  final String baseUrl;
  ApiService({http.Client? client, this.baseUrl = ApiConfig.baseUrl})
    : _client = client ?? http.Client();

  Future<Map<String, dynamic>> health() async {
    final response = await _client
        .get(Uri.parse('$baseUrl/api/health'))
        .timeout(const Duration(seconds: 8));
    if (response.statusCode != 200) {
      throw ApiException('API health check failed (${response.statusCode}).');
    }
    return Map<String, dynamic>.from(jsonDecode(response.body) as Map);
  }

  Future<SummaryResult> summarize({
    required String text,
    required double ratio,
    required int maxTokens,
    String? reference,
  }) async {
    try {
      final response = await _client
          .post(
            Uri.parse('$baseUrl/api/summarize'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'text': text,
              'target_ratio': ratio,
              'max_summary_tokens': maxTokens,
              if (reference != null && reference.trim().isNotEmpty)
                'reference': reference.trim(),
            }),
          )
          .timeout(const Duration(minutes: 15));
      final json = Map<String, dynamic>.from(jsonDecode(response.body) as Map);
      if (response.statusCode != 200) {
        throw ApiException(json['error']?.toString() ?? 'Request failed.');
      }
      return SummaryResult.fromJson(json);
    } on TimeoutException {
      throw ApiException(
        'Request timed out. The backend may still be working; check its terminal before retrying.',
      );
    } on http.ClientException {
      throw ApiException(
        'Cannot reach the API. Check the backend, API_BASE_URL and CORS origin.',
      );
    } on FormatException {
      throw ApiException(
        'The API returned an unexpected response. Check its terminal.',
      );
    }
  }

  void dispose() => _client.close();
}
