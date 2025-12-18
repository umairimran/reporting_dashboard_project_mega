"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { Button } from "./button";

interface CustomCalendarProps {
  mode?: "single" | "range";
  selected?: Date | { from?: Date; to?: Date };
  onSelect?: (date: Date | { from?: Date; to?: Date } | undefined) => void;
  numberOfMonths?: number;
  className?: string;
}

export function CustomCalendar({
  mode = "single",
  selected,
  onSelect,
  numberOfMonths = 1,
  className,
}: CustomCalendarProps) {
  const [currentMonth, setCurrentMonth] = useState(new Date());

  const daysOfWeek = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days: (Date | null)[] = [];

    // Add empty cells for days before the month starts
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }

    // Add all days in the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }

    return days;
  };

  const isSameDay = (date1: Date | null, date2: Date | null) => {
    if (!date1 || !date2) return false;
    return (
      date1.getDate() === date2.getDate() &&
      date1.getMonth() === date2.getMonth() &&
      date1.getFullYear() === date2.getFullYear()
    );
  };

  const isToday = (date: Date | null) => {
    if (!date) return false;
    return isSameDay(date, new Date());
  };

  const isInRange = (date: Date | null) => {
    if (!date || mode !== "range" || typeof selected !== "object") return false;
    const range = selected as { from?: Date; to?: Date };
    if (!range.from || !range.to) return false;
    return date >= range.from && date <= range.to;
  };

  const isRangeStart = (date: Date | null) => {
    if (!date || mode !== "range" || typeof selected !== "object") return false;
    const range = selected as { from?: Date; to?: Date };
    return range.from && isSameDay(date, range.from);
  };

  const isRangeEnd = (date: Date | null) => {
    if (!date || mode !== "range" || typeof selected !== "object") return false;
    const range = selected as { from?: Date; to?: Date };
    return range.to && isSameDay(date, range.to);
  };

  const handleDayClick = (date: Date) => {
    if (mode === "single") {
      onSelect?.(date);
    } else if (mode === "range") {
      const range = (selected as { from?: Date; to?: Date }) || {};
      if (!range.from || (range.from && range.to)) {
        // Start new range
        onSelect?.({ from: date, to: undefined });
      } else {
        // Complete the range
        if (date >= range.from) {
          onSelect?.({ from: range.from, to: date });
        } else {
          onSelect?.({ from: date, to: range.from });
        }
      }
    }
  };

  const previousMonth = () => {
    setCurrentMonth(
      new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1)
    );
  };

  const nextMonth = () => {
    setCurrentMonth(
      new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1)
    );
  };

  const renderMonth = (monthOffset: number) => {
    const date = new Date(
      currentMonth.getFullYear(),
      currentMonth.getMonth() + monthOffset,
      1
    );
    const days = getDaysInMonth(date);

    return (
      <div key={monthOffset} className="space-y-4">
        <div className="flex justify-center relative items-center mb-4">
          {monthOffset === 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={previousMonth}
              className="absolute left-1 h-7 w-7 p-0"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
          )}
          <div className="text-sm font-medium text-slate-900">
            {date.toLocaleDateString("en-US", {
              month: "long",
              year: "numeric",
            })}
          </div>
          {monthOffset === numberOfMonths - 1 && (
            <Button
              variant="outline"
              size="sm"
              onClick={nextMonth}
              className="absolute right-1 h-7 w-7 p-0"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          )}
        </div>

        <div className="grid grid-cols-7 gap-1">
          {daysOfWeek.map((day) => (
            <div
              key={day}
              className="text-center text-xs font-normal text-slate-500 h-9 flex items-center justify-center"
            >
              {day}
            </div>
          ))}
          {days.map((day, index) => {
            const isSelected =
              mode === "single" && day && isSameDay(day, selected as Date);
            const inRange = isInRange(day);
            const rangeStart = isRangeStart(day);
            const rangeEnd = isRangeEnd(day);

            return (
              <div
                key={index}
                className={cn(
                  "h-9 flex items-center justify-center",
                  inRange && !rangeStart && !rangeEnd && "bg-blue-50"
                )}
              >
                {day ? (
                  <button
                    onClick={() => handleDayClick(day)}
                    className={cn(
                      "h-9 w-9 rounded-md text-sm font-normal transition-colors",
                      "hover:bg-slate-100",
                      isSelected || rangeStart || rangeEnd
                        ? "bg-blue-600 text-white hover:bg-blue-600"
                        : isToday(day)
                        ? "bg-slate-100 font-semibold"
                        : "text-slate-900"
                    )}
                  >
                    {day.getDate()}
                  </button>
                ) : (
                  <div className="h-9 w-9" />
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className={cn("p-3", className)}>
      <div className="flex gap-4">
        {Array.from({ length: numberOfMonths }).map((_, i) => renderMonth(i))}
      </div>
    </div>
  );
}
