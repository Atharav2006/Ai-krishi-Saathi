import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class VoiceApiService {
  // Use 127.0.0.1 since the user is using adb reverse tcp:8000 tcp:8000
  static const String _baseUrl = 'http://127.0.0.1:8000/api/v1'; 

  Future<Map<String, dynamic>> submitVoiceQuery(File audioFile, String district, List<String> crops) async {
    var uri = Uri.parse('$_baseUrl/voice/query');
    var request = http.MultipartRequest('POST', uri);
    
    request.fields['district'] = district;
    request.fields['favorite_crops'] = jsonEncode(crops);

    request.files.add(await http.MultipartFile.fromPath(
      'audio_file',
      audioFile.path,
    ));

    var response = await request.send();
    var responseData = await response.stream.bytesToString();

    if (response.statusCode == 200) {
      return jsonDecode(responseData);
    } else {
      throw Exception('Failed to get voice advice: ${response.statusCode}');
    }
  }
}
