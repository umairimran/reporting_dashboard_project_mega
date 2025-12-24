"use client";

import { useState, useEffect } from "react";
import {
  Upload,
  RefreshCw,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Clock,
  FileUp,
  Database,
  Loader2,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { ingestionService } from "@/lib/services/ingestion";
import { clientsService } from "@/lib/services/clients";
import { cn } from "@/lib/utils";
import { IngestionStatus } from "@/types/dashboard";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

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

  const { simulatedClient, isAdmin } = useAuth();
  const router = useRouter();
  const queryClient = useQueryClient();

  // Redirect if viewing as client
  useEffect(() => {
    if (simulatedClient && isAdmin) {
      router.push("/dashboard");
    }
  }, [simulatedClient, isAdmin, router]);

  // Fetch Clients for dropdown
  const { data: clientsData } = useQuery({
    queryKey: ["admin", "clients"],
    queryFn: () => clientsService.getClients(0, 100),
  });

  // Fetch Logs
  const { data: logsData, isLoading: isLogsLoading } = useQuery({
    queryKey: ["admin", "logs"],
    queryFn: () => ingestionService.getLogs({ limit: 50 }),
  });

  const getClientName = (clientId?: string) => {
    if (!clientId) return "-";
    const client = clientsData?.clients.find((c) => c.id === clientId);
    return client ? client.name : "Unknown/All";
  };

  // Mutations
  const uploadFacebookMutation = useMutation({
    mutationFn: ({ clientId, file }: { clientId: string; file: File }) =>
      ingestionService.uploadFacebook(clientId, file),
    onSuccess: () => {
      toast.success("Facebook data uploaded successfully");
      resetUploadForm();
      queryClient.invalidateQueries({ queryKey: ["admin", "logs"] });
    },
    onError: (error) => toast.error("Facebook upload failed: " + error),
  });

  const uploadSurfsideMutation = useMutation({
    mutationFn: ({ clientId, file }: { clientId: string; file: File }) =>
      ingestionService.uploadSurfside(clientId, file),
    onSuccess: () => {
      toast.success("Surfside data uploaded successfully");
      resetUploadForm();
      queryClient.invalidateQueries({ queryKey: ["admin", "logs"] });
    },
    onError: (error) => toast.error("Surfside upload failed: " + error),
  });

  const resetUploadForm = () => {
    setSelectedClient("");
    setSelectedSource("");
    setSelectedFile(null);
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
        toast.error("Please upload a CSV or XLSX file");
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
      toast.error("Please select a client");
      return;
    }
    if (!selectedSource) {
      toast.error("Please select a source");
      return;
    }

    if (!selectedFile) {
      toast.error("Please select a file");
      return;
    }

    if (selectedSource === "facebook") {
      uploadFacebookMutation.mutate({
        clientId: selectedClient,
        file: selectedFile,
      });
    } else if (selectedSource === "surfside") {
      uploadSurfsideMutation.mutate({
        clientId: selectedClient,
        file: selectedFile,
      });
    }
  };

  const isUploading =
    uploadFacebookMutation.isPending || uploadSurfsideMutation.isPending;

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex flex-col gap-1 mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Data Ingestion</h1>
        <p className="text-slate-600">
          Configure data sources and monitor ingestion status
        </p>
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
        <div className="space-y-4 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
          <div className="flex justify-end">
            <Button
              variant="gold"
              className="gap-2"
              onClick={() =>
                queryClient.invalidateQueries({ queryKey: ["admin", "logs"] })
              }
              disabled={isLogsLoading}
            >
              <RefreshCw
                className={cn("w-4 h-4", isLogsLoading && "animate-spin")}
              />
              Refresh Logs
            </Button>
          </div>
          <div className="bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl overflow-hidden">
            {isLogsLoading ? (
              <div className="p-8 text-center text-slate-500">
                Loading logs...
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent border-b border-slate-200">
                    <TableHead className="text-left text-xs font-bold text-slate-900 uppercase tracking-wide px-4 py-3 h-auto">
                      Date
                    </TableHead>
                    <TableHead className="text-left text-xs font-bold text-slate-900 uppercase tracking-wide px-4 py-3 h-auto">
                      Status
                    </TableHead>
                    <TableHead className="text-left text-xs font-bold text-slate-900 uppercase tracking-wide px-4 py-3 h-auto">
                      Source
                    </TableHead>
                    <TableHead className="text-left text-xs font-bold text-slate-900 uppercase tracking-wide px-4 py-3 h-auto">
                      Client
                    </TableHead>
                    <TableHead className="text-left text-xs font-bold text-slate-900 uppercase tracking-wide px-4 py-3 h-auto">
                      Records
                    </TableHead>
                    <TableHead className="text-left text-xs font-bold text-slate-900 uppercase tracking-wide px-4 py-3 h-auto">
                      Message
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {logsData?.logs.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} className="h-48">
                        <div className="flex flex-col items-center justify-center text-center py-8">
                          <div className="w-16 h-16 mb-4 rounded-full bg-slate-100 flex items-center justify-center">
                            <Database className="w-8 h-8 text-slate-400" />
                          </div>
                          <p className="text-lg font-medium text-slate-900 mb-2">
                            No Ingestion Logs Available
                          </p>
                          <p className="text-sm text-slate-600">
                            There are no data ingestion logs to display at this
                            time.
                          </p>
                          <p className="text-sm text-slate-600 mt-1">
                            Upload a file to get started.
                          </p>
                        </div>
                      </TableCell>
                    </TableRow>
                  ) : (
                    logsData?.logs.map((log: any, index: number) => {
                      const config =
                        statusConfig[log.status as IngestionStatus] ||
                        statusConfig.processing;
                      const StatusIcon = config.icon;

                      return (
                        <TableRow
                          key={log.id}
                          className="opacity-0 animate-[fadeIn_0.5s_ease-out_forwards] border-b border-slate-200 hover:bg-slate-100/50 transition-colors"
                          style={{ animationDelay: `${index * 30}ms` }}
                        >
                          <TableCell className="text-sm px-4 py-3">
                            {new Date(
                              log.run_date || log.runDate
                            ).toLocaleDateString()}
                          </TableCell>
                          <TableCell className="px-4 py-3">
                            <div
                              className={cn(
                                "flex items-center gap-2",
                                config.color
                              )}
                            >
                              <StatusIcon className="w-4 h-4" />
                              <span className="text-sm font-medium">
                                {config.label}
                              </span>
                            </div>
                          </TableCell>
                          <TableCell className="px-4 py-3">
                            <span className="text-sm text-slate-900 capitalize">
                              {log.source}
                            </span>
                          </TableCell>
                          <TableCell className="text-sm text-slate-600 px-4 py-3">
                            {getClientName(log.client_id || log.clientId)}
                          </TableCell>
                          <TableCell className="font-mono text-sm px-4 py-3">
                            <span className="text-green-400">
                              {(
                                log.records_loaded ||
                                log.recordsLoaded ||
                                0
                              ).toLocaleString()}
                            </span>
                            {(log.records_failed || log.recordsFailed) > 0 && (
                              <span className="text-red-400 ml-1">
                                / -{log.records_failed || log.recordsFailed}
                              </span>
                            )}
                          </TableCell>
                          <TableCell className="text-sm text-muted-foreground max-w-50 truncate px-4 py-3">
                            {log.error_message || log.message || "-"}
                          </TableCell>
                        </TableRow>
                      );
                    })
                  )}
                </TableBody>
              </Table>
            )}
          </div>
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
                Manual Data Actions
              </h2>
              <p className="text-sm text-slate-600">
                Upload historical data for clients
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
                {clientsData?.clients.map((client) => (
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
                <option value="facebook">Facebook (Upload)</option>
                <option value="surfside">Surfside (Upload)</option>
              </select>
            </div>
          </div>

          <>
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
                <strong className="text-slate-900">Supported formats:</strong>{" "}
                CSV and XLSX files with columns matching your data source
                schema. Maximum file size: 50MB
              </p>
            </div>

            <div className="mt-6 flex justify-end">
              <Button
                onClick={handleUpload}
                disabled={
                  !selectedClient ||
                  !selectedSource ||
                  !selectedFile ||
                  isUploading
                }
                className={cn(
                  "gap-2 cursor-pointer",
                  (!selectedClient || !selectedSource || !selectedFile) &&
                    "opacity-50 cursor-not-allowed"
                )}
              >
                {isUploading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Upload className="w-4 h-4" />
                )}
                {isUploading ? "Uploading..." : "Upload File"}
              </Button>
            </div>
          </>
        </div>
      )}
    </div>
  );
}
