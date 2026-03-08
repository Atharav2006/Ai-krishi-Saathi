"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Lock, Mail, Loader2 } from "lucide-react";
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export default function Login() {
    const router = useRouter();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            const params = new URLSearchParams();
            params.append("username", email);
            params.append("password", password);

            // We don't use apiClient here because default interceptor expects JSON and might redirect
            const res = await axios.post(`${API_URL}/auth/login/access-token`, params, {
                headers: { "Content-Type": "application/x-www-form-urlencoded" }
            });

            const token = res.data.access_token;
            if (token) {
                localStorage.setItem("krishi_access_token", token);
                router.push("/admin?model=price_forecast");
            }
        } catch (err: any) {
            console.error(err);
            setError(err.response?.data?.detail || "Invalid credentials. Ensure your account has the 'admin' role.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-white relative flex flex-col justify-center items-center py-12 px-4 sm:px-6 lg:px-8 font-sans overflow-hidden">
            {/* Animated background blobs */}
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-100/50 rounded-full blur-[120px] animate-pulse" />
            <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-green-100/50 rounded-full blur-[120px] animate-pulse" />

            <div className="max-w-md w-full glass-card p-12 transition-all duration-700 relative z-10 border-white/40 shadow-green-900/5">
                <div className="text-center">
                    <div className="mx-auto h-20 w-20 bg-emerald-50 rounded-[2.5rem] flex items-center justify-center text-4xl shadow-lg border border-emerald-100/50 mb-8 animate-bounce">
                        🍃
                    </div>
                    <h2 className="text-4xl font-black text-slate-800 tracking-tight mb-2">
                        Krishi <span className="premium-gradient-text">Saathi</span>
                    </h2>
                    <p className="text-slate-400 font-medium text-sm uppercase tracking-widest">
                        Intelligence Dashboard
                    </p>
                </div>

                <form className="mt-12 space-y-8" onSubmit={handleLogin}>
                    <div className="space-y-5">
                        <div className="space-y-1">
                            <label className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] ml-4">Email Credentials</label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none">
                                    <Mail className="h-5 w-5 text-slate-300 group-focus-within:text-emerald-500 transition-colors" />
                                </div>
                                <input
                                    type="email"
                                    required
                                    className="block w-full px-5 py-4 pl-14 bg-slate-50 border-2 border-transparent rounded-3xl text-slate-800 placeholder-slate-300 focus:outline-none focus:ring-0 focus:border-emerald-500 focus:bg-white transition-all duration-300 sm:text-sm font-semibold"
                                    placeholder="admin@krishisaathi.in"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                            </div>
                        </div>

                        <div className="space-y-1">
                            <label className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] ml-4">Secure Password</label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none">
                                    <Lock className="h-5 w-5 text-slate-300 group-focus-within:text-emerald-500 transition-colors" />
                                </div>
                                <input
                                    type="password"
                                    required
                                    className="block w-full px-5 py-4 pl-14 bg-slate-50 border-2 border-transparent rounded-3xl text-slate-800 placeholder-slate-300 focus:outline-none focus:ring-0 focus:border-emerald-500 focus:bg-white transition-all duration-300 sm:text-sm font-semibold"
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                            </div>
                        </div>
                    </div>

                    {error && (
                        <div className="text-rose-500 text-xs text-center font-bold bg-rose-50/50 p-3 rounded-2xl border border-rose-100 flex items-center justify-center gap-2 animate-shake">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="group relative w-full flex justify-center py-5 px-6 rounded-3xl text-sm font-black text-white bg-slate-900 border border-slate-700 hover:bg-slate-800 focus:outline-none shadow-2xl shadow-slate-900/20 active:scale-95 transition-all duration-300 disabled:opacity-50"
                    >
                        {loading ? (
                            <span className="flex items-center gap-2">
                                <Loader2 size={18} className="animate-spin text-emerald-400" /> Authenticating...
                            </span>
                        ) : (
                            "Enter Command Center"
                        )}
                    </button>

                    <p className="text-center text-[10px] text-slate-300 font-bold uppercase tracking-widest">
                        SECURED BY AI KRISHI SAATHI CLOUD
                    </p>
                </form>
            </div>
        </div>
    );
}
