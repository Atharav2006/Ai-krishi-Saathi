import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class LanguageProvider extends ChangeNotifier {
  static final LanguageProvider _instance = LanguageProvider._internal();
  factory LanguageProvider() => _instance;
  LanguageProvider._internal();

  String _langCode = 'hi'; // Default: Hindi

  String get langCode => _langCode;

  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _langCode = prefs.getString('app_lang') ?? 'hi';
    notifyListeners();
  }

  Future<void> setLanguage(String code) async {
    _langCode = code;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('app_lang', code);
    notifyListeners();
  }

  String translate(String key) {
    // Import AppStrings in the widget, or use the global helper below
    return key;
  }
}

// Global instance for easy access
final languageProvider = LanguageProvider();
