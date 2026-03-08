import 'dart:io';
import 'package:dio/dio.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/database/database_helper.dart';
import '../../../../core/services/tflite_service.dart';
import 'package:uuid/uuid.dart';

abstract class DiseaseDetectionRepository {
  Future<Map<String, dynamic>> detectDisease(File imageFile, String cropId, String districtId);
}

class DiseaseDetectionRepositoryImpl implements DiseaseDetectionRepository {
  final DioClient _dioClient;
  final DatabaseHelper _dbHelper;
  final TfliteService _tfliteService;
  final Uuid _uuid = const Uuid();

  DiseaseDetectionRepositoryImpl(this._dioClient, this._dbHelper, this._tfliteService);

  @override
  Future<Map<String, dynamic>> detectDisease(File imageFile, String cropId, String districtId) async {
    // 🚀 Phase 1: Lightning Fast Local TFLite inference (Offline-First)
    final localResult = await _tfliteService.runInference(imageFile);
    
    final label = localResult['label'];
    final confidenceString = localResult['confidence'].toString().replaceAll('%', '');
    final confidence = double.tryParse(confidenceString) ?? 0.0;
    
    // Fire and forget cloud sync so UI doesn't block
    _syncToCloudInBackground(imageFile, cropId, districtId, label, confidence);
    
    // Return standard format expected by the frontend
    return {
      'disease_class': label,
      'confidence': (confidence / 100.0), // Standardize to 0.0 - 1.0 format
      'is_local_inference': true,
      'source': 'TFLite On-Device Model'
    };
  }

  Future<void> _syncToCloudInBackground(File imageFile, String cropId, String districtId, String label, double confidence) async {
    try {
      String fileName = imageFile.path.split('/').last;
      
      FormData formData = FormData.fromMap({
        'crop_id': cropId,
        'district_id': districtId,
        'predicted_label': label,
        'confidence': confidence,
        'file': await MultipartFile.fromFile(imageFile.path, filename: fileName),
      });

      // Attempt to sync prediction to cloud if online
      final response = await _dioClient.dio.post(
        '/ml/detect-disease', // Assume backend handles this correctly or just logs it
        data: formData,
      );
      
      await _dbHelper.logActivity(
        type: 'disease',
        title: 'Detected: $label',
        subtitle: 'Confidence: \${confidence.toStringAsFixed(1)}%',
        status: 'synced',
      );
    } catch (e) {
      print("Background Cloud Sync Failed (Expected if offline): \$e");
      // Log offline activity locally
      await _dbHelper.logActivity(
        type: 'disease',
        title: 'Detected: $label',
        subtitle: 'Confidence: \${confidence.toStringAsFixed(1)}%',
        status: 'pending_sync',
      );
    }
  }
}
