import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/services.dart';
import 'package:image/image.dart' as img;
import 'package:tflite_flutter/tflite_flutter.dart';

class TfliteService {
  Interpreter? _interpreter;
  List<String> _labels = [];
  bool _isModelLoaded = false;

  // Getter for model loaded status
  bool get isLoaded => _isModelLoaded;

  // Getter for the number of labels
  int get labelCount => _labels.length;

  Future<void> loadModel() async {
    if (_isModelLoaded) return;
    try {
      _interpreter = await Interpreter.fromAsset('assets/models/disease_model_v2.tflite');
      
      final labelData = await rootBundle.loadString('assets/models/labels.txt');
      _labels = labelData.split('\n').where((s) => s.trim().isNotEmpty).toList();
      
      _isModelLoaded = true;
      print("✅ TFLite Model Loaded Successfully. Classes: ${_labels.length}");
    } catch (e) {
      print("❌ TFLite Model Load Fail: $e");
      _isModelLoaded = false;
    }
  }

  Future<Map<String, dynamic>> runInference(File image) async {
    if (!_isModelLoaded) {
      await loadModel();
    }
    
    if (!_isModelLoaded || _interpreter == null) {
      return {
        'label': 'Unknown (Model could not be loaded)',
        'confidence': '0.0%',
        'raw_score': 0.0,
        'crop_info': {},
        'is_healthy': false,
      };
    }

    // Read image bytes
    final imageBytes = await image.readAsBytes();
    img.Image? decodedImage = img.decodeImage(imageBytes);

    if (decodedImage == null) {
      return {
        'label': 'Error decoding image',
        'confidence': '0.0%',
        'raw_score': 0.0,
        'crop_info': {},
        'is_healthy': false,
      };
    }

    // Resize image to 224x224 (MobileNetV2 requirement)
    img.Image resizedImage = img.copyResize(decodedImage, width: 224, height: 224);

    // Convert to Float32 format [1, 224, 224, 3] and normalize to [0, 1]
    var input = List.generate(
      1,
      (i) => List.generate(
        224,
        (j) => List.generate(
          224,
          (k) => List.filled(3, 0.0),
        ),
      ),
    );

    for (int y = 0; y < resizedImage.height; y++) {
      for (int x = 0; x < resizedImage.width; x++) {
        img.Pixel pixel = resizedImage.getPixel(x, y);
        input[0][y][x][0] = pixel.r / 255.0; // Red
        input[0][y][x][1] = pixel.g / 255.0; // Green
        input[0][y][x][2] = pixel.b / 255.0; // Blue
      }
    }

    // Output array [1, num_classes]
    var output = List.generate(1, (i) => List.filled(_labels.length, 0.0));

    // Run inference
    final stopwatch = Stopwatch()..start();
    _interpreter!.run(input, output);
    stopwatch.stop();
    print("Inference took ${stopwatch.elapsedMilliseconds}ms");

    // Parse output
    List<double> scores = (output[0] as List).cast<double>();
    double maxScore = -1;
    int maxIndex = -1;
    for (int i = 0; i < scores.length; i++) {
        if (scores[i] > maxScore) {
            maxScore = scores[i];
            maxIndex = i;
        }
    }

    String label = maxIndex != -1 ? _labels[maxIndex] : "Unknown";
    final confidence = maxScore;

    // Clean label: replace underscores, collapse multiple spaces, trim whitespace
    final cleanedLabel = label.replaceAll('_', ' ').replaceAll(RegExp(r'\s+'), ' ').trim();
    
    // Determine if the label indicates 'healthy'
    final isHealthy = cleanedLabel.toLowerCase().contains('healthy');

    return {
      'label': cleanedLabel,
      'confidence': (confidence * 100).toStringAsFixed(1) + '%',
      'raw_score': confidence,
      'crop_info': {}, // Placeholder for crop information if applicable
      'is_healthy': isHealthy,
    };
  }
}
