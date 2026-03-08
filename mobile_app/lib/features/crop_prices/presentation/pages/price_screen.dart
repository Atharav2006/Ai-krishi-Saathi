import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../bloc/crop_bloc.dart';
import '../../../../core/localization/app_strings.dart';
import '../../../../core/localization/language_provider.dart';
import '../../../../presentation/widgets/language_selector_button.dart';

class PriceScreen extends StatefulWidget {
  const PriceScreen({super.key});

  @override
  State<PriceScreen> createState() => _PriceScreenState();
}

class _PriceScreenState extends State<PriceScreen> {
  String? _selectedState;
  String? _selectedDistrict;
  String? _selectedMarket;
  String? _selectedCropId;

  final List<Map<String, String>> _crops = [
    {'id': 'rice', 'name': 'Rice (Basmati)'},
    {'id': 'wheat', 'name': 'Wheat (Sharbati)'},
    {'id': 'cotton', 'name': 'Cotton (BT)'},
    {'id': 'sugarcane', 'name': 'Sugarcane'},
    {'id': 'maize', 'name': 'Maize (Hybrid)'},
    {'id': 'soybean', 'name': 'Soybean (Yellow)'},
    {'id': 'potato', 'name': 'Potato (Jyoti)'},
    {'id': 'onion', 'name': 'Onion (Red)'},
    {'id': 'tomato', 'name': 'Tomato (Hybrid)'},
    {'id': 'apple', 'name': 'Apple (Kashmir)'},
  ];

  final Map<String, Map<String, List<String>>> _locationData = {
    'Punjab': {
      'Amritsar': ['Majitha Mandi', 'Ajnala Market'],
      'Ludhiana': ['Gill Road Mandi', 'Samrala Market'],
      'Jalandhar': ['Maqsudan Mandi', 'Phillaur APMC'],
      'Patiala': ['Sanaur Mandi', 'Rajpura Market'],
      'Bathinda': ['Rampura Phul', 'Bhucho Mandi'],
    },
    'Uttar Pradesh': {
      'Agra': ['Fatehabad Mandi', 'Kiraoli Market'],
      'Lucknow': ['Dubagga Mandi', 'Naveen Galla Mandi'],
      'Kanpur': ['Chakeri Mandi', 'Bidhnu Market'],
      'Varanasi': ['Chandua Mandi', 'Pahariya APMC'],
      'Meerut': ['Naveen Mandi', 'Mawana Market'],
    },
    'Tamil Nadu': {
      'Coimbatore': ['Mettupalayam', 'Pollachi Market'],
      'Madurai': ['Paravai Market', 'Mattuthavani'],
      'Chennai': ['Koyambedu', 'Tambaram Market'],
      'Salem': ['Leigh Bazaar', 'Omalur Mandi'],
      'Tiruchirappalli': ['Gandhi Market', 'Manapparai'],
    },
    'Karnataka': {
      'Bengaluru': ['Yeshwanthpur APMC', 'KR Market'],
      'Mysuru': ['APMC Bandipalya', 'Nanjangud Mandi'],
      'Hubballi': ['Amargol APMC', 'Navanagar Market'],
      'Belagavi': ['Bailhongal Mandi', 'Gokak APMC'],
      'Mangaluru': ['Central Market', 'Bunder APMC'],
    },
    'West Bengal': {
      'Burdwan': ['Memari Mandi', 'Kalna Market'],
      'Hooghly': ['Arambagh APMC', 'Tarakeswar Market'],
      'Howrah': ['Uluberia Mandi', 'Amta Market'],
      'Darjeeling': ['Siliguri Regulated', 'Kurseong Market'],
      'Nadia': ['Krishnanagar', 'Kalyani Market'],
    },
    'Odisha': {
      'Cuttack': ['Chhatra Bazar', 'Niali Mandi'],
      'Khordha': ['Unit-1 Market', 'Jatni Mandi'],
      'Ganjam': ['Brahmapur Regulated', 'Aska APMC'],
      'Puri': ['Sakhigopal Mandi', 'Nimapada Market'],
      'Balasore': ['Soro Mandi', 'Jaleswar Market'],
    },
    'Maharashtra': {
      'Pune': ['Marketyard APMC', 'Khed Shivapur'],
      'Nashik': ['Pimpalgaon Baswant', 'Lasalgaon Mandi'],
      'Nagpur': ['Kalamna Market', 'Katol Mandi'],
      'Kolhapur': ['Shahupuri APMC', 'Gadhinglaj Market'],
      'Ahmednagar': ['Sangamner APMC', 'Rahuri Mandi'],
    },
    'Gujarat': {
      'Ahmedabad': ['Jamalpur APMC', 'Bavla Market'],
      'Rajkot': ['Gondal APMC', 'Bedi Mandi'],
      'Surat': ['Sardar Market', 'Bardoli APMC'],
      'Vadodara': ['Sayajipura APMC', 'Padra Market'],
      'Bhavnagar': ['Talaja Mandi', 'Mahuva Mandi'],
    },
    'Madhya Pradesh': {
      'Indore': ['Choithram Mandi', 'Laxmibainagar'],
      'Ujjain': ['Badnagar Mandi', 'Khachrod APMC'],
      'Bhopal': ['Karond Mandi', 'Berasia Market'],
      'Gwalior': ['Lashkar Mandi', 'Dabra APMC'],
      'Jabalpur': ['Krimikund Mandi', 'Patan Market'],
    },
    'Chhattisgarh': {
      'Raipur': ['Pandri Mandi', 'Bhatapara APMC'],
      'Bilaspur': ['Tifra Mandi', 'Kota Market'],
      'Durg': ['Bhilai APMC', 'Patan Mandi'],
      'Bastar': ['Jagdalpur APMC', 'Lohandiguda'],
      'Rajnandgaon': ['Kawardha Mandi', 'Dongargarh APMC'],
    },
  };

