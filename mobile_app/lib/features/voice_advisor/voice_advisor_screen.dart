import 'package:flutter/material.dart';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:just_audio/just_audio.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';
import 'voice_api_service.dart';
import 'package:ai_krishi_saathi/core/database/database_helper.dart';

class VoiceAdvisorScreen extends StatefulWidget {
  @override
  _VoiceAdvisorScreenState createState() => _VoiceAdvisorScreenState();
}

class _VoiceAdvisorScreenState extends State<VoiceAdvisorScreen> {
  final FlutterSoundRecorder _recorder = FlutterSoundRecorder();
  final AudioPlayer _player = AudioPlayer();
  final VoiceApiService _apiService = VoiceApiService();
  
  bool _isRecording = false;
  bool _isLoading = false;
  String _transcription = '';
  String _responseMessage = '';
  
  @override
  void initState() {
    super.initState();
    _initRecorder();
  }
  
  Future<void> _initRecorder() async {
    await Permission.microphone.request();
    await _recorder.openRecorder();
  }

  @override
  void dispose() {
    _recorder.closeRecorder();
    _player.dispose();
    super.dispose();
  }

  Future<void> _startRecording() async {
    if (await Permission.microphone.isGranted) {
      Directory tempDir = await getTemporaryDirectory();
      String path = '${tempDir.path}/query.wav';
      await _recorder.startRecorder(toFile: path, codec: Codec.pcm16WAV);
      setState(() {
        _isRecording = true;
        _transcription = '';
        _responseMessage = '';
      });
    } else {
       ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Microphone permission required'))
      );
    }
  }

  Future<void> _stopRecording() async {
    String? path = await _recorder.stopRecorder();
    setState(() {
      _isRecording = false;
    });

    if (path != null) {
      _processAudio(File(path));
    }
  }

  Future<void> _processAudio(File audioFile) async {
    setState(() {
      _isLoading = true;
      _responseMessage = 'Processing...';
    });

    try {
      // Hardcoded district/crops for demo
      final response = await _apiService.submitVoiceQuery(audioFile, 'Nashik', ['onion', 'tomato']);
      
      setState(() {
        _transcription = response['transcribed_text'] ?? '';
        _responseMessage = response['text'] ?? '';
      });
      
      // Save history to SQLite Cache
      final db = await DatabaseHelper().database;
      await db.insert('voice_query_history', {
        'query_text': _transcription,
        'response_text': _responseMessage,
        'language': response['language'] ?? 'gu',
        'created_at': DateTime.now().millisecondsSinceEpoch
      });
      
      // Play Audio automatically
      String audioUrl = response['audio_url'];
      String fullUrl = 'http://127.0.0.1:8000$audioUrl';
      
      await _player.setUrl(fullUrl);
      _player.play();
      
    } catch (e) {
      setState(() {
        _responseMessage = 'Voice assistant requires internet connection.';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Voice Advisor'),
        backgroundColor: Colors.green.shade800,
        foregroundColor: Colors.white,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Spacer(),
              if (_transcription.isNotEmpty) 
                Text(
                  'You: "$_transcription"', 
                  style: TextStyle(fontStyle: FontStyle.italic, fontSize: 18, color: Colors.grey.shade700)
                ),
              SizedBox(height: 24),
              if (_responseMessage.isNotEmpty)
                Container(
                  padding: EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: _responseMessage.contains('internet connection') 
                        ? Colors.red.shade50 
                        : Colors.green.shade50,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: _responseMessage.contains('internet connection') 
                          ? Colors.red.shade200 
                          : Colors.green.shade200
                    )
                  ),
                  child: Text(
                    _responseMessage, 
                    style: TextStyle(
                      fontSize: 20, 
                      fontWeight: FontWeight.w500,
                      color: _responseMessage.contains('internet connection') 
                          ? Colors.red.shade900 
                          : Colors.green.shade900
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
              Spacer(),
              if (_isLoading) 
                Column(
                  children: [
                    CircularProgressIndicator(color: Colors.green.shade600),
                    SizedBox(height: 16),
                    Text('AI Krishi is thinking...', style: TextStyle(color: Colors.grey.shade600))
                  ],
                ),
              if (!_isLoading) ...[
                GestureDetector(
                  onLongPressStart: (_) => _startRecording(),
                  onLongPressEnd: (_) => _stopRecording(),
                  child: AnimatedContainer(
                    duration: Duration(milliseconds: 200),
                    height: _isRecording ? 100 : 80,
                    width: _isRecording ? 100 : 80,
                    decoration: BoxDecoration(
                      color: _isRecording ? Colors.red : Colors.green.shade600,
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: _isRecording ? Colors.red.withOpacity(0.5) : Colors.green.withOpacity(0.3),
                          spreadRadius: _isRecording ? 10 : 2,
                          blurRadius: 10,
                        )
                      ]
                    ),
                    child: Icon(
                      _isRecording ? Icons.mic : Icons.mic_none,
                      color: Colors.white,
                      size: _isRecording ? 50 : 40,
                    ),
                  ),
                ),
                SizedBox(height: 20),
                Text(
                  _isRecording ? 'Release to Send' : 'Hold to Speak', 
                  style: TextStyle(
                    fontWeight: FontWeight.bold, 
                    fontSize: 16,
                    color: _isRecording ? Colors.red : Colors.green.shade800
                  )
                ),
                SizedBox(height: 40),
              ]
            ],
          ),
        ),
      ),
    );
  }
}
