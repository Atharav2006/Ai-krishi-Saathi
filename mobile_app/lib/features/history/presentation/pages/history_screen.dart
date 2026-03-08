import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../../core/database/database_helper.dart';
import '../../../../core/localization/app_strings.dart';
import '../../../../core/localization/language_provider.dart';
import '../../../../presentation/widgets/language_selector_button.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  final DatabaseHelper _dbHelper = DatabaseHelper();

  Future<List<Map<String, dynamic>>> _getHistory() async {
    final db = await _dbHelper.database;
    return await db.query('activity_history', orderBy: 'timestamp DESC');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(AppStrings.get('history', languageProvider.langCode)),
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
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: _getHistory(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator(color: Color(0xFF2E7D32)));
          }

          if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.history_outlined, size: 80, color: Colors.grey.shade300),
                  const SizedBox(height: 16),
                  Text(
                    AppStrings.get('no_history', languageProvider.langCode),
                    style: TextStyle(color: Colors.grey.shade600, fontSize: 18),
                  ),
                ],
              ),
            );
          }

          final history = snapshot.data!;

          return ListView.builder(
            padding: const EdgeInsets.all(24.0),
            itemCount: history.length,
            itemBuilder: (context, index) {
              final item = history[index];
              return _buildHistoryCard(item);
            },
          );
        },
      ),
    );
  }

  Widget _buildHistoryCard(Map<String, dynamic> item) {
    final type = item['type'];
    final isDisease = type == 'disease';
    final timestamp = DateTime.fromMillisecondsSinceEpoch(item['timestamp'] as int);
    final status = item['status'];
    final isSynced = status == 'synced';

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
        leading: CircleAvatar(
          backgroundColor: isDisease ? Colors.green.shade50 : Colors.blue.shade50,
          child: Icon(
            isDisease ? Icons.bug_report : Icons.trending_up,
            color: isDisease ? Colors.green : Colors.blue,
          ),
        ),
        title: Text(
          item['title'] ?? 'Activity',
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text(item['subtitle'] ?? ''),
            const SizedBox(height: 4),
            Text(
              DateFormat('MMM dd, yyyy · hh:mm a').format(timestamp),
              style: const TextStyle(fontSize: 12, color: Colors.black38),
            ),
          ],
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: isSynced ? Colors.green.shade50 : Colors.orange.shade50,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            isSynced ? 'Synced' : 'Pending',
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.bold,
              color: isSynced ? Colors.green : Colors.orange,
            ),
          ),
        ),
      ),
    );
  }
}
