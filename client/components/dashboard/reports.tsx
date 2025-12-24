"use client";

import { useState } from "react";
import {
  FileText,
  Download,
  Calendar,
  CheckCircle2,
  Clock,
  Filter,
  AlertCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { mockReports } from "@/lib/mock-data";
import { cn } from "@/lib/utils";
import {
  format,
  parseISO,
  startOfWeek,
  endOfWeek,
  startOfMonth,
  endOfMonth,
  isAfter,
  isBefore,
  isSameDay,
  addDays,
} from "date-fns";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Report } from "@/types/dashboard";

export default function Reports() {
  const [filterType, setFilterType] = useState<"all" | "weekly" | "monthly">(
    "all"
  );
  const [reports, setReports] = useState<Report[]>(mockReports);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [reportType, setReportType] = useState<"weekly" | "monthly">("weekly");
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [error, setError] = useState<string>("");

  const filteredReports =
    filterType === "all"
      ? reports
      : reports.filter((r) => r.type === filterType);

  const handleGenerateReport = () => {
    setError("");

    if (!selectedDate) {
      setError("Please select a date");
      return;
    }

    // Validate that the selected date is not in the future
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (isAfter(selectedDate, today)) {
      setError("Cannot generate reports for future dates");
      return;
    }

    let periodStart: Date;
    let periodEnd: Date;

    if (reportType === "weekly") {
      // Week runs from Monday to Sunday
      periodStart = startOfWeek(selectedDate, { weekStartsOn: 1 });
      periodEnd = endOfWeek(selectedDate, { weekStartsOn: 1 });

      // Check if the week has ended
      if (isAfter(periodEnd, today)) {
        setError(
          "Cannot generate report for an incomplete week. Please select a week that has already ended."
        );
        return;
      }
    } else {
      // Monthly report
      periodStart = startOfMonth(selectedDate);
      periodEnd = endOfMonth(selectedDate);

      // Check if the month has ended
      if (isAfter(periodEnd, today)) {
        setError(
          "Cannot generate report for an incomplete month. Please select a month that has already ended."
        );
        return;
      }
    }

    // Check if a report already exists for this period
    const existingReport = reports.find(
      (r) =>
        r.type === reportType &&
        r.periodStart === format(periodStart, "yyyy-MM-dd") &&
        r.periodEnd === format(periodEnd, "yyyy-MM-dd")
    );

    if (existingReport) {
      setError(
        `A ${reportType} report for this period already exists (${format(
          periodStart,
          "MMM d"
        )} - ${format(periodEnd, "MMM d, yyyy")})`
      );
      return;
    }

    // Generate new report
    const newReport: Report = {
      id: Math.random().toString(36).substr(2, 9),
      clientId: "1", // In production, use actual client ID
      type: reportType,
      periodStart: format(periodStart, "yyyy-MM-dd"),
      periodEnd: format(periodEnd, "yyyy-MM-dd"),
      generatedAt: new Date().toISOString(),
      status: "generating",
    };

    // Add to reports list at the beginning
    setReports([newReport, ...reports]);

    // Close dialog and reset form
    setIsDialogOpen(false);
    setSelectedDate(null);
    setError("");

    // Simulate report generation completing after 3 seconds
    setTimeout(() => {
      setReports((prev) =>
        prev.map((r) =>
          r.id === newReport.id ? { ...r, status: "ready" as const } : r
        )
      );
    }, 3000);
  };

  const getPeriodDescription = () => {
    if (!selectedDate) return "No date selected";

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (reportType === "weekly") {
      const weekStart = startOfWeek(selectedDate, { weekStartsOn: 1 });
      const weekEnd = endOfWeek(selectedDate, { weekStartsOn: 1 });
      return `${format(weekStart, "MMM d")} - ${format(
        weekEnd,
        "MMM d, yyyy"
      )}`;
    } else {
      const monthStart = startOfMonth(selectedDate);
      const monthEnd = endOfMonth(selectedDate);
      return `${format(monthStart, "MMM d")} - ${format(
        monthEnd,
        "MMM d, yyyy"
      )}`;
    }
  };

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Reports</h1>
          <p className="text-slate-600">
            Access weekly and monthly performance summaries
          </p>
        </div>

        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button variant="gold" className="gap-2">
              <FileText className="w-4 h-4" />
              Generate Report
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-white max-w-md">
            <DialogHeader>
              <DialogTitle>Generate New Report</DialogTitle>
            </DialogHeader>

            <div className="space-y-6 mt-4">
              {/* Report Type Selection */}
              <div>
                <label className="text-sm font-medium text-slate-900 mb-3 block">
                  Report Type
                </label>
                <div className="flex items-center gap-2 p-1 bg-slate-100 rounded-xl">
                  {[
                    { id: "weekly", label: "Weekly" },
                    { id: "monthly", label: "Monthly" },
                  ].map((type) => (
                    <button
                      key={type.id}
                      onClick={() => {
                        setReportType(type.id as "weekly" | "monthly");
                        setSelectedDate(null);
                        setError("");
                      }}
                      className={cn(
                        "flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                        reportType === type.id
                          ? "bg-blue-500 text-white shadow-lg"
                          : "text-slate-600 hover:text-slate-900 hover:bg-slate-200"
                      )}
                    >
                      {type.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Date Selection */}
              <div>
                <label className="text-sm font-medium text-slate-900 mb-2 block">
                  Select {reportType === "weekly" ? "Week" : "Month"}
                </label>
                <input
                  type={reportType === "weekly" ? "date" : "month"}
                  value={
                    selectedDate
                      ? reportType === "weekly"
                        ? format(selectedDate, "yyyy-MM-dd")
                        : format(selectedDate, "yyyy-MM")
                      : ""
                  }
                  onChange={(e) => {
                    if (e.target.value) {
                      setSelectedDate(new Date(e.target.value));
                      setError("");
                    } else {
                      setSelectedDate(null);
                    }
                  }}
                  max={
                    reportType === "weekly"
                      ? format(new Date(), "yyyy-MM-dd")
                      : format(new Date(), "yyyy-MM")
                  }
                  className="w-full h-10 px-4 rounded-lg border border-slate-200 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
                />
                <p className="text-xs text-slate-600 mt-2">
                  {reportType === "weekly"
                    ? "Select any date within the week you want to report"
                    : "Select the month you want to report"}
                </p>
              </div>

              {/* Period Preview */}
              {selectedDate && (
                <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
                  <div className="flex items-center gap-2 text-sm">
                    <Calendar className="w-4 h-4 text-blue-600" />
                    <span className="font-medium text-blue-900">
                      Report Period:
                    </span>
                  </div>
                  <p className="text-sm text-blue-700 mt-1 font-medium">
                    {getPeriodDescription()}
                  </p>
                </div>
              )}

              {/* Error Message */}
              {error && (
                <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
                    <p className="text-sm text-red-700">{error}</p>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-3 pt-2">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => {
                    setIsDialogOpen(false);
                    setSelectedDate(null);
                    setError("");
                  }}
                >
                  Cancel
                </Button>
                <Button
                  variant="default"
                  className="flex-1 bg-blue-600 hover:bg-blue-700"
                  onClick={handleGenerateReport}
                  disabled={!selectedDate}
                >
                  Generate Report
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2 mb-8">
        <div className="flex items-center gap-2 p-1 bg-slate-100 rounded-xl">
          {[
            { id: "all", label: "All Reports" },
            { id: "weekly", label: "Weekly" },
            { id: "monthly", label: "Monthly" },
          ].map((filter) => (
            <button
              key={filter.id}
              onClick={() => setFilterType(filter.id as any)}
              className={cn(
                "px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                filterType === filter.id
                  ? "bg-blue-500 text-white shadow-lg"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-200"
              )}
            >
              {filter.label}
            </button>
          ))}
        </div>
      </div>

      {/* Reports Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredReports.map((report, index) => (
          <div
            key={report.id}
            className="bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[slideUp_0.5s_ease-out_forwards]"
            style={{
              animationDelay: `${index * 50}ms`,
            }}
          >
            <div className="flex items-start justify-between mb-4">
              <div
                className={cn(
                  "p-3 rounded-xl",
                  report.type === "weekly"
                    ? "bg-blue-500/10"
                    : "bg-purple-500/10"
                )}
              >
                <FileText
                  className={cn(
                    "w-6 h-6",
                    report.type === "weekly"
                      ? "text-blue-400"
                      : "text-purple-400"
                  )}
                />
              </div>
              <span
                className={cn(
                  "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize",
                  report.status === "ready" && "bg-green-500/20 text-green-400",
                  report.status === "generating" &&
                    "bg-yellow-500/20 text-yellow-400",
                  report.status === "failed" && "bg-red-500/20 text-red-400"
                )}
              >
                {report.status === "ready" ? (
                  <CheckCircle2 className="w-3 h-3 mr-1" />
                ) : (
                  <Clock className="w-3 h-3 mr-1" />
                )}
                {report.status}
              </span>
            </div>

            <h3 className="text-lg font-semibold text-slate-900 mb-1 capitalize">
              {report.type} Summary
            </h3>

            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
              <Calendar className="w-4 h-4" />
              <span>
                {format(parseISO(report.periodStart), "MMM d")} -{" "}
                {format(parseISO(report.periodEnd), "MMM d, yyyy")}
              </span>
            </div>

            <p className="text-xs text-muted-foreground mb-4">
              Generated: {format(parseISO(report.generatedAt), "MMM d, yyyy")}
            </p>

            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                className="flex-1 gap-2"
                disabled={report.status !== "ready"}
              >
                <Download className="w-4 h-4" />
                PDF
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="flex-1 gap-2"
                disabled={report.status !== "ready"}
              >
                <Download className="w-4 h-4" />
                CSV
              </Button>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredReports.length === 0 && (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <div className="w-16 h-16 mb-4 rounded-full bg-slate-100 flex items-center justify-center">
            <FileText className="w-8 h-8 text-slate-400" />
          </div>
          <p className="text-lg font-medium text-slate-900 mb-2">
            No Reports Available
          </p>
          <p className="text-sm text-slate-600 mb-4">
            {filterType === "all"
              ? "There are no reports to display. Generate a new report to get started."
              : `No ${filterType} reports found. Try adjusting your filters or generate a new report.`}
          </p>
        </div>
      )}
    </div>
  );
}
