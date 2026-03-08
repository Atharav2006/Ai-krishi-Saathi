import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../data/repositories/crop_prices_repository_impl.dart';

// --- Events ---
abstract class CropEvent extends Equatable {
  const CropEvent();
  @override
  List<Object> get props => [];
}

class FetchMandiPrices extends CropEvent {
  final String cropId;
  final String districtId;
  const FetchMandiPrices(this.cropId, this.districtId);
  @override
  List<Object> get props => [cropId, districtId];
}

class FetchPricePrediction extends CropEvent {
  final String cropId;
  final String districtId;
  const FetchPricePrediction(this.cropId, this.districtId);
  @override
  List<Object> get props => [cropId, districtId];
}

// --- States ---
abstract class CropState extends Equatable {
  const CropState();
  @override
  List<Object> get props => [];
}

class CropInitial extends CropState {}
class CropLoading extends CropState {}

class CropPricesLoaded extends CropState {
  final List<dynamic> prices;
  const CropPricesLoaded(this.prices);
  @override
  List<Object> get props => [prices];
}

class CropPriceLoaded extends CropState {
  final Map<String, dynamic> data;
  const CropPriceLoaded(this.data);
  @override
  List<Object> get props => [data];
}

class CropError extends CropState {
  final String message;
  const CropError(this.message);
  @override
  List<Object> get props => [message];
}

// --- Bloc ---
class CropBloc extends Bloc<CropEvent, CropState> {
  final CropPricesRepository _repository;

  CropBloc(this._repository) : super(CropInitial()) {
    on<FetchMandiPrices>(_onFetchMandiPrices);
    on<FetchPricePrediction>(_onFetchPricePrediction);
  }

  Future<void> _onFetchMandiPrices(FetchMandiPrices event, Emitter<CropState> emit) async {
    emit(CropLoading());
    try {
      final data = await _repository.getMandiPrices(cropId: event.cropId, districtId: event.districtId);
      emit(CropPricesLoaded(data));
    } catch (e) {
      emit(const CropError("Failed to fetch mandi prices. Ensure initial offline download synced first."));
    }
  }

  Future<void> _onFetchPricePrediction(FetchPricePrediction event, Emitter<CropState> emit) async {
    emit(CropLoading());
    try {
      final predictionData = await _repository.predictPrice(cropId: event.cropId, districtId: event.districtId);
      emit(CropPriceLoaded(predictionData));
    } catch (e) {
      emit(const CropError("Prediction Engine is unreachable. Please connect to the internet."));
    }
  }
}
