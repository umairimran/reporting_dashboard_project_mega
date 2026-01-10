"use client";

import { useState } from "react";
import { Calendar, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  format,
  startOfWeek,
  endOfWeek,
  startOfMonth,
  endOfMonth,
  isAfter,
} from "date-fns";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Report } from "@/types/dashboard";
import { useMutation } from "@tanstack/react-query";
import { reportService } from "@/lib/api-client";
import { toast } from "sonner";
import { useAuth } from "@/contexts/AuthContext";

interface GenerateReportDialogProps {
  children: React.ReactNode;
  onReportGenerated?: (report: Report) => void;
  clientId?: string;
}

export default function GenerateReportDialog({
  children,
  onReportGenerated,
  clientId: propClientId,
}: GenerateReportDialogProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [reportType, setReportType] = useState<"weekly" | "monthly">("weekly");
  const [source, setSource] = useState<string>("all");
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [error, setError] = useState<string>("");

  const { user, simulatedClient, isAdmin } = useAuth();

  const { mutate: generateReport, isPending } = useMutation({
    mutationFn: (data: { type: "weekly" | "monthly"; source?: string; periodStart: string; periodEnd: string }) => {
      // Determine client ID
      // Priority: 1. Prop (from Dashboard selection), 2. Simulated (Admin Context), 3. Undefined (Client Context)
      const targetClientId = propClientId || ((isAdmin && simulatedClient?.id) ? simulatedClient.id : undefined);

      return reportService.create({
        ...data,
        clientId: targetClientId
      });
    },
    onSuccess: (data) => {
      toast.success("Report generation started");
      if (onReportGenerated) {
        onReportGenerated(data);
      }
      setIsDialogOpen(false);
      setSelectedDate(null);
      setSource("all");
      setError("");
    },
    onError: (error: Error) => {
      setError(error.message);
      toast.error("Failed to generate report");
    },
  });

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

    // Additional check for admin simulation or selection
    const hasTargetClient = propClientId || simulatedClient;
    if (isAdmin && !hasTargetClient) {
      setError("Please select a client to generate a report for.");
      return;
    }

    generateReport({
      type: reportType,
      source: source === "all" ? undefined : source,
      periodStart: format(periodStart, "yyyy-MM-dd"),
      periodEnd: format(periodEnd, "yyyy-MM-dd"),
    });
  };

  const getPeriodDescription = () => {
    if (!selectedDate) return "No date selected";

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
    <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent className="bg-white max-w-md">
        <DialogHeader>
          <DialogTitle>Generate Report</DialogTitle>
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

          {/* Source Selection */}
          <div>
            <label className="text-sm font-medium text-slate-900 mb-3 block">
              Data Source
            </label>
            <div className="flex items-center gap-2">
              <select
                value={source}
                onChange={(e) => setSource(e.target.value)}
                className="w-full h-10 px-4 rounded-lg border border-slate-200 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
              >
                <option value="all">All Sources (Aggregated)</option>
                <option value="facebook">Facebook</option>
                <option value="surfside">CTV</option>
              </select>
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
              disabled={!selectedDate || isPending}
            >
              {isPending ? "Generating..." : "Generate Report"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
