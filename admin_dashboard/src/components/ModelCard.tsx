import { useEffect, useState } from "react";
import { format } from "date-fns";
import { AlertTriangle, Clock, Server } from "lucide-react";
import clsx from "clsx";
import { apiClient } from "@/lib/api";
import { ModelRegistryEntry } from "@/types";

export default function ModelCard({ modelType }: { modelType: string }) {
    const [model, setModel] = useState<ModelRegistryEntry | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchActive() {
            try {
                setLoading(true);
                const res = await apiClient.get<ModelRegistryEntry>(`/registry/${modelType}/active`);
                setModel(res.data);
            } catch (err) {
                console.error("No active model found", err);
                setModel(null);
            } finally {
                setLoading(false);
            }
        }
        fetchActive();
    }, [modelType]);

    if (loading) {
        return <div className="h-48 bg-gray-50 rounded-xl animate-pulse mb-6" />;
    }

    if (!model) {
        return (
            <div className="bg-white rounded-xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] p-6 mb-6 border border-gray-100 flex items-center gap-4 text-gray-500">
                <Server size={24} className="text-gray-300" />
                <p>No active model deployed for <span className="font-semibold text-gray-700">{modelType}</span></p>
            </div>
        );
    }

    const isDegraded = model.status === "degraded";

    return (
        <div className={clsx(
            "glass-card p-1 transition-all duration-500 mb-8 overflow-hidden group",
            isDegraded
                ? "shadow-rose-500/10 border-rose-200/50"
                : "shadow-green-500/10 border-white/40"
        )}>
            <div className="p-8">
                <div className="flex items-center justify-between mb-8">
                    <div className="space-y-1">
                        <div className="flex items-center gap-3">
                            <h2 className="text-2xl font-black text-slate-800 tracking-tight">
                                {model.model_type.replace(/_/g, " ").toUpperCase()}
                            </h2>
                            <span className={clsx(
                                "text-[10px] px-3 py-1 rounded-full font-bold uppercase tracking-widest border",
                                isDegraded
                                    ? "bg-rose-50 text-rose-600 border-rose-100"
                                    : "bg-emerald-50 text-emerald-600 border-emerald-100"
                            )}>
                                {model.status.toUpperCase()}
                            </span>
                        </div>
                        <p className="text-sm text-slate-400 font-medium">Core Intelligence Instance</p>
                    </div>
                    <div className="flex items-center gap-2 text-xs font-bold text-slate-500 bg-white shadow-sm border border-slate-100 px-4 py-2 rounded-2xl">
                        <Server size={14} className="text-green-500" />
                        v.{model.model_version}
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    <div className="flex items-center gap-4 bg-slate-50/50 p-4 rounded-2xl border border-slate-100">
                        <div className="bg-white p-2.5 rounded-xl shadow-sm">
                            <Clock size={20} className="text-slate-400" />
                        </div>
                        <div>
                            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Last Training</p>
                            <p className="text-sm font-semibold text-slate-700">
                                {model.trained_at ? format(new Date(model.trained_at), "MMM d, yyyy · HH:mm") : "Unknown"}
                            </p>
                        </div>
                    </div>

                    {isDegraded && (
                        <div className="flex items-center gap-4 bg-rose-50/50 p-4 rounded-2xl border border-rose-100 animate-pulse">
                            <div className="bg-white p-2.5 rounded-xl shadow-sm">
                                <AlertTriangle size={20} className="text-rose-500" />
                            </div>
                            <div>
                                <p className="text-[10px] font-bold text-rose-400 uppercase tracking-wider">System Alert</p>
                                <p className="text-sm font-semibold text-rose-700">Degradation Detected</p>
                            </div>
                        </div>
                    )}
                </div>

                {isDegraded && (
                    <div className="mb-8 bg-rose-50/30 p-4 rounded-2xl border border-rose-100/50 text-sm text-rose-700/80 leading-relaxed">
                        Automatic recovery triggered. The system is evaluating candidate promotions or retraining pipelines to restore performance.
                    </div>
                )}

                {/* Metrics Visual Block */}
                <div className="space-y-4">
                    <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] px-1">Performance Benchmarks</h3>
                    <div className="bg-slate-900 rounded-3xl p-6 shadow-2xl relative overflow-hidden group-hover:shadow-green-900/20 transition-all duration-700">
                        {/* Decorative scan line */}
                        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-green-500/5 to-transparent h-[200%] -translate-y-[100%] group-hover:translate-y-[100%] transition-transform duration-[3000ms] pointer-events-none" />

                        {model.metrics_snapshot ? (
                            <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                                {Object.entries(model.metrics_snapshot).map(([key, value]) => (
                                    <div key={key} className="space-y-1">
                                        <p className="text-[10px] font-bold text-green-500/50 uppercase tracking-widest">{key}</p>
                                        <p className="text-xl font-mono text-green-400 font-bold">{String(value)}</p>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-slate-500 font-mono text-sm py-4">NO_TELEMETRY_DATA_AVAILABLE</div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
