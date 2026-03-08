import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:sqflite/sqflite.dart';
import '../database/database_helper.dart';
import '../network/dio_client.dart';
import 'package:dio/dio.dart';
import 'dart:convert';
import 'dart:async';

enum SyncStatus { online, offline, syncing }

class SyncManager {
  static final SyncManager _instance = SyncManager._internal();
  factory SyncManager() => _instance;
  SyncManager._internal();

  final DatabaseHelper _dbHelper = DatabaseHelper();
  final DioClient _dioClient = DioClient();
  final Connectivity _connectivity = Connectivity();

  final _statusController = StreamController<SyncStatus>.broadcast();
  Stream<SyncStatus> get statusStream => _statusController.stream;

  final _queueCountController = StreamController<int>.broadcast();
  Stream<int> get queueCountStream => _queueCountController.stream;

  Future<void> initializeSyncListener() async {
    // Initial check
    final result = await _connectivity.checkConnectivity();
    _updateStatus(result);

    _connectivity.onConnectivityChanged.listen((ConnectivityResult result) async {
      _updateStatus(result);
      if (result == ConnectivityResult.mobile || result == ConnectivityResult.wifi) {
        await executePendingSyncQueue();
      }
    });

    // Periodically update queue count
    Timer.periodic(const Duration(seconds: 5), (_) => _updateQueueCount());
  }

  void _updateStatus(ConnectivityResult result) {
    if (result == ConnectivityResult.none) {
      _statusController.add(SyncStatus.offline);
    } else {
      _statusController.add(SyncStatus.online);
    }
  }

  Future<void> _updateQueueCount() async {
    final db = await _dbHelper.database;
    final result = await db.rawQuery('SELECT COUNT(*) FROM sync_queue WHERE status = "pending"');
    final count = (result.first.values.first as int?) ?? 0;
    _queueCountController.add(count);
  }

  Future<void> executePendingSyncQueue() async {
    _statusController.add(SyncStatus.syncing);
    final db = await _dbHelper.database;
    
    final pendingTasks = await db.query(
      'sync_queue',
      where: 'status = ?',
      whereArgs: ['pending'],
      orderBy: 'timestamp_added ASC',
      limit: 10
    );

    if (pendingTasks.isEmpty) {
      final result = await _connectivity.checkConnectivity();
      _updateStatus(result);
      return;
    }

    for (var task in pendingTasks) {
      try {
        final id = task['id'] as int;
        final endpoint = task['api_endpoint'] as String;
        final method = task['method'] as String;
        final payloadStr = task['payload'] as String;
        
        dynamic payloadData = jsonDecode(payloadStr);

        if (method == 'POST_MULTIPART') {
           FormData formData = FormData.fromMap({
             'crop_id': payloadData['crop_id'],
             'district_id': payloadData['district_id'],
             'file': await MultipartFile.fromFile(payloadData['path'], filename: payloadData['path'].split('/').last)
           });
           await _dioClient.dio.post(endpoint, data: formData);
        } else if (method == 'POST') {
           await _dioClient.dio.post(endpoint, data: payloadData);
        }

        await db.update('sync_queue', {'status': 'synced'}, where: 'id = ?', whereArgs: [id]);
        
      } catch (e) {
        print("Sync Queue Fail: $e");
      }
    }
    
    _updateQueueCount();
    final result = await _connectivity.checkConnectivity();
    _updateStatus(result);
  }

  Future<void> fetchAndCacheForecasts(String district, List<String> crops) async {
    final connectivityResult = await _connectivity.checkConnectivity();
    if (connectivityResult == ConnectivityResult.none) return;

    try {
      final cropsQuery = crops.join(',');
      final response = await _dioClient.dio.get('/api/v1/forecasts', queryParameters: {
        'district': district,
        'crops': cropsQuery,
      });

      if (response.statusCode == 200) {
        final db = await _dbHelper.database;
        final data = response.data;
        
        final batch = db.batch();
        for (var forecastGroup in data['forecasts']) {
          batch.insert(
            'forecast_cache',
            {
              'district': district,
              'crop': forecastGroup['crop'],
              'forecast_json': jsonEncode(forecastGroup['forecast']),
              'synced_at': DateTime.now().millisecondsSinceEpoch,
            },
            conflictAlgorithm: ConflictAlgorithm.replace,
          );
        }
        await batch.commit(noResult: true);
      }
    } catch (e) {
      print("Failed to fetch forecasts: \$e");
    }
  }
}