  void _fetchPrice() {
    if (_selectedCropId != null && _selectedDistrict != null) {
      context.read<CropBloc>().add(FetchPricePrediction(_selectedCropId!, _selectedDistrict!));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F8F5),
      appBar: AppBar(
        title: Text(AppStrings.get('mandi_rate_forecast', languageProvider.langCode), style: const TextStyle(fontWeight: FontWeight.bold)),
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
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildLocationSelectors(),
            const SizedBox(height: 16),
            _buildCropSelector(),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: (_selectedState != null && _selectedDistrict != null &&
                          _selectedMarket != null && _selectedCropId != null)
                  ? _fetchPrice
                  : null,
              icon: const Icon(Icons.search),
              label: Text(AppStrings.get('check_price', languageProvider.langCode), style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF2E7D32),
                foregroundColor: Colors.white,
                disabledBackgroundColor: Colors.grey.shade300,
                padding: const EdgeInsets.symmetric(vertical: 15),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              ),
            ),
            const SizedBox(height: 32),
            BlocBuilder<CropBloc, CropState>(
              builder: (context, state) {
                if (state is CropLoading) {
                  return const Center(
                    child: Padding(
                      padding: EdgeInsets.all(40.0),
                      child: Column(
                        children: [
                          CircularProgressIndicator(color: Color(0xFF2E7D32)),
                          SizedBox(height: 12),
                          Text('बाजार भाव खोज रहे हैं...', style: TextStyle(color: Colors.black54)),
                        ],
                      ),
                    ),
                  );
                }
                if (state is CropPriceLoaded) {
                  return _buildForecastView(state.data);
                }
                if (state is CropError) {
                  return Center(
                    child: Padding(
                      padding: const EdgeInsets.all(24.0),
                      child: Text(state.message, textAlign: TextAlign.center, style: const TextStyle(color: Colors.redAccent)),
                    ),
                  );
                }
                return Center(
                  child: Padding(
                    padding: const EdgeInsets.only(top: 40.0),
                    child: Text(
                      '${AppStrings.get('select_state', languageProvider.langCode)}, ${AppStrings.get('select_district', languageProvider.langCode)}, ${AppStrings.get('select_crop_hint', languageProvider.langCode)}\n${AppStrings.get('check_price', languageProvider.langCode)}',
                      textAlign: TextAlign.center,
                      style: const TextStyle(color: Colors.black45, fontSize: 15, height: 1.6),
                    ),
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLocationSelectors() {
    final states = _locationData.keys.toList();
    final districts = _selectedState != null ? _locationData[_selectedState]!.keys.toList() : <String>[];
    final markets = (_selectedState != null && _selectedDistrict != null)
        ? (_locationData[_selectedState]![_selectedDistrict] ?? <String>[])
        : <String>[];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(AppStrings.get('select_region', languageProvider.langCode), style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Color(0xFF1B5E20))),
        const SizedBox(height: 10),
        _buildDropdown(hint: AppStrings.get('select_state', languageProvider.langCode), value: _selectedState, items: states, onChanged: (val) {
          setState(() { _selectedState = val; _selectedDistrict = null; _selectedMarket = null; });
        }),
        const SizedBox(height: 10),
        _buildDropdown(hint: AppStrings.get('select_district', languageProvider.langCode), value: _selectedDistrict, items: districts, onChanged: (val) {
          setState(() { _selectedDistrict = val; _selectedMarket = null; });
        }),
        const SizedBox(height: 10),
        _buildDropdown(hint: AppStrings.get('select_mandi', languageProvider.langCode), value: _selectedMarket, items: markets, onChanged: (val) {
          setState(() { _selectedMarket = val; });
        }),
      ],
    );
  }

  Widget _buildCropSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(AppStrings.get('select_crop', languageProvider.langCode), style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Color(0xFF1B5E20))),
        const SizedBox(height: 10),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.grey.shade300),
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              hint: Text(AppStrings.get('select_crop_hint', languageProvider.langCode)),
              value: _selectedCropId,
              isExpanded: true,
              items: _crops.map((crop) => DropdownMenuItem(
                value: crop['id'],
                child: Text(crop['name']!, style: const TextStyle(fontWeight: FontWeight.w600)),
              )).toList(),
              onChanged: (val) => setState(() { _selectedCropId = val; }),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildDropdown({
    required String hint,
    required String? value,
    required List<String> items,
    required Function(String?) onChanged,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: items.isEmpty ? Colors.grey.shade100 : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade300),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          hint: Text(hint, style: const TextStyle(fontSize: 14)),
          value: value,
          isExpanded: true,
          iconEnabledColor: const Color(0xFF2E7D32),
          disabledHint: Text(hint, style: const TextStyle(color: Colors.grey, fontSize: 14)),
          items: items.map((item) => DropdownMenuItem(
            value: item,
            child: Text(item, style: const TextStyle(fontWeight: FontWeight.w500)),
          )).toList(),
          onChanged: items.isEmpty ? null : onChanged,
        ),
      ),
    );
  }

  Widget _buildForecastView(Map<String, dynamic> data) {
    final bool isOffline = data['is_offline_cached'] == true || data['is_offline_mock'] == true;
    final List<dynamic> forecastDays = data['forecast_days'] ?? [];
    final double price = (data['predicted_price'] is int)
        ? (data['predicted_price'] as int).toDouble()
        : (data['predicted_price'] ?? 0.0);
    final String advisory = data['advisory'] ?? '';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildMainPriceCard(price, isOffline, advisory, data),
        const SizedBox(height: 24),
        Row(
          children: [
            const Icon(Icons.trending_up, color: Color(0xFF2E7D32), size: 20),
            const SizedBox(width: 8),
            Text(AppStrings.get('next_7_days', languageProvider.langCode), style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold, color: Color(0xFF1B5E20))),
          ],
        ),
        const SizedBox(height: 4),
        Text(AppStrings.get('forecast_disclaimer', languageProvider.langCode), style: const TextStyle(fontSize: 11, color: Colors.black45)),
        const SizedBox(height: 12),
        ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: forecastDays.length,
          itemBuilder: (context, index) => _buildDayCard(forecastDays[index], index),
        ),
      ],
    );
  }

  Widget _buildMainPriceCard(double price, bool isOffline, String advisory, Map<String, dynamic> data) {
    // Determine which of the 3 states to show
    final bool isMock = data['is_offline_mock'] == true;
    final bool isCached = data['is_offline_cached'] == true;
    
    String badgeLabel;
    Color badgeBg, badgeBorder, badgeFg;
    IconData badgeIcon;

    if (!isOffline && !isMock && !isCached) {
      badgeLabel = 'Live Mandi';
      badgeBg = Colors.green.shade50;
      badgeBorder = Colors.green.shade200;
      badgeFg = Colors.green.shade700;
      badgeIcon = Icons.wifi;
    } else if (isCached) {
      badgeLabel = languageProvider.langCode == 'hi' ? 'सहेजा डेटा' : 'Saved Data';
      badgeBg = Colors.blue.shade50;
      badgeBorder = Colors.blue.shade200;
      badgeFg = Colors.blue.shade700;
      badgeIcon = Icons.cloud_done_outlined;
    } else {
      // It's a Mock/Fallback
      badgeLabel = languageProvider.langCode == 'hi' ? 'बिना इंटरनेट' : 'Offline';
      badgeBg = Colors.orange.shade50;
      badgeBorder = Colors.orange.shade200;
      badgeFg = Colors.orange.shade700;
      badgeIcon = Icons.wifi_off;
    }

    return Card(
      elevation: 5,
      shadowColor: Colors.green.withOpacity(0.15),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          gradient: const LinearGradient(
            colors: [Color(0xFFFFFFFF), Color(0xFFEFF7EF)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        padding: const EdgeInsets.all(22.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(AppStrings.get('today_market_price', languageProvider.langCode), style: const TextStyle(color: Colors.black54, fontWeight: FontWeight.w600, fontSize: 14)),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: badgeBg,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: badgeBorder),
                  ),
                  child: Row(
                    children: [
                      Icon(badgeIcon, size: 12, color: badgeFg),
                      const SizedBox(width: 4),
                      Text(badgeLabel, style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: badgeFg)),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              '₹${price.toStringAsFixed(0)} ${AppStrings.get('per_quintal', languageProvider.langCode)}',
              style: const TextStyle(fontSize: 34, fontWeight: FontWeight.w900, color: Color(0xFF2E7D32)),
            ),
            if (isMock) ...[
              const SizedBox(height: 6),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.orange.shade50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.info_outline, size: 14, color: Colors.orange),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        AppStrings.get('advisory_offline_mock', languageProvider.langCode),
                        style: const TextStyle(fontSize: 11, color: Colors.orange),
                      ),
                    ),
                  ],
                ),
              ),
            ],
            if (advisory.isNotEmpty) ...[
              const Divider(height: 24),
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.lightbulb_outline, color: Color(0xFF2E7D32), size: 18),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      advisory,
                      style: const TextStyle(color: Color(0xFF2E7D32), fontWeight: FontWeight.w600, fontSize: 13),
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildDayCard(dynamic day, int index) {
    final date = DateTime.now().add(Duration(days: index + 1));
    final dayStr = _weekday(date.weekday);
    final dateStr = '${date.day.toString().padLeft(2, '0')}/${date.month.toString().padLeft(2, '0')}';

    final double price = (day['price'] is int)
        ? (day['price'] as int).toDouble()
        : ((day['price'] ?? 0.0) as double);

    final double confidence = (day['confidence'] != null)
        ? ((day['confidence'] is int)
            ? (day['confidence'] as int).toDouble()
            : (day['confidence'] as double))
        : 0.0;

    String reliabilityText;
    Color reliabilityColor;
    IconData reliabilityIcon;
    if (confidence > 0.8) {
      reliabilityText = AppStrings.get('good_confidence', languageProvider.langCode);
      reliabilityColor = Colors.green.shade700;
      reliabilityIcon = Icons.check_circle_outline;
    } else if (confidence >= 0.6) {
      reliabilityText = AppStrings.get('medium_confidence', languageProvider.langCode);
      reliabilityColor = Colors.orange.shade700;
      reliabilityIcon = Icons.remove_circle_outline;
    } else if (confidence > 0) {
      reliabilityText = AppStrings.get('low_confidence', languageProvider.langCode);
      reliabilityColor = Colors.red.shade700;
      reliabilityIcon = Icons.warning_amber_outlined;
    } else {
      reliabilityText = '';
      reliabilityColor = Colors.transparent;
      reliabilityIcon = Icons.circle;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.grey.shade200),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 6, offset: const Offset(0, 2))],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(color: const Color(0xFFE8F5E9), borderRadius: BorderRadius.circular(10)),
            child: const Icon(Icons.calendar_today_rounded, color: Color(0xFF2E7D32), size: 18),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(dayStr, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                Text(dateStr, style: TextStyle(color: Colors.grey.shade500, fontSize: 12)),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '₹${price.toStringAsFixed(0)}',
                style: const TextStyle(fontWeight: FontWeight.w900, color: Color(0xFF1B5E20), fontSize: 18),
              ),
              if (reliabilityText.isNotEmpty)
                Row(
                  children: [
                    Icon(reliabilityIcon, size: 11, color: reliabilityColor),
                    const SizedBox(width: 3),
                    Text(reliabilityText, style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: reliabilityColor)),
                  ],
                ),
            ],
          ),
        ],
      ),
    );
  }

  String _weekday(int w) {
    switch (w) {
      case 1: return AppStrings.get('mon', languageProvider.langCode);
      case 2: return AppStrings.get('tue', languageProvider.langCode);
      case 3: return AppStrings.get('wed', languageProvider.langCode);
      case 4: return AppStrings.get('thu', languageProvider.langCode);
      case 5: return AppStrings.get('fri', languageProvider.langCode);
      case 6: return AppStrings.get('sat', languageProvider.langCode);
      case 7: return AppStrings.get('sun', languageProvider.langCode);
      default: return '';
    }
  }
}
