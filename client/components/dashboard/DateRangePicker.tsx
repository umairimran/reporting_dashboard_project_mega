import { useState } from "react";
import { Calendar, ChevronDown } from "lucide-react";
import { format } from "date-fns";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { CustomCalendar } from "@/components/ui/custom-calendar";
import { DatePreset, DateRange } from "@/types/dashboard";
import { cn } from "@/lib/utils";

interface DateRangePickerProps {
  dateRange: DateRange;
  onDateRangeChange: (range: DateRange) => void;
}

const presets: { id: DatePreset; label: string; days: number }[] = [
  { id: "last7", label: "Last 7 days", days: 7 },
  { id: "last30", label: "Last 30 days", days: 30 },
  { id: "last90", label: "Last 90 days", days: 90 },
];

export default function DateRangePicker({
  dateRange,
  onDateRangeChange,
}: DateRangePickerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [activePreset, setActivePreset] = useState<DatePreset>("last30");

  const handlePresetClick = (preset: (typeof presets)[0]) => {
    const to = new Date();
    const from = new Date();
    from.setDate(from.getDate() - preset.days);

    setActivePreset(preset.id);
    onDateRangeChange({ from, to });
    setIsOpen(false);
  };

  const handleCustomSelect = (
    range: Date | { from?: Date; to?: Date } | undefined
  ) => {
    if (!range) return;

    // Handle range object
    if (typeof range === "object" && "from" in range) {
      // Update the date range even if only 'from' is set (partial selection)
      setActivePreset("custom");

      // Update the range but keep popover open for further adjustments
      if (range.from && range.to) {
        onDateRangeChange({ from: range.from, to: range.to });
      } else if (range.from) {
        // Only 'from' is set, keep popover open for user to select 'to'
        onDateRangeChange({ from: range.from, to: range.from });
      }
    }
  };

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" className="justify-start gap-2 min-w-[220px]">
          <Calendar className="w-4 h-4 text-slate-600" />
          <span className="text-sm">
            {format(dateRange.from, "MMM d")} -{" "}
            {format(dateRange.to, "MMM d, yyyy")}
          </span>
          <ChevronDown className="w-4 h-4 ml-auto text-slate-600" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="end">
        <div className="flex">
          {/* Presets */}
          <div className="p-3 border-r border-slate-200 space-y-1 bg-white">
            <p className="text-xs font-medium text-slate-600 px-2 pb-2">
              Quick Select
            </p>
            {presets.map((preset) => (
              <button
                key={preset.id}
                onClick={() => handlePresetClick(preset)}
                className={cn(
                  "w-full text-left px-3 py-2 rounded-md text-sm transition-colors",
                  activePreset === preset.id
                    ? "bg-blue-500 text-white"
                    : "hover:bg-slate-100 text-slate-900"
                )}
              >
                {preset.label}
              </button>
            ))}
          </div>

          {/* Calendars Container */}
          <div className="flex divide-x divide-slate-200">
            {/* Start Date Calendar */}
            <div className="p-3 bg-white">
              <div className="text-xs font-semibold text-slate-500 mb-2 px-1">Start Date</div>
              <CustomCalendar
                mode="range"
                selected={{ from: dateRange.from, to: dateRange.to }}
                onSelect={handleCustomSelect}
                numberOfMonths={1}
                defaultMonth={dateRange.from}
                forceSelection="start"
                className="pointer-events-auto"
              />
            </div>

            {/* End Date Calendar */}
            <div className="p-3 bg-white">
              <div className="text-xs font-semibold text-slate-500 mb-2 px-1">End Date</div>
              <CustomCalendar
                mode="range"
                selected={{ from: dateRange.from, to: dateRange.to }}
                onSelect={handleCustomSelect}
                numberOfMonths={1}
                defaultMonth={dateRange.to || dateRange.from || new Date()}
                forceSelection="end"
                className="pointer-events-auto"
              />
            </div>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
