"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { LayoutDashboard, LogOut } from "lucide-react";
import Link from "next/link";
import clsx from "clsx";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
    const router = useRouter();
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
        // Rough auth check on mount (api interceptor handles real validation)
        if (!localStorage.getItem("krishi_access_token")) {
            router.replace("/login");
        }
    }, [router]);

    const handleLogout = () => {
        localStorage.removeItem("krishi_access_token");
        router.push("/login");
    };

    if (!mounted) return null; // Prevent hydration mismatch

    return (
        <div className="min-h-screen bg-[#f0fdf4] flex text-slate-800 font-sans selection:bg-green-100">
            {/* Glass Sidebar */}
            <aside className="w-72 glass-sidebar flex flex-col hidden md:flex fixed h-full z-20">
                <div className="h-20 flex items-center px-8 border-b border-white/10">
                    <div className="flex items-center gap-3">
                        <div className="bg-gradient-to-br from-green-400 to-emerald-600 p-2 rounded-2xl shadow-lg shadow-green-500/20">
                            <LayoutDashboard className="text-white" size={24} />
                        </div>
                        <span className="text-white font-bold text-xl tracking-tight">AI Krishi Saathi</span>
                    </div>
                </div>

                <div className="flex-1 py-8 px-6 space-y-4">
                    <p className="px-2 text-[10px] font-bold text-green-300 uppercase tracking-[0.2em] opacity-60">
                        Operations Hub
                    </p>
                    <nav className="space-y-2">
                        <Link
                            href="/admin?model=price_forecast"
                            className={clsx(
                                "flex items-center gap-3 px-4 py-3.5 rounded-2xl transition-all duration-300 group",
                                "bg-white/10 text-white font-semibold shadow-inner shadow-white/5 border border-white/10"
                            )}
                        >
                            <LayoutDashboard className="text-green-400 group-hover:scale-110 transition-transform" size={20} />
                            MLOps Insights
                        </Link>
                    </nav>
                </div>

                <div className="p-6 border-t border-white/5">
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-3 px-4 py-3.5 w-full rounded-2xl text-green-100/70 hover:text-white hover:bg-white/5 font-medium transition-all group"
                    >
                        <LogOut className="text-green-300/50 group-hover:text-red-400 transition-colors" size={20} />
                        Exit System
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 md:ml-72 min-w-0 relative overflow-hidden">
                {/* Decorative blob */}
                <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-green-200/30 blur-[120px] rounded-full -z-10" />
                <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-100/30 blur-[120px] rounded-full -z-10" />

                <div className="max-w-7xl mx-auto p-10 mt-4">
                    {children}
                </div>
            </main>
        </div>
    );
}
