"use client";

import { useState } from "react";
import {
  Upload,
  RefreshCw,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Clock,
  Cloud,
  FileUp,
  Database,
  MonitorPlay,
  Trash2,
} from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { mockIngestionLogs, mockClients } from "@/lib/mock-data";
import { cn } from "@/lib/utils";
import { IngestionStatus } from "@/types/dashboard";

const statusConfig: Record<
  IngestionStatus,
  { icon: typeof CheckCircle2; color: string; label: string }
> = {
  success: { icon: CheckCircle2, color: "text-green-400", label: "Success" },
  failed: { icon: XCircle, color: "text-red-400", label: "Failed" },
  partial: { icon: AlertCircle, color: "text-yellow-400", label: "Partial" },
  processing: { icon: Clock, color: "text-blue-400", label: "Processing" },
};

export default function AdminIngestion() {
  const [activeTab, setActiveTab] = useState<"logs" | "upload">("logs");
  const [selectedClient, setSelectedClient] = useState<string>("");
  const [selectedSource, setSelectedSource] = useState<string>("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const getClientName = (clientId?: string) => {
    if (!clientId) return "All Clients";
    return mockClients.find((c) => c.id === clientId)?.name || "Unknown";
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.name.endsWith(".csv") || file.name.endsWith(".xlsx")) {
        setSelectedFile(file);
      } else {
        alert("Please upload a CSV or XLSX file");
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      setSelectedFile(files[0]);
    }
  };

  const handleUpload = () => {
    if (!selectedClient) {
      alert("Please select a client");
      return;
    }
    if (!selectedSource) {
      alert("Please select a source");
      return;
    }
    if (!selectedFile) {
      alert("Please select a file");
      return;
    }

    // Simulate upload
    alert(
      `Uploading ${selectedFile.name} for ${getClientName(
        selectedClient
      )} from ${selectedSource} source`
    );

    // Reset form
    setSelectedClient("");
    setSelectedSource("");
    setSelectedFile(null);
  };

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Data Ingestion</h1>
          <p className="text-slate-600">
            Configure data sources and monitor ingestion status
          </p>
        </div>

        {/* <Button variant="gold" className="gap-2">
          <RefreshCw className="w-4 h-4" />
          Sync Now
        </Button> */}
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 p-1 bg-slate-100 rounded-xl mb-8 w-fit">
        {[
          { id: "logs", label: "Ingestion Logs", icon: Database },
          { id: "upload", label: "Manual Upload", icon: FileUp },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer",
              activeTab === tab.id
                ? "bg-blue-500 text-white shadow-lg"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-200"
            )}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Logs Tab */}
      {activeTab === "logs" && (
        <div className="bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl overflow-hidden opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent border-b border-slate-200">
                <TableHead className="text-left text-xs font-medium text-slate-600 uppercase tracking-wide px-4 py-3 h-auto">
                  Date
                </TableHead>
                <TableHead className="text-left text-xs font-medium text-slate-600 uppercase tracking-wide px-4 py-3 h-auto">
                  Status
                </TableHead>
                <TableHead className="text-left text-xs font-medium text-slate-600 uppercase tracking-wide px-4 py-3 h-auto">
                  Source
                </TableHead>
                <TableHead className="text-left text-xs font-medium text-slate-600 uppercase tracking-wide px-4 py-3 h-auto">
                  Client
                </TableHead>
                <TableHead className="text-left text-xs font-medium text-slate-600 uppercase tracking-wide px-4 py-3 h-auto">
                  Records
                </TableHead>
                <TableHead className="text-left text-xs font-medium text-slate-600 uppercase tracking-wide px-4 py-3 h-auto">
                  Message
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {mockIngestionLogs.map((log, index) => {
                const config = statusConfig[log.status];
                const StatusIcon = config.icon;

                return (
                  <TableRow
                    key={log.id}
                    className="opacity-0 animate-[fadeIn_0.5s_ease-out_forwards] border-b border-slate-200 hover:bg-slate-100/50 transition-colors"
                    style={{ animationDelay: `${index * 30}ms` }}
                  >
                    <TableCell className="text-sm px-4 py-3">
                      {log.runDate}
                    </TableCell>
                    <TableCell className="px-4 py-3">
                      <div
                        className={cn("flex items-center gap-2", config.color)}
                      >
                        <StatusIcon className="w-4 h-4" />
                        <span className="text-sm font-medium">
                          {config.label}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell className="px-4 py-3">
                      <span
                        className={cn(
                          "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize",
                          log.source === "surfside" &&
                            "bg-green-500/20 text-green-400",
                          log.source === "facebook" &&
                            "bg-blue-500/20 text-blue-400",
                          log.source === "vibe" &&
                            "bg-purple-500/20 text-purple-400"
                        )}
                      >
                        {log.source}
                      </span>
                    </TableCell>
                    <TableCell className="text-sm text-slate-600 px-4 py-3">
                      {getClientName(log.clientId)}
                    </TableCell>
                    <TableCell className="font-mono text-sm px-4 py-3">
                      <span className="text-green-400">
                        {log.recordsLoaded.toLocaleString()}
                      </span>
                      {log.recordsFailed > 0 && (
                        <span className="text-red-400 ml-1">
                          / -{log.recordsFailed}
                        </span>
                      )}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground max-w-50 truncate px-4 py-3">
                      {log.message}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Manual Upload Tab */}
      {activeTab === "upload" && (
        <div className="bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center">
              <Upload className="w-6 h-6 text-amber-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-900">
                Manual File Upload
              </h2>
              <p className="text-sm text-slate-600">
                Upload historical data or backfill missing records
              </p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6 mb-6">
            {/* Client Selector */}
            <div>
              <label className="text-sm font-medium text-slate-900 block mb-2">
                Select Client <span className="text-red-500">*</span>
              </label>
              <select
                value={selectedClient}
                onChange={(e) => setSelectedClient(e.target.value)}
                className="w-full h-10 px-4 rounded-lg border border-slate-200 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-amber-500/30 cursor-pointer"
              >
                <option value="">Choose a client...</option>
                {mockClients.map((client) => (
                  <option key={client.id} value={client.id}>
                    {client.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Source Selector */}
            <div>
              <label className="text-sm font-medium text-slate-900 block mb-2">
                Select Source <span className="text-red-500">*</span>
              </label>
              <select
                value={selectedSource}
                onChange={(e) => setSelectedSource(e.target.value)}
                className="w-full h-10 px-4 rounded-lg border border-slate-200 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-amber-500/30 cursor-pointer"
              >
                <option value="">Choose a source...</option>
                <option value="facebook">Facebook</option>
                <option value="vibe">Vibe</option>
                <option value="surfside">Surfside</option>
              </select>
            </div>
          </div>

          {/* File Upload Area */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={cn(
              "border-2 border-dashed rounded-xl p-12 text-center transition-all cursor-pointer",
              isDragging
                ? "border-amber-500 bg-amber-50"
                : "border-slate-200 hover:border-amber-400 hover:bg-slate-50"
            )}
            onClick={() => document.getElementById("file-upload")?.click()}
          >
            <input
              id="file-upload"
              type="file"
              accept=".csv,.xlsx"
              onChange={handleFileSelect}
              className="hidden"
            />

            {selectedFile ? (
              <div className="flex flex-col items-center">
                <CheckCircle2 className="w-12 h-12 text-green-500 mb-4" />
                <p className="text-slate-900 font-medium mb-2">
                  {selectedFile.name}
                </p>
                <p className="text-sm text-slate-600 mb-4">
                  {(selectedFile.size / 1024).toFixed(2)} KB
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedFile(null);
                  }}
                >
                  Remove File
                </Button>
              </div>
            ) : (
              <>
                <Upload className="w-12 h-12 text-slate-400 mx-auto mb-4" />
                <p className="text-slate-900 font-medium mb-2">
                  Drag and drop your file here
                </p>
                <p className="text-sm text-slate-600 mb-4">
                  or click to browse files
                </p>
                <Button variant="outline">Select File</Button>
              </>
            )}
          </div>

          <div className="mt-6 p-4 rounded-lg bg-slate-100">
            <p className="text-sm text-slate-600">
              <strong className="text-slate-900">Supported formats:</strong> CSV
              and XLSX files with columns matching your data source schema.
              Maximum file size: 50MB
            </p>
          </div>

          <div className="mt-6 flex justify-end">
            <Button
              onClick={handleUpload}
              disabled={!selectedClient || !selectedSource || !selectedFile}
              className={cn(
                "gap-2 cursor-pointer",
                (!selectedClient || !selectedSource || !selectedFile) &&
                  "opacity-50 cursor-not-allowed"
              )}
            >
              <Upload className="w-4 h-4" />
              Upload File
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
