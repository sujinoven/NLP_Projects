class ApiConfig {
  // Override at build/run time with --dart-define=API_BASE_URL=http://...
  static const baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://127.0.0.1:5001',
  );
}
