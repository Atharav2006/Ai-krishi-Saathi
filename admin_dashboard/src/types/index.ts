export interface SystemSummary {
    predictions_last_24h: number;
    degraded_models_count: number;
    pending_retraining_jobs: number;
}

export interface MetricPoint {
    window_end: string;
    metric_value: number;
}

export interface MetricSeries {
    metric_name: string;
    data_points: MetricPoint[];
}

export interface DegradationLog {
    id: string;
    model_type: string;
    model_version: string;
    metric_name: string;
    metric_value: number;
    threshold: number;
    triggered_at: string;
}

export interface RetrainingJob {
    id: string;
    model_type: string;
    triggered_by: string;
    status: "pending" | "running" | "success" | "failed";
    old_model_version: string;
    new_model_version: string | null;
    started_at: string | null;
    completed_at: string | null;
    error_message: string | null;
    created_at: string;
}

export interface ModelRegistryEntry {
    id: string;
    model_type: string;
    model_version: string;
    status: "candidate" | "active" | "degraded";
    trained_at: string | null;
    metrics_snapshot: Record<string, any> | null;
    created_at: string;
}
