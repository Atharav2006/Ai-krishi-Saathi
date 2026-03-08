import 'dart:convert';
import 'dart:math';
import 'package:dio/dio.dart';
import '../../../../core/localization/app_strings.dart';
import '../../../../core/localization/language_provider.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/database/database_helper.dart';
import 'package:sqflite/sqflite.dart';
import 'package:uuid/uuid.dart';

abstract class CropPricesRepository {
  Future<List<Map<String, dynamic>>> getMandiPrices({required String cropId, required String districtId});
  Future<Map<String, dynamic>> predictPrice({required String cropId, required String districtId});
}

class CropPricesRepositoryImpl implements CropPricesRepository {
  final DioClient _dioClient;
  final DatabaseHelper _dbHelper;

  CropPricesRepositoryImpl(this._dioClient, this._dbHelper);

  @override
  Future<List<Map<String, dynamic>>> getMandiPrices({required String cropId, required String districtId}) async {
    final db = await _dbHelper.database;
    
    try {
      // Attempt Network Fetch
      final path = '/api/v1/agtech/mandi-prices';
      final response = await _dioClient.dio.get(
        path,
        queryParameters: {
          'crop_id': cropId,
          'district_id': districtId,
          'page': 1,
          'size': 50
        }
      );
      
      final List data = response.data['data'];
      
      // Update Cache securely tracking timestamp
      Batch batch = db.batch();
      for (var item in data) {
         batch.insert('cached_mandi_prices', {
           'id': item['id'],
           'crop_id': item['crop_id'],
           'market_id': item['market_id'],
           'price_date': item['price_date'],
           'modal_price': item['modal_price'],
           'timestamp_synced': DateTime.now().millisecondsSinceEpoch
         }, conflictAlgorithm: ConflictAlgorithm.replace);
      }
      await batch.commit(noResult: true);
      
      return List<Map<String, dynamic>>.from(data);
      
    } catch (e) {
      // Fallback to SQLite Cache
      final cachedData = await db.query(
        'cached_mandi_prices',
        where: 'crop_id = ?',
        whereArgs: [cropId],
        orderBy: 'price_date DESC',
        limit: 50
      );
      return cachedData;
    }
  }

