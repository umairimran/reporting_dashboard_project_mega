import { useMemo } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { format, parseISO } from "date-fns";

interface ChartDataPoint {
  date: string;
  spend: number;
  revenue: number;
  impressions: number;
}

interface PerformanceChartProps {
  data: ChartDataPoint[];
  metric?: "spend" | "revenue" | "both";
}

export default function PerformanceChart({
  data,
  metric = "both",
}: PerformanceChartProps) {
  const formattedData = useMemo(() => {
    return data.map((d) => ({
      ...d,
      formattedDate: format(parseISO(d.date), "MMM d"),
    }));
  }, [data]);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload?.length) return null;

    return (
      <div className="bg-white border border-slate-200 rounded-lg shadow-lg p-3">
        <p className="text-xs text-slate-600 mb-2">{label}</p>
        {payload.map((entry: any, index: number) => (
          <div key={index} className="flex items-center gap-2 text-sm">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-slate-600 capitalize">{entry.name}:</span>
            <span className="font-medium text-slate-900">
              {entry.name === "spend" || entry.name === "revenue"
                ? `$${entry.value.toLocaleString()}`
                : entry.value.toLocaleString()}
            </span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={formattedData}
          margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
        >
          <defs>
            <linearGradient id="colorSpend" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" opacity={0.5} />
          <XAxis
            dataKey="formattedDate"
            stroke="#64748b"
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            stroke="#64748b"
            fontSize={12}
            tickLine={false}
            axisLine={false}
            tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="top"
            height={36}
            formatter={(value) => (
              <span className="text-sm capitalize text-slate-600">{value}</span>
            )}
          />
          {(metric === "spend" || metric === "both") && (
            <Area
              type="monotone"
              dataKey="spend"
              stroke="#06b6d4"
              fillOpacity={1}
              fill="url(#colorSpend)"
              strokeWidth={2}
            />
          )}
          {(metric === "revenue" || metric === "both") && (
            <Area
              type="monotone"
              dataKey="revenue"
              stroke="#f59e0b"
              fillOpacity={1}
              fill="url(#colorRevenue)"
              strokeWidth={2}
            />
          )}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
