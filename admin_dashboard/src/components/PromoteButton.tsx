"use client";

import { useState } from "react";
import { CopyCheck, Loader2 } from "lucide-react";
import clsx from "clsx";
import { apiClient } from "@/lib/api";

export default function PromoteButton({ modelType }: { modelType: string }) {
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState<boolean | null>(null);

    const handlePromote = async () => {
        if (!window.confirm(`Are you sure you want to promote the candidate model for ${modelType}? This will override the current active model in production.`)) {
            return;
        }

        try {
            setLoading(true);

            // 1. Find the newest candidate ID for this model type
            const versionsRes = await apiClient.get(`/registry/${modelType}/versions`);
            const candidates = versionsRes.data.filter((v: any) => v.status === "candidate");

            if (candidates.length === 0) {
                alert("No candidate models available to promote.");
                setLoading(false);
                return;
            }

            const candidateId = candidates[0].id;

            // 2. Promote the candidate
            await apiClient.post(`/registry/promote`, { candidate_id: candidateId });

            setSuccess(true);
            setTimeout(() => window.location.reload(), 2000); // hard refresh to show new active model
        } catch (err: any) {
            console.error("Failed to promote", err);

            let errMsg = "Failed to promote candidate.";
            if (err.response?.data?.detail) {
                errMsg = typeof err.response.data.detail === 'string'
                    ? err.response.data.detail
                    : JSON.stringify(err.response.data.detail);
            }

            alert(errMsg);
            setSuccess(false);
            setTimeout(() => setSuccess(null), 3000);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex items-center gap-4">
            {success === true && (
                <span className="text-xs text-emerald-600 font-bold flex items-center gap-2 animate-bounce">
                    <CopyCheck size={14} /> Propagation Complete
                </span>
            )}
            <button
                onClick={handlePromote}
                disabled={loading || success === true}
                className={clsx(
                    "px-6 py-3 rounded-2xl text-sm font-black transition-all duration-300 flex items-center gap-3 active:scale-95 disabled:opacity-50 shadow-lg",
                    success === true
                        ? "bg-emerald-500 text-white shadow-emerald-500/40"
                        : "bg-slate-900 border border-slate-700 hover:bg-slate-800 text-white shadow-slate-900/40"
                )}
            >
                {loading ? <Loader2 size={18} className="animate-spin text-emerald-400" /> : <CopyCheck size={18} />}
                {loading ? "Syncing..." : success === true ? "Deployed" : "Promote to Prod"}
            </button>
        </div>
    );
}
