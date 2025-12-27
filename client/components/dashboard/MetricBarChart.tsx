"use client";

import { useState, useEffect } from "react";
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
  allowedMetrics?: MetricType[];
  color?: string;
}


const metrics: { key: MetricType; label: string; color: string }[] = [
  { key: "conversions", label: "Conversions", color: "#8b5cf6" }, // Purple
  { key: "revenue", label: "Revenue", color: "#10b981" }, // Green
  { key: "spend", label: "Spend", color: "#3b82f6" }, // Blue
  { key: "clicks", label: "Clicks", color: "#f59e0b" }, // Orange
];

export default function MetricBarChart({ data, title, allowedMetrics, color }: MetricBarChartProps) {
  const availableMetrics = allowedMetrics
    ? metrics.filter(m => allowedMetrics.includes(m.key))
    : metrics;

  // Ensure default selected metric is valid
  const [selectedMetric, setSelectedMetric] =
    useState<MetricType>(availableMetrics[0]?.key || "conversions");

  // Update selected metric if it becomes unavailable when allowedMetrics changes
  useEffect(() => {
    if (availableMetrics.length > 0 && !availableMetrics.find(m => m.key === selectedMetric)) {
      setSelectedMetric(availableMetrics[0].key);
    }
  }, [allowedMetrics, selectedMetric]);



  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload?.length) return null;

    const data = payload[0].payload;
    return (
      <div className="bg-white border border-slate-200 rounded-lg shadow-lg p-3">
        <p className="text-sm font-medium text-slate-900 mb-2">{data.name}</p>
        <div className="space-y-1 text-xs">
          {availableMetrics.map((metric) => (
            <div key={metric.key} className="flex justify-between gap-4">
              <span className="text-slate-600">{metric.label}:</span>
              <span className="font-medium text-slate-900">
                {metric.key === "revenue" || metric.key === "spend"
                  ? formatCurrency(data[metric.key])
                  : formatNumber(data[metric.key])}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const formatYAxis = (value: number) => {
    if (selectedMetric === "revenue" || selectedMetric === "spend") {
      if (value >= 1000) {
        return "$" + (value / 1000).toFixed(0) + "k";
      }
      return "$" + formatNumber(value);
    }
    return formatNumber(value);
  };

  // Custom tick component to wrap long text
  const CustomXAxisTick = ({ x, y, payload }: any) => {
    const text = payload.value || "";
    const maxCharsPerLine = 15; // Maximum characters per line
    
    // Split text into words
    const words = text.split(" ");
    const lines: string[] = [];
    let currentLine = "";

    words.forEach((word: string) => {
      const testLine = currentLine ? `${currentLine} ${word}` : word;
      if (testLine.length > maxCharsPerLine && currentLine) {
        lines.push(currentLine);
        currentLine = word;
      } else {
        currentLine = testLine;
      }
    });
    
    if (currentLine) {
      lines.push(currentLine);
    }

    return (
      <g transform={`translate(${x},${y})`}>
        {lines.map((line, index) => (
          <text
            key={index}
            x={0}
            y={0}
            dy={index * 14 + 10}
            textAnchor="middle"
            fill="#64748b"
            fontSize={11}
            fontWeight={400}
          >
            {line}
          </text>
        ))}
      </g>
    );
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
          {availableMetrics.map((metric) => (
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
                height={100}
                tick={<CustomXAxisTick />}
                interval={0}
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
                fill={
                  color ||
                  availableMetrics.find((m) => m.key === selectedMetric)
                    ?.color || "#3b82f6"
                }
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
              No {availableMetrics.find((m) => m.key === selectedMetric)?.label} Data
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
