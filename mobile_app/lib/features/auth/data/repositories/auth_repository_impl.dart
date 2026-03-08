import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../../../../core/network/dio_client.dart';

abstract class AuthRepository {
  Future<bool> login(String phone, String password);
  Future<bool> register(String phone, String password);
  Future<void> logout();
  Future<bool> checkAuthStatus();
}

class AuthRepositoryImpl implements AuthRepository {
  final DioClient _dioClient;
  final FlutterSecureStorage _secureStorage;

  AuthRepositoryImpl(this._dioClient, this._secureStorage);

  @override
  Future<bool> login(String phone, String password) async {
    try {
      final path = '/api/v1/auth/login/access-token';
      final response = await _dioClient.dio.post(
        path,
        data: FormData.fromMap({
          'username': phone, // Backend OAuth flow uses 'username' mapped to phone
          'password': password,
        }),
      );
      print("[REPOSITORY] login Calling: ${response.requestOptions.uri}");

      if (response.statusCode == 200) {
        await _secureStorage.write(
            key: 'access_token', value: response.data['access_token']);
        await _secureStorage.write(
            key: 'refresh_token', value: response.data['refresh_token']);
        return true;
      }
      return false;
    } on DioException catch (e) {
      if (e.response != null && e.response?.data != null) {
         final errorData = e.response?.data;
         if (errorData is Map<String, dynamic> && errorData.containsKey('detail')) {
            throw Exception(errorData['detail'].toString());
         }
      }
      throw Exception('Network or server error during login.');
    } catch (e) {
      throw Exception('An unexpected error occurred: $e');
    }
  }

  @override
  Future<bool> register(String phone, String password) async {
    try {
      final path = '/api/v1/auth/register';
      final response = await _dioClient.dio.post(
        path,
        data: {
          'full_name': 'Kisan', // Default name as UI only requires Phone & PIN
          'phone_number': phone,
          'password': password,
          'is_active': true
        },
      );
      print("[REPOSITORY] register Calling: ${response.requestOptions.uri}");

      if (response.statusCode == 200 || response.statusCode == 201) {
        // Auto-login after successful registration
        return await login(phone, password);
      }
      return false;
    } on DioException catch (e) {
      if (e.response != null && e.response?.data != null) {
         final errorData = e.response?.data;
         if (errorData is Map<String, dynamic> && errorData.containsKey('detail')) {
            throw Exception(errorData['detail'].toString()); // Extracted FastAPI validation error
         }
         throw Exception('Server rejected registration. Status: ${e.response?.statusCode}');
      }
      throw Exception('Network error. Is the server running?');
    } catch (e) {
      throw Exception('An unexpected error occurred: $e');
    }
  }

  @override
  Future<void> logout() async {
    await _secureStorage.deleteAll();
  }

  @override
  Future<bool> checkAuthStatus() async {
    final token = await _secureStorage.read(key: 'access_token');
    // Note: To be fully robust, decode the JWT exp date here before returning true.
    return token != null && token.isNotEmpty;
  }
}
