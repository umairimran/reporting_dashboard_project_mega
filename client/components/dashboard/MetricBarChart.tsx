"use client";

import { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { cn, formatCurrency, formatNumber } from "@/lib/utils";

type MetricType = "conversions" | "revenue" | "spend" | "clicks";

interface MetricBarChartProps {
  data: Array<{
    id: string;
    name: string;
    conversions: number;
    revenue: number;
    spend: number;
    clicks: number;
  }>;
  title: string;
}

const metrics: { key: MetricType; label: string }[] = [
  { key: "conversions", label: "Conversions" },
  { key: "revenue", label: "Revenue" },
  { key: "spend", label: "Spend" },
  { key: "clicks", label: "Clicks" },
];

export default function MetricBarChart({ data, title }: MetricBarChartProps) {
  const [selectedMetric, setSelectedMetric] =
    useState<MetricType>("conversions");

  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload?.length) return null;

    const data = payload[0].payload;
    return (
      <div className="bg-white border border-slate-200 rounded-lg shadow-lg p-3">
        <p className="text-sm font-medium text-slate-900 mb-2">{data.name}</p>
        <div className="space-y-1 text-xs">
          <div className="flex justify-between gap-4">
            <span className="text-slate-600">Conversions:</span>
            <span className="font-medium text-slate-900">
              {formatNumber(data.conversions)}
            </span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-slate-600">Revenue:</span>
            <span className="font-medium text-slate-900">
              {formatCurrency(data.revenue)}
            </span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-slate-600">Spend:</span>
            <span className="font-medium text-slate-900">
              {formatCurrency(data.spend)}
            </span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-slate-600">Clicks:</span>
            <span className="font-medium text-slate-900">
              {formatNumber(data.clicks)}
            </span>
          </div>
        </div>
      </div>
    );
  };

  const formatYAxis = (value: number) => {
    if (selectedMetric === "revenue" || selectedMetric === "spend") {
      return "$" + (value / 1000).toFixed(0) + "k";
    }
    return formatNumber(value);
  };

  // Check if there is data for the selected metric
  const hasMetricData = data.some((item) => (item[selectedMetric] || 0) > 0);

  // Show completely empty state if no data at all (no rows)
  if (!data || data.length === 0) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
        </div>
        <div className="flex flex-col items-center justify-center py-12 text-center h-[400px] border border-slate-200 rounded-lg">
          <div className="w-16 h-16 mb-4 rounded-full bg-slate-100 flex items-center justify-center">
            <svg
              className="w-8 h-8 text-slate-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
          </div>
          <p className="text-lg font-medium text-slate-900 mb-2">
            No Data Available
          </p>
          <p className="text-sm text-slate-600">
            There is no data to display for this period.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
        <div className="flex items-center gap-2 p-1 bg-slate-100 rounded-lg">
          {metrics.map((metric) => (
            <button
              key={metric.key}
              onClick={() => setSelectedMetric(metric.key)}
              className={cn(
                "px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200",
                selectedMetric === metric.key
                  ? "bg-blue-500 text-white shadow-md"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-200"
              )}
            >
              {metric.label}
            </button>
          ))}
        </div>
      </div>

      <div className="h-[400px] w-full">
        {hasMetricData ? (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={data}
              margin={{ top: 10, right: 10, left: 10, bottom: 60 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#e2e8f0"
                opacity={0.5}
              />
              <XAxis
                dataKey="name"
                stroke="#64748b"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis
                stroke="#64748b"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                tickFormatter={formatYAxis}
              />
              <Tooltip
                content={<CustomTooltip />}
                cursor={{ fill: "#f1f5f9" }}
              />
              <Bar
                dataKey={selectedMetric}
                fill="#3b82f6"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex flex-col items-center justify-center h-full border border-dashed border-slate-200 rounded-lg bg-slate-50/50">
            <div className="w-12 h-12 mb-3 rounded-full bg-slate-100 flex items-center justify-center">
              <svg
                className="w-6 h-6 text-slate-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <p className="font-medium text-slate-900">
              No {metrics.find((m) => m.key === selectedMetric)?.label} Data
            </p>
            <p className="text-sm text-slate-500">
              Try selecting a different metric.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
