import { cn } from "@/lib/utils";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";

interface KPICardProps {
  title: string;
  value: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
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

  const renderTrend = () => {
    if (!trend) return null;

    // isPositive means the number went UP (e.g. +10%).
    // For normal metrics (Revenue), Up = Good (Green).
    // For inverted metrics (CPA), Up = Bad (Red).
    // Wait, let's align with the caller:
    // in page.tsx: "isPositive" meant "Is Good".
    // Let's check page.tsx logic:
    // calcTrend returns: { value: abs(change), isPositive: isPos }
    // where isPos is TRUE if it's "Good" (e.g. Revenue UP, CPA DOWN).

    // So here:
    // isPositive = Good = Green.
    // !isPositive = Bad = Red.

    const isGood = trend.isPositive;
    const colorClass = isGood ? "text-emerald-600 bg-emerald-50" : "text-rose-600 bg-rose-50";
    const ArrowIcon = isGood ? ArrowUpRight : ArrowDownRight; // Visual up/down?

    // Problem: "isPositive" in page.tsx means "Good outcome", not "Numeric Increase".
    // But we need to know if it's an Increase or Decrease to pick the Arrow.
    // The current page.tsx logic obscures the Direction.
    // Let's adjust page.tsx logic? 
    // Actually, simpler:
    // If I only have "Good/Bad" and "Value", I can't strictly show Up/Down arrows accurately without knowing direction.
    // BUT the user asked for "change from previous".
    // If I blindly trust page.tsx, I might show an Up arrow for a CPA decrease if I associate Green with Up.

    // RE-READ page.tsx logic carefully:
    // const calcTrend = (curr, prev, inverse) => {
    //    const change = ((curr - prev) / prev) * 100;
    //    const isPos = inverse ? change <= 0 : change >= 0; 
    //    return { value: Math.abs(change), isPositive: isPos, hasData: true };
    // };

    // I only receive `value` (absolute %) and `isPositive` (Good/Bad).
    // I DO NOT know if it went up or down numerically.
    // This is a flaw in my page.tsx implementation if I want Up/Down arrows.

    // FIX: I will ASSUME for now that:
    // If Normal Metric + Good -> Increased -> Up Arrow
    // If Normal Metric + Bad -> Decreased -> Down Arrow
    // If Inverted Metric + Good -> Decreased -> Down Arrow
    // If Inverted Metric + Bad -> Increased -> Up Arrow

    let isUp = isGood; // default
    if (invertTrend) {
      // If inverted (CPA) and Good (Cost Down), then isUp should be False (Down Arrow).
      isUp = !isGood;
    }

    const DisplayIcon = isUp ? ArrowUpRight : ArrowDownRight;

    return (
      <div className={cn("flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full", colorClass)}>
        <DisplayIcon className="w-3 h-3" />
        <span>{trend.value.toFixed(1)}%</span>
      </div>
    );
  };

  return (
    <div
      className="relative rounded-xl bg-white border border-slate-100 shadow-sm p-6 opacity-0 animate-[slideUp_0.5s_ease-out_forwards] hover:shadow-md transition-shadow duration-300"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="p-3 rounded-xl bg-blue-50 text-blue-600">
          <Icon className="w-5 h-5" />
        </div>
        {renderTrend()}
      </div>

      <div>
        <p className="text-sm font-medium text-slate-500 mb-1">{title}</p>
        <p className="text-2xl font-bold text-slate-900 tracking-tight">{value}</p>
      </div>
    </div>
  );
}
