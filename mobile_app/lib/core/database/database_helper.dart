import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';

class DatabaseHelper {
  static final DatabaseHelper _instance = DatabaseHelper._internal();
  factory DatabaseHelper() => _instance;
  
  static Database? _database;
  static bool _migrated = false;

  DatabaseHelper._internal();

  Future<Database> get database async {
    if (_database == null) {
      _database = await _initDatabase();
    }
    if (!_migrated) {
      _migrated = true;
      // Ensure forecast_cache exists on ALL installs (even old ones without onUpgrade)
      await _database!.execute('''
        CREATE TABLE IF NOT EXISTS forecast_cache (
          district TEXT NOT NULL,
          crop TEXT NOT NULL,
          forecast_json TEXT NOT NULL,
          synced_at INTEGER NOT NULL,
          PRIMARY KEY (district, crop)
        )
      ''');
    }
    
    // Ensure voice_query_history exists (lazy migration for hackathon demo)
    await _database!.execute('''
      CREATE TABLE IF NOT EXISTS voice_query_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query_text TEXT NOT NULL,
        response_text TEXT NOT NULL,
        language TEXT NOT NULL,
        created_at INTEGER NOT NULL
      )
    ''');
    
    return _database!;
  }

  Future<Database> _initDatabase() async {
    final documentsDirectory = await getApplicationDocumentsDirectory();
    final path = join(documentsDirectory.path, 'krishi_saathi_offline.db');
    
    return await openDatabase(
      path,
      version: 2,
      onCreate: _onCreate,
      onUpgrade: _onUpgrade,
    );
  }

  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    // v1 -> v2: Add forecast_cache table for Hybrid Offline Forecasting
    if (oldVersion < 2) {
      await db.execute('''
        CREATE TABLE IF NOT EXISTS forecast_cache (
          district TEXT NOT NULL,
          crop TEXT NOT NULL,
          forecast_json TEXT NOT NULL,
          synced_at INTEGER NOT NULL,
          PRIMARY KEY (district, crop)
        )
      ''');
    }
  }

  Future<void> _onCreate(Database db, int version) async {
    // Sync Queue (for sending commands back to the server when online)
    await db.execute('''
      CREATE TABLE sync_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        api_endpoint TEXT NOT NULL,
        method TEXT NOT NULL,
        payload TEXT NOT NULL,
        timestamp_added INTEGER NOT NULL,
        status TEXT DEFAULT 'pending'
      )
    ''');

    // Cached Crop Pricing Data
    await db.execute('''
      CREATE TABLE cached_mandi_prices (
        id TEXT PRIMARY KEY,
        crop_id TEXT NOT NULL,
        market_id TEXT NOT NULL,
        price_date TEXT NOT NULL,
        modal_price REAL NOT NULL,
        timestamp_synced INTEGER NOT NULL
      )
    ''');
    
    // Offline predictive records generated independently
    await db.execute('''
      CREATE TABLE offline_disease_logs (
        local_id TEXT PRIMARY KEY,
        image_path TEXT NOT NULL,
        disease_predicted TEXT,
        confidence REAL,
        synced INTEGER DEFAULT 0
      )
    ''');

    // Offline Price Cache for Forecasting (Hybrid Mode)
    await db.execute('''
      CREATE TABLE forecast_cache (
        district TEXT NOT NULL,
        crop TEXT NOT NULL,
        forecast_json TEXT NOT NULL,
        synced_at INTEGER NOT NULL,
        PRIMARY KEY (district, crop)
      )
    ''');
    // Unified activity history for the farmer
    await db.execute('''
      CREATE TABLE activity_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL, -- 'disease' or 'price'
        title TEXT NOT NULL,
        subtitle TEXT,
        timestamp INTEGER NOT NULL,
        status TEXT DEFAULT 'synced' -- 'pending' or 'synced'
      )
    ''');
    
    // Voice query history cache
    await db.execute('''
      CREATE TABLE voice_query_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query_text TEXT NOT NULL,
        response_text TEXT NOT NULL,
        language TEXT NOT NULL,
        created_at INTEGER NOT NULL
      )
    ''');
  }

  Future<void> logActivity({
    required String type,
    required String title,
    String? subtitle,
    String status = 'synced',
  }) async {
    final db = await database;
    await db.insert('activity_history', {
      'type': type,
      'title': title,
      'subtitle': subtitle,
      'timestamp': DateTime.now().millisecondsSinceEpoch,
      'status': status,
    });
  }

  Future<void> wipeDatabase() async {
    final documentsDirectory = await getApplicationDocumentsDirectory();
    final path = join(documentsDirectory.path, 'krishi_saathi_offline.db');
    await deleteDatabase(path);
  }
}
