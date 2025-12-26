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
  XCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { format, parseISO } from "date-fns";
import { Report } from "@/types/dashboard";
import { useAuth } from "@/contexts/AuthContext";
import GenerateReportDialog from "./GenerateReportDialog";
import { useQuery } from "@tanstack/react-query";
import { reportService } from "@/lib/api-client";
import { toast } from "sonner";

export default function Reports() {
  const [filterType, setFilterType] = useState<"all" | "weekly" | "monthly">(
    "all"
  );

  const { isAdmin, simulatedClient } = useAuth();
  // If admin is simulating, pass the client ID. Otherwise undefined (backend handles logic for client user)
  const targetClientId = (isAdmin && simulatedClient) ? simulatedClient.id : undefined;

  // Fetch reports from API
  const {
    data: reports = [],
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["reports", targetClientId],
    queryFn: () => reportService.getAll(targetClientId),
    refetchInterval: (query) => {
      // Poll if any report is generating
      const hasGenerating = query.state.data?.some(
        (r: Report) => r.status === "generating"
      );
      // Poll every 3 seconds if generating, otherwise stop polling
      return hasGenerating ? 3000 : false;
    },
  });

  const filteredReports =
    filterType === "all"
      ? reports
      : reports.filter((r: Report) => r.type === filterType);

  const handleDownload = async (report: Report, fileType: "pdf" | "csv") => {
    try {
      const ext = fileType === "pdf" ? "pdf" : "csv";
      await reportService.download(
        report.id,
        `${report.type}_report_${report.periodStart}.${ext}`,
        fileType
      );
      toast.success("Download started");
    } catch (error) {
      toast.error("Download failed");
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

        <GenerateReportDialog onReportGenerated={() => refetch()}>
          <Button
            variant="default"
            className="gap-2 bg-blue-500 hover:bg-blue-600 text-white border-none"
          >
            <FileText className="w-4 h-4" />
            Generate Report
          </Button>
        </GenerateReportDialog>
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
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredReports.map((report: Report, index: number) => (
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
                    report.status === "ready" &&
                    "bg-green-500/20 text-green-400",
                    report.status === "generating" &&
                    "bg-yellow-500/20 text-yellow-400",
                    report.status === "failed" && "bg-red-500/20 text-red-400"
                  )}
                >
                  {report.status === "ready" ? (
                    <CheckCircle2 className="w-3 h-3 mr-1" />
                  ) : report.status === "failed" ? (
                    <XCircle className="w-3 h-3 mr-1" />
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
                  className="flex-1 gap-2 border-red-200 hover:bg-red-50 hover:text-red-600 text-red-500"
                  disabled={report.status !== "ready"}
                  onClick={() => handleDownload(report, "pdf")}
                >
                  <FileText className="w-4 h-4" />
                  PDF
                </Button>

                {/* CSV DOWNLOAD BUTTON DISABLED - To re-enable, uncomment below */}
                {/* <Button
                  variant="outline"
                  size="sm"
                  className="flex-1 gap-2 border-green-200 hover:bg-green-50 hover:text-green-600 text-green-500"
                  disabled={report.status !== "ready"}
                  onClick={() => handleDownload(report, "csv")}
                >
                  <Download className="w-4 h-4" />
                  CSV
                </Button> */}
              </div>

              {/* Error Message Display */}
              {report.status === 'failed' && report.errorMessage && (
                <div className="mt-4 p-3 bg-red-50 border border-red-100 rounded-lg flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-red-600 mt-0.5 shrink-0" />
                  <p className="text-xs text-red-600 break-words">{report.errorMessage}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && filteredReports.length === 0 && (
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
