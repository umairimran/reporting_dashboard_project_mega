import { cn } from "@/lib/utils";
import { MetricTrend } from "@/types/dashboard";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface KPICardProps {
  title: string;
  value: string;
  trend: MetricTrend;
  icon: React.ElementType;
  format?: "currency" | "number" | "percent";
  invertTrend?: boolean; // For metrics where down is good (like CPA)
  delay?: number;
}

export default function KPICard({
  title,
  value,
  trend,
  icon: Icon,
  invertTrend = false,
  delay = 0,
}: KPICardProps) {
  const getTrendDescription = () => {
    const direction =
      trend.direction === "up"
        ? "increase"
        : trend.direction === "down"
        ? "decrease"
        : "no change";
    return `${Math.abs(trend.percentChange).toFixed(
      1
    )}% ${direction} from previous period`;
  };

  const showSign = trend.direction !== "flat";
  const sign =
    trend.direction === "up" ? "+" : trend.direction === "down" ? "-" : "";

  return (
    <div
      className="relative rounded-xl bg-gradient-to-b from-white to-slate-50 border border-slate-200 p-6 opacity-0 animate-[slideUp_0.5s_ease-out_forwards]"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="p-2.5 rounded-lg bg-amber-500/10">
          <Icon className="w-5 h-5 text-amber-600" />
        </div>
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="flex items-center gap-1 text-sm font-medium text-slate-600 cursor-help">
              <span>
                {showSign && sign}
                {Math.abs(trend.percentChange).toFixed(1)}%
              </span>
            </div>
          </TooltipTrigger>
          <TooltipContent
            side="top"
            sideOffset={8}
            className="bg-white border border-slate-200 shadow-lg"
          >
            <p className="text-xs text-slate-900">{getTrendDescription()}</p>
          </TooltipContent>
        </Tooltip>
      </div>

      <div>
        <p className="text-sm text-slate-600 mb-1">{title}</p>
        <p className="text-2xl font-bold text-slate-900">{value}</p>
      </div>

      {/* Hover glow effect */}
      <div className="absolute inset-0 opacity-0 hover:opacity-100 transition-opacity duration-300 pointer-events-none bg-[radial-gradient(circle_at_center,rgba(251,191,36,0.08)_0%,transparent_70%)] rounded-xl" />
    </div>
  );
}
