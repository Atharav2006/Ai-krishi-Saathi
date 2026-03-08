import { useEffect, useState } from "react";
import { format } from "date-fns";
import { AlertCircle } from "lucide-react";
import { apiClient } from "@/lib/api";
import { DegradationLog } from "@/types";

export default function DegradationList({ modelType }: { modelType: string }) {
    const [logs, setLogs] = useState<DegradationLog[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchLogs() {
            try {
                setLoading(true);
                const res = await apiClient.get<DegradationLog[]>(`/degradation/${modelType}?limit=20`);
                setLogs(res.data);
            } catch (err) {
                console.error("Failed to fetch degradation logs", err);
            } finally {
                setLoading(false);
            }
        }
        fetchLogs();
    }, [modelType]);

    if (loading) {
        return <div className="h-64 bg-gray-50 rounded-xl animate-pulse" />;
    }

    return (
        <div className="glass-card shadow-rose-900/5 transition-all duration-500 overflow-hidden h-full flex flex-col border-white/40">
            <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-white/30 backdrop-blur-md sticky top-0 z-10">
                <h3 className="text-sm font-black text-slate-800 uppercase tracking-widest">Health Event Log</h3>
                <span className="text-[10px] font-bold bg-rose-50 text-rose-500 px-3 py-1 rounded-full border border-rose-100 uppercase tracking-tighter">
                    Last 20 events
                </span>
            </div>

            <div className="p-4 overflow-y-auto flex-1 max-h-[450px] scrollbar-hide">
                {logs.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-64 text-slate-300">
                        <p className="font-bold text-xs uppercase tracking-[0.2em] animate-pulse">Telemetry Clean</p>
                    </div>
                ) : (
                    <ul className="space-y-3">
                        {logs.map((log) => (
                            <li key={log.id} className="p-4 bg-white/50 hover:bg-white rounded-2xl transition-all duration-300 border border-slate-50 hover:border-slate-100 hover:shadow-lg hover:shadow-slate-200/50 group">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                                        {format(new Date(log.triggered_at), "MMM d · HH:mm")}
                                    </span>
                                    <span className="text-[10px] font-black bg-slate-100 text-slate-500 px-2 py-0.5 rounded-lg border border-slate-200 group-hover:bg-green-100 group-hover:text-green-600 group-hover:border-green-200 transition-colors">
                                        v.{log.model_version.split("_").pop()}
                                    </span>
                                </div>
                                <div className="flex items-start gap-3">
                                    <div className="bg-rose-100 p-1.5 rounded-lg mt-0.5 group-hover:scale-110 transition-transform">
                                        <AlertCircle size={14} className="text-rose-500" />
                                    </div>
                                    <div className="space-y-1">
                                        <p className="text-xs text-slate-600 font-bold leading-tight uppercase tracking-tight">
                                            {log.metric_name} Breach
                                        </p>
                                        <p className="text-[11px] text-slate-400 font-medium">
                                            Value: <span className="text-rose-500 font-bold">{log.metric_value.toFixed(4)}</span>
                                            <span className="mx-1 opacity-40">/</span>
                                            Limit: {log.threshold.toFixed(4)}
                                        </p>
                                    </div>
                                </div>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
}
