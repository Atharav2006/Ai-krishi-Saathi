import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../data/repositories/auth_repository_impl.dart';

// --- Events ---
abstract class AuthEvent extends Equatable {
  const AuthEvent();
  @override
  List<Object> get props => [];
}

class AppStarted extends AuthEvent {}
class LoginRequested extends AuthEvent {
  final String phone;
  final String password;
  const LoginRequested(this.phone, this.password);
  @override
  List<Object> get props => [phone, password];
}

class RegisterRequested extends AuthEvent {
  final String phone;
  final String password;
  const RegisterRequested(this.phone, this.password);
  @override
  List<Object> get props => [phone, password];
}

class LogoutRequested extends AuthEvent {}

// --- States ---
abstract class AuthState extends Equatable {
  const AuthState();
  @override
  List<Object> get props => [];
}

class AuthInitial extends AuthState {}
class AuthLoading extends AuthState {}
class AuthAuthenticated extends AuthState {}
class AuthUnauthenticated extends AuthState {}
class AuthError extends AuthState {
  final String message;
  const AuthError(this.message);
  @override
  List<Object> get props => [message];
}

// --- Bloc ---
class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final AuthRepository _authRepository;

  AuthBloc(this._authRepository) : super(AuthInitial()) {
    on<AppStarted>(_onAppStarted);
    on<LoginRequested>(_onLoginRequested);
    on<RegisterRequested>(_onRegisterRequested);
    on<LogoutRequested>(_onLogoutRequested);
  }

  Future<void> _onAppStarted(AppStarted event, Emitter<AuthState> emit) async {
    final isAuthenticated = await _authRepository.checkAuthStatus();
    if (isAuthenticated) {
      emit(AuthAuthenticated());
    } else {
      emit(AuthUnauthenticated());
    }
  }

  Future<void> _onLoginRequested(LoginRequested event, Emitter<AuthState> emit) async {
    emit(AuthLoading());
    try {
      final success = await _authRepository.login(event.phone, event.password);
      if (success) {
        emit(AuthAuthenticated());
      } else {
        emit(const AuthError('Login failed.'));
        emit(AuthUnauthenticated());
      }
    } catch (e) {
      final errorMsg = e.toString().replaceAll('Exception: ', '');
      emit(AuthError(errorMsg));
      emit(AuthUnauthenticated());
    }
  }

  Future<void> _onRegisterRequested(RegisterRequested event, Emitter<AuthState> emit) async {
    emit(AuthLoading());
    try {
      final success = await _authRepository.register(event.phone, event.password);
      if (success) {
        emit(AuthAuthenticated());
      } else {
        emit(const AuthError('Registration failed.'));
        emit(AuthUnauthenticated());
      }
    } catch (e) {
      final errorMsg = e.toString().replaceAll('Exception: ', '');
      emit(AuthError(errorMsg));
      emit(AuthUnauthenticated());
    }
  }

  Future<void> _onLogoutRequested(LogoutRequested event, Emitter<AuthState> emit) async {
    await _authRepository.logout();
    emit(AuthUnauthenticated());
  }
}
