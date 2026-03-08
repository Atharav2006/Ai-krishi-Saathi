import 'package:flutter/material.dart';
import '../../core/utils/sync_manager.dart';

class SyncStatusWidget extends StatelessWidget {
  const SyncStatusWidget({super.key});

  @override
  Widget build(BuildContext context) {
    final syncManager = SyncManager();

    return StreamBuilder<SyncStatus>(
      stream: syncManager.statusStream,
      initialData: SyncStatus.online,
      builder: (context, statusSnapshot) {
        final status = statusSnapshot.data ?? SyncStatus.online;
        
        return StreamBuilder<int>(
          stream: syncManager.queueCountStream,
          initialData: 0,
          builder: (context, countSnapshot) {
            final count = countSnapshot.data ?? 0;
            
            return Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (count > 0)
                  Padding(
                    padding: const EdgeInsets.only(right: 8.0),
                    child: Container(
                      padding: const EdgeInsets.all(6),
                      decoration: BoxDecoration(
                        color: Colors.orange.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        '$count pending',
                        style: const TextStyle(
                          color: Colors.orange,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                _buildIndicator(status),
              ],
            );
          },
        );
      },
    );
  }

  Widget _buildIndicator(SyncStatus status) {
    Color color;
    String label;
    bool isSyncing = false;

    switch (status) {
      case SyncStatus.online:
        color = Colors.green;
        label = "Online";
        break;
      case SyncStatus.offline:
        color = Colors.orange;
        label = "Offline";
        break;
      case SyncStatus.syncing:
        color = Colors.blue;
        label = "Syncing";
        isSyncing = true;
        break;
    }

    return Tooltip(
      message: label,
      child: Container(
        width: 12,
        height: 12,
        decoration: BoxDecoration(
          color: color,
          shape: BoxShape.circle,
          boxShadow: [
            BoxShadow(
              color: color.withOpacity(0.5),
              blurRadius: 4,
              spreadRadius: 1,
            )
          ],
        ),
        child: isSyncing 
          ? const CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
            )
          : null,
      ),
    );
  }
}
