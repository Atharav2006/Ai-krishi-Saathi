import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:dio_smart_retry/dio_smart_retry.dart';

class CustomInterceptors extends Interceptor {
  final FlutterSecureStorage secureStorage = const FlutterSecureStorage();

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    final token = await secureStorage.read(key: 'access_token');
    
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    options.headers['Content-Type'] = 'application/json';
    options.headers['Accept'] = 'application/json';
    
    super.onRequest(options, handler);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      // TODO: Implement Token Refresh Logic silently here using 'refresh_token'
      // For now, logging out the user if verification fails
    }
    super.onError(err, handler);
  }
}

class DioClient {
  static final DioClient _instance = DioClient._internal();
  factory DioClient() => _instance;
  late Dio dio;

  DioClient._internal() {
    dio = Dio(
      BaseOptions(
        // adb reverse tcp:8000 tcp:8000 tunnels phone -> PC
        baseUrl: 'http://127.0.0.1:8000',
        connectTimeout: const Duration(seconds: 12),
        receiveTimeout: const Duration(seconds: 12),
      ),
    );

    dio.interceptors.add(CustomInterceptors());
    
    // Log every request & error so we can debug in Flutter console
    dio.interceptors.add(LogInterceptor(
      requestBody: false,
      responseBody: false,
      requestHeader: false,
      error: true,
      logPrint: (obj) => print('[DIO] $obj'),
    ));
    
    // Retry once on failure
    dio.interceptors.add(RetryInterceptor(
      dio: dio,
      logPrint: print,
      retries: 1,
      retryDelays: const [Duration(seconds: 2)],
    ));
  }
}

