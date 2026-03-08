import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:get_it/get_it.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'core/network/dio_client.dart';
import 'core/database/database_helper.dart';
import 'core/utils/sync_manager.dart';
import 'core/theme/app_theme.dart';
import 'core/services/tflite_service.dart';
import 'core/localization/language_provider.dart';

import 'features/auth/data/repositories/auth_repository_impl.dart';
import 'features/auth/presentation/bloc/auth_bloc.dart';
import 'features/auth/presentation/pages/login_screen.dart';

import 'features/crop_prices/data/repositories/crop_prices_repository_impl.dart';
import 'features/crop_prices/presentation/bloc/crop_bloc.dart';

import 'features/disease_detection/data/repositories/disease_detection_repository_impl.dart';
import 'features/disease_detection/presentation/bloc/disease_bloc.dart';

import 'features/home/presentation/pages/home_screen.dart';

final sl = GetIt.instance;

Future<void> initDependencies() async {
  // Core
  sl.registerLazySingleton(() => DioClient());
  sl.registerLazySingleton(() => DatabaseHelper());
  sl.registerLazySingleton(() => const FlutterSecureStorage());
  
  final tfliteService = TfliteService();
  // Fire and forget: Load model asynchronously so it doesn't block the Splash Screen on low-end devices
  tfliteService.loadModel();
  sl.registerLazySingleton(() => tfliteService);

  // Repositories
  sl.registerLazySingleton<AuthRepository>(
    () => AuthRepositoryImpl(sl(), sl()),
  );
  sl.registerLazySingleton<CropPricesRepository>(
    () => CropPricesRepositoryImpl(sl(), sl()),
  );
  sl.registerLazySingleton<DiseaseDetectionRepository>(
    () => DiseaseDetectionRepositoryImpl(sl(), sl(), sl()),
  );

  // Blocs
  sl.registerFactory(() => AuthBloc(sl()));
  sl.registerFactory(() => CropBloc(sl()));
  sl.registerFactory(() => DiseaseBloc(sl()));
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await initDependencies();
  
  // Background Workers - Fire and forget
  SyncManager().initializeSyncListener();
  
  // Load saved language preference
  await languageProvider.init();

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider(create: (_) => sl<AuthBloc>()..add(AppStarted())),
        BlocProvider(create: (_) => sl<CropBloc>()),
        BlocProvider(create: (_) => sl<DiseaseBloc>()),
      ],
      child: ListenableBuilder(
        listenable: languageProvider,
        builder: (context, _) {
          return MaterialApp(
            title: 'AI Krishi Saathi',
            theme: AppTheme.lightTheme,
            debugShowCheckedModeBanner: false,
            home: BlocBuilder<AuthBloc, AuthState>(
              builder: (context, state) {
                if (state is AuthAuthenticated) {
                  return const HomeScreen(); // Replaces with Dashboard layout
                }
                if (state is AuthUnauthenticated || state is AuthError) {
                  return const LoginScreen();
                }
                return const Scaffold(
                  body: Center(child: CircularProgressIndicator(color: Color(0xFF2E7D32))),
                );
              },
            ),
          );
        },
      ),
    );
  }
}
