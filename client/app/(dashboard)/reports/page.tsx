"use client";

import { useState } from "react";
import {
  FileText,
  Download,
  Calendar,
  CheckCircle2,
  Clock,
  Filter,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { mockReports } from "@/lib/mock-data";
import { cn } from "@/lib/utils";
import { format, parseISO } from "date-fns";

export default function Reports() {
  const [filterType, setFilterType] = useState<"all" | "weekly" | "monthly">(
    "all"
  );

  const filteredReports =
    filterType === "all"
      ? mockReports
      : mockReports.filter((r) => r.type === filterType);

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

        <Button variant="gold" className="gap-2">
          <FileText className="w-4 h-4" />
          Generate Report
        </Button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2 mb-8">
        <div className="flex items-center gap-2 p-1 bg-gray-100 rounded-xl">
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
                  ? "bg-amber-500 text-white shadow-lg"
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
        <div className="text-center py-12">
          <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium text-slate-900 mb-2">
            No reports found
          </h3>
          <p className="text-muted-foreground">
            Try adjusting your filters or generate a new report.
          </p>
        </div>
      )}
    </div>
  );
}
