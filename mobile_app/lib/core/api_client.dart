import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

const String _baseUrl = 'http://localhost:8000/api/v1';
const _storage = FlutterSecureStorage();

final dioProvider = Provider<Dio>((ref) {
  final dio = Dio(BaseOptions(
    baseUrl: _baseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 30),
    headers: {'Content-Type': 'application/json'},
  ));

  // Auth interceptor: inject JWT token
  dio.interceptors.add(InterceptorsWrapper(
    onRequest: (options, handler) async {
      final token = await _storage.read(key: 'access_token');
      if (token != null) {
        options.headers['Authorization'] = 'Bearer $token';
      }
      handler.next(options);
    },
    onError: (error, handler) async {
      if (error.response?.statusCode == 401) {
        await _storage.delete(key: 'access_token');
        // Navigation to login handled by router redirect
      }
      handler.next(error);
    },
  ));

  return dio;
});

final secureStorageProvider = Provider<FlutterSecureStorage>((_) => _storage);
