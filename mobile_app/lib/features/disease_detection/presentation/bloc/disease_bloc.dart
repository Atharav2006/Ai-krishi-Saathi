import 'dart:io';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../data/repositories/disease_detection_repository_impl.dart';

// --- Events ---
abstract class DiseaseEvent extends Equatable {
  const DiseaseEvent();
  @override
  List<Object> get props => [];
}

class AnalyzeImage extends DiseaseEvent {
  final File document;
  final String cropId;
  final String districtId;
  
  const AnalyzeImage(this.document, this.cropId, this.districtId);
  @override
  List<Object> get props => [document, cropId, districtId];
}

// --- States ---
abstract class DiseaseState extends Equatable {
  const DiseaseState();
  @override
  List<Object> get props => [];
}

class DiseaseInitial extends DiseaseState {}
class DiseaseLoading extends DiseaseState {}

class DiseaseResultLoaded extends DiseaseState {
  final Map<String, dynamic> result;
  
  const DiseaseResultLoaded(this.result);
  @override
  List<Object> get props => [result];
}

class DiseaseError extends DiseaseState {
  final String message;
  const DiseaseError(this.message);
  @override
  List<Object> get props => [message];
}

// --- Bloc ---
class DiseaseBloc extends Bloc<DiseaseEvent, DiseaseState> {
  final DiseaseDetectionRepository _repository;

  DiseaseBloc(this._repository) : super(DiseaseInitial()) {
    on<AnalyzeImage>(_onAnalyzeImage);
  }

  Future<void> _onAnalyzeImage(AnalyzeImage event, Emitter<DiseaseState> emit) async {
    emit(DiseaseLoading());
    try {
      final result = await _repository.detectDisease(event.document, event.cropId, event.districtId);
      emit(DiseaseResultLoaded(result));
    } catch (e) {
      // Pass the specific error message to the UI
      emit(DiseaseError(e.toString()));
    }
  }
}