  @override
  Future<Map<String, dynamic>> predictPrice({required String cropId, required String districtId}) async {
    final db = await _dbHelper.database;
    final now = DateTime.now().millisecondsSinceEpoch;

    // 1. Try fetching fresh from API (Live) - Priority 1
    try {
      final path = '/api/v1/forecasts';
      
      final response = await _dioClient.dio.get(path, queryParameters: {
        'district': districtId,
        'crops': cropId,
      });
      print("[REPOSITORY] predictPrice Calling: ${response.requestOptions.uri}");

      if (response.statusCode == 200) {
        final data = response.data;
        if (data['forecasts'] != null && data['forecasts'].isNotEmpty) {
           final forecastDays = data['forecasts'][0]['forecast'];
           
           // Update Cache
           await db.insert(
             'forecast_cache',
             {
               'district': districtId,
               'crop': cropId,
               'forecast_json': jsonEncode(forecastDays),
               'synced_at': now,
             },
             conflictAlgorithm: ConflictAlgorithm.replace,
           );

           return {
             'predicted_price': forecastDays[0]['price'],
             'forecast_days': forecastDays,
             'is_offline_cached': false,
             'is_offline_mock': false,
             'advisory': _generateAdvisory(forecastDays),
           };
        } else {
           // Success but no data for this specific district/crop
           return {
             'predicted_price': 0.0,
             'forecast_days': [],
             'is_offline_cached': false,
             'is_offline_mock': false,
             'advisory': AppStrings.get('data_unavailable', languageProvider.langCode),
           };
        }
      }
    } on DioException catch (e) {
      print("[REPOSITORY] predictPrice DioError: ${e.type} | ${e.message}");
      if (e.response != null) {
        print("[REPOSITORY] Status: ${e.response?.statusCode} | Data: ${e.response?.data}");
      }
    } catch (e) {
      print("[REPOSITORY] predictPrice UnexpectedError: $e");
    }

    // 2. Check Local SQLite Forecast Cache - Priority 2 (Fallback)
    try {
      final cached = await db.query(
        'forecast_cache',
        where: 'district = ? AND crop = ?',
        whereArgs: [districtId, cropId],
        limit: 1,
      );

      if (cached.isNotEmpty) {
        final syncedAt = cached.first['synced_at'] as int;
        // If cache exists, use it as fallback
        final forecastJson = jsonDecode(cached.first['forecast_json'] as String);
        double predicted = forecastJson[0]['price'] ?? 0.0;
        return {
          'predicted_price': predicted,
          'forecast_days': forecastJson,
          'is_offline_cached': true,
          'advisory': _generateAdvisory(forecastJson),
        };
      }
    } catch (e) {
      print("Cache read error: $e");
    }

    // 3. Ultra-Offline Failsafe: 0.6 * last + 0.4 * 7-day MA using Historical Prices
    try {
      final history = await db.query(
        'cached_mandi_prices',
        where: 'crop_id = ?',
        whereArgs: [cropId],
        orderBy: 'price_date DESC',
        limit: 7,
      );

      double fallbackPrice = 2000.0; // Hard fallback
      
      if (history.isNotEmpty) {
        double lastKnown = history.first['modal_price'] as double;
        double sum = 0;
        int count = 0;
        for (var row in history) {
           sum += (row['modal_price'] as double);
           count++;
        }
        double movingAvg = sum / count;
        fallbackPrice = (0.6 * lastKnown) + (0.4 * movingAvg);
      } else {
        // Ultimate Seed Fallback if zero history exists
        final int seed = "\${cropId}_\$districtId".hashCode.abs();
        if (cropId.contains('apple')) fallbackPrice = 8500.0 + (seed % 1000);
        else if (cropId.contains('cotton')) fallbackPrice = 6000.0 + (seed % 800);
        else if (cropId.contains('onion')) fallbackPrice = 1500.0 + (seed % 1500);
        else if (cropId.contains('tomato')) fallbackPrice = 1800.0 + (seed % 2000);
        else if (cropId.contains('wheat')) fallbackPrice = 2700.0 + (seed % 400);
        else fallbackPrice = 2100.0 + (seed % 500);
      }

      List<Map<String, dynamic>> forecastDays = [];
      double currentPrice = fallbackPrice;
      
      for (int i = 0; i < 7; i++) {
        // Flattened out predictive curve (-1% to +1% daily shift)
        double percentShift = ((i % 3) - 1) / 100.0;
        currentPrice = currentPrice + (currentPrice * percentShift);
        currentPrice = (currentPrice / 10).roundToDouble() * 10;
        
        forecastDays.add({
          'price': currentPrice,
          'confidence': max(0.40, 0.70 - (i * 0.05)), // Low confidence indicator
        });
      }

      return {
        'predicted_price': fallbackPrice,
        'forecast_days': forecastDays,
        'is_offline_mock': true,
        'advisory': AppStrings.get('advisory_offline_mock', languageProvider.langCode),
      };
      
    } catch (e) {
       return {
         'predicted_price': 0.0,
         'forecast_days': [],
       };
    }
  }

  double max(double a, double b) => a > b ? a : b;

  String _generateAdvisory(List<dynamic> forecastDays) {
    if (forecastDays.isEmpty) return AppStrings.get('advisory_no_data', languageProvider.langCode);
    
    double firstPrice = (forecastDays.first['price'] is int)
        ? (forecastDays.first['price'] as int).toDouble()
        : forecastDays.first['price'] as double;
    double maxFuturePrice = firstPrice;
    
    for (var day in forecastDays) {
      double p = (day['price'] is int)
          ? (day['price'] as int).toDouble()
          : day['price'] as double;
      if (p > maxFuturePrice) maxFuturePrice = p;
    }

    if (maxFuturePrice > firstPrice) {
      double percentIncrease = ((maxFuturePrice - firstPrice) / firstPrice) * 100;
      String pct = percentIncrease.toStringAsFixed(1);
      return AppStrings.get('advisory_increase', languageProvider.langCode).replaceAll('%s', pct);
    } else {
      return AppStrings.get('advisory_decrease', languageProvider.langCode);
    }
  }
}
