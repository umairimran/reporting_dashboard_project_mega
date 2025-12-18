"use client";

import { useState, useMemo } from "react";
import {
  ChevronUp,
  ChevronDown,
  ChevronsUpDown,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { formatCurrency, formatNumber, formatPercent } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

type SortDirection = "asc" | "desc" | null;

interface Column {
  key: string;
  label: string;
  format?: "currency" | "number" | "percent" | "text";
}

interface DataTableProps {
  data: Array<Record<string, any>>;
  columns: Column[];
  pageSize?: number;
}

export default function DataTable({
  data,
  columns,
  pageSize = 10,
}: DataTableProps) {
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>(null);
  const [currentPage, setCurrentPage] = useState(1);

  const handleSort = (columnKey: string) => {
    if (sortColumn === columnKey) {
      if (sortDirection === "asc") {
        setSortDirection("desc");
      } else if (sortDirection === "desc") {
        setSortDirection(null);
        setSortColumn(null);
      } else {
        setSortDirection("asc");
      }
    } else {
      setSortColumn(columnKey);
      setSortDirection("asc");
    }
    setCurrentPage(1); // Reset to first page on sort
  };

  const sortedData = useMemo(() => {
    if (!sortColumn || !sortDirection) return data;

    return [...data].sort((a, b) => {
      const aValue = a[sortColumn];
      const bValue = b[sortColumn];

      if (typeof aValue === "number" && typeof bValue === "number") {
        return sortDirection === "asc" ? aValue - bValue : bValue - aValue;
      }

      const aStr = String(aValue).toLowerCase();
      const bStr = String(bValue).toLowerCase();
      return sortDirection === "asc"
        ? aStr.localeCompare(bStr)
        : bStr.localeCompare(aStr);
    });
  }, [data, sortColumn, sortDirection]);

  const totalPages = Math.ceil(sortedData.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const paginatedData = sortedData.slice(startIndex, endIndex);

  const formatValue = (value: any, format?: string) => {
    if (value === null || value === undefined) return "-";

    switch (format) {
      case "currency":
        return formatCurrency(value);
      case "number":
        return formatNumber(value);
      case "percent":
        return formatPercent(value);
      default:
        return String(value);
    }
  };

  const getSortIcon = (columnKey: string) => {
    if (sortColumn !== columnKey) {
      return <ChevronsUpDown className="w-4 h-4 text-slate-400" />;
    }
    if (sortDirection === "asc") {
      return <ChevronUp className="w-4 h-4 text-blue-600" />;
    }
    return <ChevronDown className="w-4 h-4 text-blue-600" />;
  };

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  className="text-left text-xs font-bold text-slate-900 uppercase tracking-wide px-4 py-3 border-b border-slate-200"
                >
                  <button
                    onClick={() => handleSort(column.key)}
                    className="flex items-center gap-2 hover:text-blue-600 transition-colors"
                  >
                    {column.label}
                    {getSortIcon(column.key)}
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody
            style={{
              minHeight: `${pageSize * 49}px`,
              display: "table-row-group",
            }}
          >
            {paginatedData.map((row, index) => (
              <tr
                key={row.id || index}
                className="border-b border-slate-200 hover:bg-slate-50 transition-colors"
              >
                {columns.map((column) => (
                  <td
                    key={column.key}
                    className={cn(
                      "px-4 py-3 text-sm",
                      column.format === "currency" || column.format === "number"
                        ? "font-mono text-slate-900"
                        : "text-slate-900"
                    )}
                  >
                    {formatValue(row[column.key], column.format)}
                  </td>
                ))}
              </tr>
            ))}
            {/* Add empty rows to maintain consistent height */}
            {Array.from({ length: pageSize - paginatedData.length }).map(
              (_, i) => (
                <tr key={`empty-${i}`} style={{ height: "49px" }}>
                  {columns.map((column) => (
                    <td key={column.key} className="px-4 py-3"></td>
                  ))}
                </tr>
              )
            )}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-4 border-t border-slate-200">
          <p className="text-sm text-slate-600">
            Showing {startIndex + 1} to {Math.min(endIndex, sortedData.length)}{" "}
            of {sortedData.length} results
          </p>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
            >
              <ChevronLeft className="w-4 h-4 mr-1" />
              Previous
            </Button>
            <div className="flex items-center gap-1">
              {Array.from({ length: totalPages }, (_, i) => i + 1).map(
                (page) => (
                  <Button
                    key={page}
                    variant={currentPage === page ? "default" : "outline"}
                    size="sm"
                    onClick={() => setCurrentPage(page)}
                    className={cn(
                      "w-8 h-8 p-0",
                      currentPage === page && "bg-blue-600 hover:bg-blue-700"
                    )}
                  >
                    {page}
                  </Button>
                )
              )}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
            >
              Next
              <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
