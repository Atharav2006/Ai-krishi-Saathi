import { useEffect, useState } from "react";
import { CopyX, Activity, RefreshCw } from "lucide-react";
import clsx from "clsx";
import { apiClient } from "@/lib/api";
import { SystemSummary } from "@/types";

export default function SystemSummaryBanner() {
    const [data, setData] = useState<SystemSummary | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchSummary() {
            try {
                const res = await apiClient.get<SystemSummary>("/admin/system-summary");
                setData(res.data);
            } catch (err) {
                console.error("Failed to fetch system summary", err);
            } finally {
                setLoading(false);
            }
        }
        fetchSummary();
        const interval = setInterval(fetchSummary, 60000); // refresh every minute
        return () => clearInterval(interval);
    }, []);

    if (loading || !data) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 animate-pulse">
                {[1, 2, 3].map((i) => (
                    <div key={i} className="h-24 bg-gray-100 rounded-xl"></div>
                ))}
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-10">
            {/* Total Predictions */}
            <div className="glass-card p-1 shadow-green-900/5 group hover:shadow-green-500/10 transition-all duration-500">
                <div className="p-7 flex items-center justify-between">
                    <div>
                        <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2 opacity-80">Predictions (24h)</p>
                        <p className="text-4xl font-black text-slate-800 tracking-tight">
                            {data.predictions_last_24h.toLocaleString()}
                        </p>
                    </div>
                    <div className="h-14 w-14 rounded-2xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center text-white shadow-lg shadow-green-500/30 group-hover:scale-110 transition-transform duration-500">
                        <Activity size={28} />
                    </div>
                </div>
                <div className="px-7 pb-4">
                    <div className="h-1 w-full bg-slate-100 rounded-full overflow-hidden">
                        <div className="h-full bg-green-500 w-[70%]" />
                    </div>
                </div>
            </div>

            {/* Degraded Models */}
            <div className="glass-card p-1 shadow-rose-900/5 group hover:shadow-rose-500/10 transition-all duration-500">
                <div className="p-7 flex items-center justify-between">
                    <div>
                        <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2 opacity-80">Health Status</p>
                        <p className={clsx(
                            "text-4xl font-black tracking-tight",
                            data.degraded_models_count > 0 ? "text-rose-500" : "text-emerald-500"
                        )}>
                            {data.degraded_models_count > 0 ? `${data.degraded_models_count} Degraded` : "All Healthy"}
                        </p>
                    </div>
                    <div className={clsx(
                        "h-14 w-14 rounded-2xl flex items-center justify-center text-white shadow-lg group-hover:scale-110 transition-transform duration-500",
                        data.degraded_models_count > 0
                            ? "bg-gradient-to-br from-rose-400 to-red-600 shadow-red-500/30"
                            : "bg-gradient-to-br from-emerald-400 to-green-600 shadow-emerald-500/30"
                    )}>
                        <CopyX size={28} />
                    </div>
                </div>
                <div className="px-7 pb-4">
                    <div className="h-1 w-full bg-slate-100 rounded-full overflow-hidden">
                        <div className={clsx(
                            "h-full w-full",
                            data.degraded_models_count > 0 ? "bg-rose-500" : "bg-emerald-500"
                        )} />
                    </div>
                </div>
            </div>

            {/* Pending Retraining */}
            <div className="glass-card p-1 shadow-amber-900/5 group hover:shadow-amber-500/10 transition-all duration-500">
                <div className="p-7 flex items-center justify-between">
                    <div>
                        <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2 opacity-80">Active Pipelines</p>
                        <p className="text-4xl font-black text-slate-800 tracking-tight">
                            {data.pending_retraining_jobs} Jobs
                        </p>
                    </div>
                    <div className="h-14 w-14 rounded-2xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center text-white shadow-lg shadow-amber-500/30 group-hover:scale-110 transition-transform duration-500">
                        <RefreshCw size={28} className={data.pending_retraining_jobs > 0 ? "animate-spin" : ""} />
                    </div>
                </div>
                <div className="px-7 pb-4">
                    <div className="h-1 w-full bg-slate-100 rounded-full overflow-hidden">
                        <div className={clsx(
                            "h-full bg-amber-500 transition-all duration-1000",
                            data.pending_retraining_jobs > 0 ? "w-[40%] animate-pulse" : "w-0"
                        )} />
                    </div>
                </div>
            </div>
        </div>
    );
}
