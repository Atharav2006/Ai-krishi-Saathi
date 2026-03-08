import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../bloc/auth_bloc.dart';
import '../../../../core/localization/app_strings.dart';
import '../../../../core/localization/language_provider.dart';
import '../../../../presentation/widgets/language_selector_button.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});
  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _phoneController = TextEditingController();
  final _pinController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(AppStrings.get('register', languageProvider.langCode)),
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
      body: SafeArea(
        child: BlocConsumer<AuthBloc, AuthState>(
          listener: (context, state) {
            if (state is AuthError) {
              ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(state.message)));
            } else if (state is AuthAuthenticated) {
              // Registration auto-logs in, so pop back to let the app router handle the state change
              Navigator.pop(context);
            }
          },
          builder: (context, state) {
            return SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                   Text(
                    AppStrings.get('app_name', languageProvider.langCode),
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Color(0xFF1B5E20)),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Join the farming revolution today',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 16, color: Colors.grey),
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
                            RegisterRequested(_phoneController.text, _pinController.text),
                          );
                        } else {
                          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter a valid 10-digit phone number and a 4-digit PIN.')));
                        }
                      },
                      child: Text(AppStrings.get('register', languageProvider.langCode), style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                    ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }
}
