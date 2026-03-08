import 'package:flutter/material.dart';
import '../../core/localization/app_strings.dart';
import '../../core/localization/language_provider.dart';

class LanguageSelectorButton extends StatelessWidget {
  const LanguageSelectorButton({super.key});

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: languageProvider,
      builder: (context, _) {
        final currentLang = AppStrings.languages.firstWhere(
          (l) => l['code'] == languageProvider.langCode,
          orElse: () => AppStrings.languages[1], // Default Hindi
        );
        
        return PopupMenuButton<String>(
          onSelected: (code) {
            languageProvider.setLanguage(code);
          },
          tooltip: 'Select Language',
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          padding: EdgeInsets.zero,
          icon: Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            decoration: BoxDecoration(
              color: const Color(0xFF2E7D32).withOpacity(0.1),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: const Color(0xFF2E7D32).withOpacity(0.3)),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.language, size: 16, color: Color(0xFF2E7D32)),
                const SizedBox(width: 4),
                Text(
                  currentLang['native']!.substring(0, 2).toUpperCase(),
                  style: const TextStyle(
                    fontSize: 12, 
                    fontWeight: FontWeight.bold, 
                    color: Color(0xFF2E7D32),
                  ),
                ),
                const Icon(Icons.arrow_drop_down, size: 16, color: Color(0xFF2E7D32)),
              ],
            ),
          ),
          itemBuilder: (BuildContext context) {
            return AppStrings.languages.map((lang) {
              final isSelected = lang['code'] == languageProvider.langCode;
              return PopupMenuItem<String>(
                value: lang['code'],
                child: Row(
                  children: [
                    Text(
                      lang['native']!, 
                      style: TextStyle(
                        fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
                        color: isSelected ? const Color(0xFF2E7D32) : Colors.black87,
                      ),
                    ),
                    const Spacer(),
                    Text(
                      lang['name']!, 
                      style: TextStyle(fontSize: 12, color: Colors.grey.shade500),
                    ),
                  ],
                ),
              );
            }).toList();
          },
        );
      },
    );
  }
}
