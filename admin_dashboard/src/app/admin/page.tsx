"use client";

import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import Link from "next/link";
import clsx from "clsx";

import SystemSummaryBanner from "@/components/SystemSummary";
import ModelCard from "@/components/ModelCard";
import MetricsChart from "@/components/MetricsChart";
import DegradationList from "@/components/DegradationList";
import RetrainingTable from "@/components/RetrainingTable";
import PromoteButton from "@/components/PromoteButton";

function DashboardContent() {
    const searchParams = useSearchParams();
    const modelParam = searchParams?.get("model");
    const modelType = modelParam === "disease_detection" ? "disease_detection" : "price_forecast";

    return (
        <>
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
                <div>
                    <h1 className="text-5xl font-black tracking-tight text-slate-800 mb-2">
                        MLOps <span className="premium-gradient-text text-5xl">Intelligence</span>
                    </h1>
                    <p className="text-slate-400 font-medium text-lg">Orchestrating agricultural decision support models.</p>
                </div>
                <PromoteButton modelType={modelType} />
            </div>

            <SystemSummaryBanner />

            {/* Model Type Tabs */}
            <div className="flex space-x-4 mb-10 overflow-x-auto pb-2 scrollbar-hide">
                <Link
                    href="?model=price_forecast"
                    className={clsx(
                        "px-8 py-3 rounded-2xl text-sm font-black transition-all duration-500 whitespace-nowrap border-b-4",
                        modelType === "price_forecast"
                            ? "bg-white text-green-700 border-green-500 shadow-xl shadow-green-500/10 scale-105"
                            : "bg-transparent text-slate-400 border-transparent hover:text-slate-600"
                    )}
                >
                    Market Price Forecasting
                </Link>
                <Link
                    href="?model=disease_detection"
                    className={clsx(
                        "px-8 py-3 rounded-2xl text-sm font-black transition-all duration-500 whitespace-nowrap border-b-4",
                        modelType === "disease_detection"
                            ? "bg-white text-green-700 border-green-500 shadow-xl shadow-green-500/10 scale-105"
                            : "bg-transparent text-slate-400 border-transparent hover:text-slate-600"
                    )}
                >
                    Crop Disease Detection
                </Link>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-10">
                {/* Left Column (2/3) */}
                <div className="lg:col-span-2">
                    <ModelCard modelType={modelType} />
                    <MetricsChart modelType={modelType} />
                </div>

                {/* Right Column (1/3) */}
                <div className="lg:col-span-1">
                    <DegradationList modelType={modelType} />
                </div>
            </div>

            <RetrainingTable modelType={modelType} />
        </>
    );
}

export default function AdminDashboard() {
    return (
        <Suspense fallback={<div className="h-screen w-full flex items-center justify-center animate-pulse text-gray-400 font-medium">Loading Dashboard...</div>}>
            <DashboardContent />
        </Suspense>
    );
}
