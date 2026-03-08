import 'package:flutter/material.dart';
import '../../../../presentation/widgets/sync_status_widget.dart';
import '../../../disease_detection/presentation/pages/disease_screen.dart';
import '../../../crop_prices/presentation/pages/price_screen.dart';
import '../../../history/presentation/pages/history_screen.dart';
import '../../../voice_advisor/voice_advisor_screen.dart';
import '../../../../core/localization/app_strings.dart';
import '../../../../core/localization/language_provider.dart';
import '../../../../presentation/widgets/language_selector_button.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          AppStrings.get('app_name', languageProvider.langCode),
          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 24),
        ),
        elevation: 0,
        backgroundColor: Colors.transparent,
        foregroundColor: const Color(0xFF1B5E20),
        actions: const [
          Padding(
            padding: EdgeInsets.only(right: 8.0),
            child: LanguageSelectorButton(),
          ),
          Padding(
            padding: EdgeInsets.only(right: 16.0),
            child: SyncStatusWidget(),
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 20),
              Text(
                AppStrings.get('welcome', languageProvider.langCode),
                style: Theme.of(context).textTheme.headlineMedium,
              ),
              const SizedBox(height: 40),
              
              _buildFeatureCard(
                context,
                title: AppStrings.get('check_crop_disease', languageProvider.langCode),
                subtitle: '', // Let the dynamic translation speak for itself
                icon: '🌿',
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const DiseaseScreen()),
                ),
              ),
              
              const SizedBox(height: 20),
              
              _buildFeatureCard(
                context,
                title: AppStrings.get('mandi_rate_forecast', languageProvider.langCode),
                subtitle: '',
                icon: '📈',
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const PriceScreen()),
                ),
              ),
              
              const SizedBox(height: 20),
              
              _buildFeatureCard(
                context,
                title: 'Voice Advisor', // Hardcoded fallback until localized 
                subtitle: '',
                icon: '🎙️',
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => VoiceAdvisorScreen()),
                ),
              ),
              
              const Spacer(),
              
              Center(
                child: TextButton.icon(
                  onPressed: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const HistoryScreen()),
                  ),
                  icon: const Icon(Icons.history, color: Color(0xFF2E7D32)),
                  label: Text(
                    AppStrings.get('history', languageProvider.langCode),
                    style: const TextStyle(
                      color: Color(0xFF2E7D32),
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFeatureCard(
    BuildContext context, {
    required String title,
    required String subtitle,
    required String icon,
    required VoidCallback onTap,
  }) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(24),
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Row(
            children: [
              Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  color: const Color(0xFFE8F5E9),
                  borderRadius: BorderRadius.circular(16),
                ),
                alignment: Alignment.center,
                child: Text(
                  icon,
                  style: const TextStyle(fontSize: 32),
                ),
              ),
              const SizedBox(width: 20),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1B5E20),
                      ),
                    ),
                    if (subtitle.isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Text(
                        subtitle,
                        style: const TextStyle(
                          fontSize: 14,
                          color: Colors.black54,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              const Icon(Icons.chevron_right, color: Colors.green),
            ],
          ),
        ),
      ),
    );
  }
}
