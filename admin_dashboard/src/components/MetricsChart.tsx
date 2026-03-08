import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { format } from "date-fns";
import { apiClient } from "@/lib/api";
import { MetricSeries } from "@/types";

export default function MetricsChart({ modelType }: { modelType: string }) {
    const [seriesData, setSeriesData] = useState<MetricSeries[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchMetrics() {
            try {
                setLoading(true);
                const res = await apiClient.get<MetricSeries[]>(`/metrics/${modelType}/rolling?days=30`);
                setSeriesData(res.data);
            } catch (err) {
                console.error("Failed to fetch rolling metrics", err);
            } finally {
                setLoading(false);
            }
        }
        fetchMetrics();
    }, [modelType]);

    if (loading) {
        return <div className="h-80 bg-gray-50 rounded-xl animate-pulse w-full mb-6" />;
    }

    if (seriesData.length === 0) {
        return (
            <div className="h-80 bg-white rounded-xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] border border-gray-100 flex items-center justify-center text-gray-400 mb-6">
                No metric history available for the last 30 days.
            </div>
        );
    }

    // Transform data for Recharts: combine series by date
    const combinedData: any[] = [];
    const allDates = new Set<string>();

    seriesData.forEach(series => {
        series.data_points.forEach(dp => {
            // Use short date string format for matching
            const dateStr = format(new Date(dp.window_end), "MMM dd");
            allDates.add(dateStr);
        });
    });

    Array.from(allDates).sort().forEach(dateStr => {
        const point: any = { date: dateStr };
        seriesData.forEach(series => {
            // Find matching point in this series
            const match = series.data_points.find(dp => format(new Date(dp.window_end), "MMM dd") === dateStr);
            if (match) {
                point[series.metric_name] = match.metric_value;
            }
        });
        combinedData.push(point);
    });

    const colors = ["#10b981", "#3b82f6", "#f59e0b", "#ec4899"];

    return (
        <div className="glass-card p-1 shadow-green-900/5 transition-all duration-500 mb-8 overflow-hidden group">
            <div className="p-8">
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h3 className="text-lg font-black text-slate-800 tracking-tight">System Reliability Index</h3>
                        <p className="text-sm text-slate-400 font-medium">30-day evaluation telemetry</p>
                    </div>
                </div>

                <div className="h-[350px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={combinedData} margin={{ top: 20, right: 20, bottom: 20, left: -20 }}>
                            <CartesianGrid strokeDasharray="8 8" vertical={false} stroke="#f1f5f9" />
                            <XAxis
                                dataKey="date"
                                axisLine={false}
                                tickLine={false}
                                tick={{ fontSize: 10, fill: "#cbd5e1", fontWeight: 700 }}
                                dy={15}
                            />
                            <YAxis
                                axisLine={false}
                                tickLine={false}
                                tick={{ fontSize: 10, fill: "#cbd5e1", fontWeight: 700 }}
                                domain={['auto', 'auto']}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                                    backdropFilter: 'blur(8px)',
                                    borderRadius: '16px',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1)',
                                    color: '#fff',
                                    fontSize: '12px',
                                    fontWeight: 'bold'
                                }}
                                itemStyle={{ padding: '2px 0' }}
                                cursor={{ stroke: '#10b981', strokeWidth: 2, strokeDasharray: '4 4' }}
                            />
                            <Legend
                                verticalAlign="top"
                                align="right"
                                iconType="circle"
                                wrapperStyle={{ paddingBottom: '30px', fontSize: '11px', fontWeight: 'bold', color: '#64748b' }}
                            />

                            {seriesData.map((series, idx) => (
                                <Line
                                    key={series.metric_name}
                                    type="monotone"
                                    dataKey={series.metric_name}
                                    stroke={colors[idx % colors.length]}
                                    strokeWidth={4}
                                    dot={{ r: 4, fill: colors[idx % colors.length], strokeWidth: 2, stroke: '#fff' }}
                                    activeDot={{ r: 8, strokeWidth: 0 }}
                                    animationDuration={1500}
                                    connectNulls
                                />
                            ))}
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
}
