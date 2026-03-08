import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:image_picker/image_picker.dart';
import '../bloc/disease_bloc.dart';
import '../../../../presentation/widgets/confidence_bar.dart';
import '../../../../core/localization/app_strings.dart';
import '../../../../core/localization/language_provider.dart';
import '../../../../presentation/widgets/language_selector_button.dart';

class DiseaseScreen extends StatefulWidget {
  const DiseaseScreen({super.key});

  @override
  State<DiseaseScreen> createState() => _DiseaseScreenState();
}

class _DiseaseScreenState extends State<DiseaseScreen> {
  File? _selectedImage;
  final ImagePicker _picker = ImagePicker();

  Future<void> _pickImage(ImageSource source) async {
    final XFile? pickedFile = await _picker.pickImage(
      source: source,
      maxWidth: 224, // Optimizing for low-end devices: ML model only needs 224x224.
      maxHeight: 224, // Prevents decoding 1 million pixels synchronously on the main thread!
      imageQuality: 80,
    );

    if (pickedFile != null) {
      setState(() {
        _selectedImage = File(pickedFile.path);
      });
      // Automatically trigger analysis
      if (mounted) {
        context.read<DiseaseBloc>().add(
          AnalyzeImage(_selectedImage!, "tomato_default", "mh_pune"),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(AppStrings.get('disease_detection', languageProvider.langCode)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: const Color(0xFF1B5E20),
        actions: const [
          Padding(
            padding: EdgeInsets.only(right: 16.0),
            child: LanguageSelectorButton(),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildImageCard(),
            const SizedBox(height: 24),
            BlocBuilder<DiseaseBloc, DiseaseState>(
              builder: (context, state) {
                if (state is DiseaseLoading) {
                  return const Card(
                    child: Padding(
                      padding: EdgeInsets.all(32.0),
                      child: Column(
                        children: [
                          CircularProgressIndicator(color: Color(0xFF2E7D32)),
                          SizedBox(height: 16),
                          Text('Analyzing leaf health...', style: TextStyle(fontWeight: FontWeight.bold)),
                        ],
                      ),
                    ),
                  );
                }
                
                if (state is DiseaseResultLoaded) {
                  return _buildResultCard(state.result);
                }
                
                if (state is DiseaseError) {
                  return Card(
                    color: Colors.red.shade50,
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Text(state.message, style: const TextStyle(color: Colors.red)),
                    ),
                  );
                }

                return _buildActionButtons();
              },
            ),
            const SizedBox(height: 24),
            _buildInstructions(),
          ],
        ),
      ),
    );
  }

  Widget _buildImageCard() {
    return Container(
      height: 280,
      decoration: BoxDecoration(
        color: Colors.grey.shade100,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.grey.shade300),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(24),
        child: _selectedImage != null
            ? Image.file(_selectedImage!, fit: BoxFit.cover)
            : Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.image_outlined, size: 64, color: Colors.grey.shade400),
                  const SizedBox(height: 12),
                  Text(
                    'No image selected',
                    style: TextStyle(color: Colors.grey.shade600),
                  ),
                ],
              ),
      ),
    );
  }

  Widget _buildActionButtons() {
    return Column(
      children: [
        ElevatedButton.icon(
          onPressed: () => _pickImage(ImageSource.camera),
          icon: const Icon(Icons.camera_alt),
          label: Text(AppStrings.get('take_photo', languageProvider.langCode)),
        ),
        const SizedBox(height: 12),
        OutlinedButton.icon(
          onPressed: () => _pickImage(ImageSource.gallery),
          icon: const Icon(Icons.photo_library),
          label: Text(AppStrings.get('analyze', languageProvider.langCode)),
          style: OutlinedButton.styleFrom(
            minimumSize: const Size(double.infinity, 56),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          ),
        ),
      ],
    );
  }

  Widget _buildResultCard(Map<String, dynamic> result) {
    final isOffline = result['is_offline_result'] == true;
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Analysis Result',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                if (isOffline)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.orange.shade100,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Text(
                      'Offline',
                      style: TextStyle(fontSize: 12, color: Colors.orange, fontWeight: FontWeight.bold),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              result['disease_class'] ?? 'No disease detected',
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1B5E20),
              ),
            ),
            const SizedBox(height: 16),
            ConfidenceBar(confidence: result['confidence'] ?? 0.0),
            const SizedBox(height: 20),
            const Text(
              'Recommended Action:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              result['advisory_text'] ?? 'Ensure the plant gets plenty of sunlight and water.',
              style: const TextStyle(color: Colors.black87),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () {
                setState(() {
                  _selectedImage = null;
                });
                context.read<DiseaseBloc>().add(AnalyzeImage(File(''), '', '')); // Reset state trigger or use new event
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFE8F5E9),
                foregroundColor: const Color(0xFF1B5E20),
              ),
              child: const Text('Try Another Leaf'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInstructions() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFFE3F2FD),
        borderRadius: BorderRadius.circular(20),
      ),
      child: const Column(
        children: [
          Row(
            children: [
              Icon(Icons.info_outline, color: Colors.blue),
              SizedBox(width: 12),
              Text(
                'How to get best results?',
                style: TextStyle(fontWeight: FontWeight.bold, color: Colors.blue),
              ),
            ],
          ),
          SizedBox(height: 12),
          Text(
            '1. Ensure the leaf is well-lit.\n2. Keep the camera steady.\n3. Make sure only one leaf is in focus.',
            style: TextStyle(height: 1.5, color: Colors.black54),
          ),
        ],
      ),
    );
  }
}
