"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { Button } from "./button";

interface CustomCalendarProps {
  mode?: "single" | "range";
  selected?: Date | { from?: Date; to?: Date };
  onSelect?: (date: Date | { from?: Date; to?: Date } | undefined) => void;
  numberOfMonths?: number;
  className?: string;
  defaultMonth?: Date;
  forceSelection?: "start" | "end";
}

export function CustomCalendar({
  mode = "single",
  selected,
  onSelect,
  numberOfMonths = 1,
  className,
  defaultMonth,
  forceSelection,
}: CustomCalendarProps) {
  const [currentMonth, setCurrentMonth] = useState(defaultMonth || new Date());

  useEffect(() => {
    if (defaultMonth) {
      setCurrentMonth(defaultMonth);
    }
  }, [defaultMonth]);

  // ... (lines 28-93 skipped)

  // Helper functions for date calculations (assuming these were in the skipped section)
  // These are placeholder implementations as the original functions were not provided.
  // The user's instruction implies these functions exist and need modification.
  const isSameDay = (d1: Date, d2: Date) => d1.toDateString() === d2.toDateString();
  const isToday = (date: Date) => isSameDay(date, new Date());
  const isFuture = (date: Date) => date.getTime() > new Date().setHours(0, 0, 0, 0);

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDayOfMonth = new Date(year, month, 1);
    const lastDayOfMonth = new Date(year, month + 1, 0);
    const days = [];

    // Add leading empty days for alignment
    const startDay = firstDayOfMonth.getDay(); // 0 for Sunday, 1 for Monday, etc.
    for (let i = 0; i < startDay; i++) {
      days.push(null);
    }

    // Add days of the month
    for (let i = 1; i <= lastDayOfMonth.getDate(); i++) {
      days.push(new Date(year, month, i));
    }
    return days;
  };

  const daysOfWeek = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  const isInRange = (date: Date | null) => {
    if (!date || mode !== "range" || typeof selected !== "object") return false;
    const range = (selected as any) || {};
    if (!range.from || !range.to) return false;
    return date >= range.from && date <= range.to;
  };

  const isRangeStart = (date: Date | null) => {
    if (!date || mode !== "range" || typeof selected !== "object") return false;
    const range = (selected as any) || {};
    return range.from && isSameDay(date, range.from);
  };

  const isRangeEnd = (date: Date | null) => {
    if (!date || mode !== "range" || typeof selected !== "object") return false;
    const range = (selected as any) || {};
    return range.to && isSameDay(date, range.to);
  };

  const handleDayClick = (date: Date) => {
    // Prevent selecting future dates
    if (isFuture(date)) return;

    if (mode === "single") {
      onSelect?.(date);
    } else if (mode === "range") {
      const range = (selected as { from?: Date; to?: Date }) || {};

      if (forceSelection === "start") {
        // Strict Start Date Selection
        // If the new start date is after the current end date, we must reset the end date
        // because a range cannot start after it ends.
        const newTo = range.to && date > range.to ? undefined : range.to;
        onSelect?.({ from: date, to: newTo });
        return;
      }

      if (forceSelection === "end") {
        // Strict End Date Selection
        // If the new end date is before the current start date, we must reset the start date
        // because a range cannot end before it starts.
        const newFrom = range.from && date < range.from ? undefined : range.from;
        onSelect?.({ from: newFrom, to: date });
        return;
      }

      if (!range.from || !range.to) {
        // First click or completing the range
        if (!range.from) {
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
      } else {
        // Both dates are set - adjust the nearest boundary
        const clickedTime = date.getTime();
        const fromTime = range.from.getTime();
        const toTime = range.to.getTime();

        const distanceToFrom = Math.abs(clickedTime - fromTime);
        const distanceToTo = Math.abs(clickedTime - toTime);

        if (distanceToFrom < distanceToTo) {
          // Closer to 'from' - move 'from' boundary
          if (date <= range.to) {
            onSelect?.({ from: date, to: range.to });
          } else {
            // Clicked after 'to', swap them
            onSelect?.({ from: range.to, to: date });
          }
        } else {
          // Closer to 'to' - move 'to' boundary
          if (date >= range.from) {
            onSelect?.({ from: range.from, to: date });
          } else {
            // Clicked before 'from', swap them
            onSelect?.({ from: date, to: range.from });
          }
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
              mode === "single" && day && isSameDay(day, selected as any);
            const inRange = isInRange(day);
            const rangeStart = isRangeStart(day);
            const rangeEnd = isRangeEnd(day);
            const futureDate = day ? isFuture(day) : false;

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
                    disabled={futureDate}
                    className={cn(
                      "h-9 w-9 rounded-md text-sm font-normal transition-colors",
                      futureDate
                        ? "text-slate-300 cursor-not-allowed hover:bg-transparent"
                        : "hover:bg-slate-100",
                      isSelected || rangeStart || rangeEnd
                        ? "bg-blue-600 text-white hover:bg-blue-600"
                        : isToday(day)
                          ? "bg-slate-100 font-semibold"
                          : futureDate
                            ? "text-slate-300"
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
