import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../bloc/auth_bloc.dart';
import 'register_screen.dart';
import '../../../../core/localization/app_strings.dart';
import '../../../../core/localization/language_provider.dart';
import '../../../../presentation/widgets/language_selector_button.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _phoneController = TextEditingController();
  final _pinController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: BlocConsumer<AuthBloc, AuthState>(
          listener: (context, state) {
            if (state is AuthError) {
              ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(state.message)));
            }
          },
          builder: (context, state) {
            return SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 40.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Align(
                    alignment: Alignment.centerRight,
                    child: LanguageSelectorButton(),
                  ),
                  const SizedBox(height: 20),
                  const Icon(Icons.agriculture_rounded, size: 80, color: Color(0xFF2E7D32)),
                  const SizedBox(height: 24),
                  Text(
                    AppStrings.get('app_name', languageProvider.langCode),
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Color(0xFF1B5E20)),
                  ),
                  const SizedBox(height: 48),
                  TextField(
                    controller: _phoneController,
                    keyboardType: TextInputType.phone,
                    maxLength: 10,
                    decoration: InputDecoration(
                      labelText: AppStrings.get('phone_number', languageProvider.langCode),
                      prefixIcon: Icon(Icons.phone),
                      counterText: '',
                    ),
                  ),
                  const SizedBox(height: 20),
                  TextField(
                    controller: _pinController,
                    keyboardType: TextInputType.number,
                    obscureText: true,
                    maxLength: 4,
                    decoration: InputDecoration(
                      labelText: AppStrings.get('enter_pin', languageProvider.langCode),
                      prefixIcon: Icon(Icons.dialpad),
                      counterText: '',
                    ),
                  ),
                  const SizedBox(height: 40),
                  if (state is AuthLoading)
                    const Center(child: CircularProgressIndicator(color: Color(0xFF2E7D32)))
                  else
                    ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        backgroundColor: const Color(0xFF2E7D32),
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      onPressed: () {
                        if (_phoneController.text.length == 10 && _pinController.text.length == 4) {
                          context.read<AuthBloc>().add(
                            LoginRequested(_phoneController.text, _pinController.text),
                          );
                        } else {
                          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter a valid 10-digit phone number and 4-digit PIN.')));
                        }
                      },
                      child: Text(AppStrings.get('login', languageProvider.langCode), style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                    ),
                  const SizedBox(height: 24),
                  TextButton(
                    onPressed: () {
                      Navigator.push(context, MaterialPageRoute(builder: (_) => const RegisterScreen()));
                    },
                    child: Text(
                      AppStrings.get('register', languageProvider.langCode),
                      style: TextStyle(color: Color(0xFF1B5E20), fontSize: 16, fontWeight: FontWeight.w600),
                    ),
                  )
                ],
              ),
            );
          },
        ),
      ),
    );
  }
}
