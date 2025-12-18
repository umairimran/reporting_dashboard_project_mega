"use client";

import { useState } from "react";
import { Users, Database } from "lucide-react";
import { cn } from "@/lib/utils";

// Import the content from the clients and ingestion pages
import AdminClients from "./clients/page";
import AdminIngestion from "./ingestion/page";

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState<"clients" | "ingestion">(
    "clients"
  );

  return (
    <div className="flex flex-col h-full">
      {/* Tabs */}
      <div className="bg-white border-b border-slate-200">
        <div className="px-8 pt-6">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveTab("clients")}
              className={cn(
                "flex items-center gap-2 px-4 py-3 border-b-2 text-sm font-medium transition-all duration-200",
                activeTab === "clients"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300"
              )}
            >
              <Users className="w-4 h-4" />
              Clients
            </button>
            <button
              onClick={() => setActiveTab("ingestion")}
              className={cn(
                "flex items-center gap-2 px-4 py-3 border-b-2 text-sm font-medium transition-all duration-200",
                activeTab === "ingestion"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300"
              )}
            >
              <Database className="w-4 h-4" />
              Data Ingestion
            </button>
          </div>
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === "clients" ? <AdminClients /> : <AdminIngestion />}
      </div>
    </div>
  );
}
