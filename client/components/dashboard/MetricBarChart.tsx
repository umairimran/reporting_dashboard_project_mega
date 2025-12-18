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
import { cn } from "@/lib/utils";
import { formatCurrency, formatNumber } from "@/lib/mock-data";

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
                  ? "bg-amber-500 text-white shadow-md"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-200"
              )}
            >
              {metric.label}
            </button>
          ))}
        </div>
      </div>

      <div className="h-[400px] w-full">
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
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "#f1f5f9" }} />
            <Bar
              dataKey={selectedMetric}
              fill="#f59e0b"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
