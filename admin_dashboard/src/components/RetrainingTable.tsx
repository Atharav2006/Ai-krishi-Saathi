import { useEffect, useState } from "react";
import { format } from "date-fns";
import clsx from "clsx";
import { Play, CheckCircle2, XCircle, Clock } from "lucide-react";
import { apiClient } from "@/lib/api";
import { RetrainingJob } from "@/types";

export default function RetrainingTable({ modelType }: { modelType: string }) {
    const [jobs, setJobs] = useState<RetrainingJob[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchJobs() {
            try {
                const res = await apiClient.get<RetrainingJob[]>(`/retraining?limit=50`);
                // Filter locally by modelType for now
                const filtered = res.data.filter(j => j.model_type === modelType);
                setJobs(filtered);
            } catch (err) {
                console.error("Failed to fetch retraining jobs", err);
            } finally {
                setLoading(false);
            }
        }
        fetchJobs();
        const interval = setInterval(fetchJobs, 20000); // refresh every 20s
        return () => clearInterval(interval);
    }, [modelType]);

    const StatusBadge = ({ status }: { status: string }) => {
        switch (status) {
            case "pending":
                return <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-gray-100 text-gray-600 border border-gray-200"><Clock size={12} /> Pending</span>;
            case "running":
                return <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200"><Play size={12} className="animate-pulse" /> Running</span>;
            case "success":
                return <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-green-50 text-green-700 border border-green-200"><CheckCircle2 size={12} /> Success</span>;
            case "failed":
                return <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-red-50 text-red-700 border border-red-200"><XCircle size={12} /> Failed</span>;
            default:
                return <span>{status}</span>;
        }
    };

    if (loading) {
        return <div className="h-64 bg-gray-50 rounded-xl animate-pulse mt-8" />;
    }

    return (
        <div className="glass-card shadow-green-900/5 transition-all duration-500 overflow-hidden mt-10 border-white/40 group">
            <div className="p-8 border-b border-slate-100 flex items-center justify-between bg-white/30 backdrop-blur-md">
                <div>
                    <h3 className="text-lg font-black text-slate-800 tracking-tight">Machine Learning Pipeline</h3>
                    <p className="text-sm text-slate-400 font-medium">Automatic lifecycle & retraining history</p>
                </div>
                <div className="px-4 py-2 bg-slate-50 border border-slate-200 rounded-2xl flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-ping" />
                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Live Monitoring</span>
                </div>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full text-left">
                    <thead>
                        <tr className="border-b border-slate-100 bg-slate-50/30">
                            {["Trigger", "Status", "Temporal Data", "Version Shift"].map((header) => (
                                <th key={header} className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
                                    {header}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                        {jobs.length === 0 ? (
                            <tr>
                                <td colSpan={4} className="px-8 py-20 text-center">
                                    <div className="flex flex-col items-center gap-3">
                                        <div className="bg-slate-50 p-4 rounded-3xl">
                                            <Clock className="text-slate-200" size={32} />
                                        </div>
                                        <p className="text-xs font-bold text-slate-300 uppercase tracking-widest">No pipeline cycles recorded</p>
                                    </div>
                                </td>
                            </tr>
                        ) : (
                            jobs.map((job) => (
                                <tr key={job.id} className="hover:bg-green-50/30 transition-all duration-300 group/row">
                                    <td className="px-8 py-6">
                                        <div className="flex flex-col">
                                            <span className="text-sm font-black text-slate-700 capitalize tracking-tight group-hover/row:text-green-700 transition-colors">
                                                {job.triggered_by}
                                            </span>
                                            <span className="text-[10px] text-slate-400 font-bold uppercase tracking-tighter opacity-60">System Initiated</span>
                                        </div>
                                    </td>
                                    <td className="px-8 py-6"><StatusBadge status={job.status} /></td>
                                    <td className="px-8 py-6">
                                        <div className="space-y-1">
                                            <div className="flex items-center gap-2 text-xs font-bold text-slate-600">
                                                <Clock size={12} className="text-slate-300" />
                                                {job.started_at ? format(new Date(job.started_at), "MMM d · HH:mm") : "—"}
                                            </div>
                                            {job.completed_at && (
                                                <div className="text-[10px] text-slate-400 font-medium ml-5">
                                                    Duration: {Math.round((new Date(job.completed_at).getTime() - new Date(job.started_at!).getTime()) / 1000)}s
                                                </div>
                                            )}
                                        </div>
                                    </td>
                                    <td className="px-8 py-6">
                                        <div className="flex items-center gap-3">
                                            <div className="flex flex-col">
                                                <span className="text-[10px] text-slate-400 font-bold uppercase opacity-40">From</span>
                                                <span className="text-xs font-mono text-slate-400">v.{job.old_model_version.split("_").pop()}</span>
                                            </div>
                                            <div className="h-px w-4 bg-slate-200" />
                                            <div className="flex flex-col">
                                                <span className="text-[10px] text-emerald-400 font-bold uppercase">To</span>
                                                <span className="text-xs font-black font-mono text-emerald-600">
                                                    {job.new_model_version ? `v.${job.new_model_version.split("_").pop()}` : "—"}
                                                </span>
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
