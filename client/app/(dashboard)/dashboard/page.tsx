"use client";

import { useState, useMemo, useEffect } from "react";
import {
  DollarSign,
  TrendingUp,
  Target,
  Eye,
  MousePointer,
  Download,
  RefreshCw,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import KPICard from "@/components/dashboard/KPICard";
import PlatformTabs from "@/components/dashboard/PlatformTabs";
import DateRangePicker from "@/components/dashboard/DateRangePicker";
import PerformanceChart from "@/components/dashboard/PerformanceChart";
import CampaignTable from "@/components/dashboard/CampaignTable";
import { useAuth } from "@/contexts/AuthContext";
import { DataSource, DateRange } from "@/types/dashboard";
import {
  mockClients,
  mockCampaigns,
  mockKPIData,
  mockCampaignPerformance,
  mockStrategyPerformance,
  mockRegionPerformance,
  mockCreativePerformance,
  generateChartData,
  formatCurrency,
  formatNumber,
  filterBySource,
} from "@/lib/mock-data";
import MetricBarChart from "@/components/dashboard/MetricBarChart";
import DataTable from "@/components/dashboard/DataTable";

export default function Dashboard() {
  const { currentClient, isAdmin, simulatedClient } = useAuth();
  const [selectedClientId, setSelectedClientId] = useState<string>("");
  const [activeSource, setActiveSource] = useState<DataSource | "all">("all");
  const [dateRange, setDateRange] = useState<DateRange>({
    from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    to: new Date(),
  });

  // Ensure we always have a client selected if we are admin AND not simulating
  useEffect(() => {
    if (
      isAdmin &&
      !simulatedClient &&
      !selectedClientId &&
      mockClients.length > 0
    ) {
      setSelectedClientId(mockClients[0].id);
    }
  }, [isAdmin, simulatedClient, selectedClientId]);

  const showSelector = isAdmin && !simulatedClient;

  // If showing selector -> use local selection
  // If simulating -> use currentClient (which is the simulated client)
  // If regular client -> use currentClient
  const effectiveClient = showSelector
    ? mockClients.find((c) => c.id === selectedClientId)
    : currentClient;

  // Safety fallback for display
  const displayClient =
    effectiveClient || (showSelector ? mockClients[0] : null);
  const displayClientId = displayClient?.id;

  // Filter campaigns based on effective client
  const clientCampaignIds = useMemo(() => {
    if (!displayClientId) return [];
    return mockCampaigns
      .filter((c) => c.clientId === displayClientId)
      .map((c) => c.id);
  }, [displayClientId]);

  const filteredCampaigns = useMemo(() => {
    let data = mockCampaignPerformance;

    // Filter by client campaigns
    if (displayClientId) {
      data = data.filter((p) => clientCampaignIds.includes(p.campaignId));
    }

    if (activeSource === "all") return data;
    return filterBySource(data, activeSource);
  }, [activeSource, displayClientId, clientCampaignIds]);

  const chartData = useMemo(() => generateChartData(30), []);

  const clientName = displayClient?.name || "Select Client";

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{clientName}</h1>
          <p className="text-slate-600">
            Performance overview for your paid media campaigns
          </p>
        </div>

        <div className="flex items-center gap-3">
          {showSelector && (
            <Select
              value={selectedClientId}
              onValueChange={setSelectedClientId}
            >
              <SelectTrigger className="w-[200px] bg-white border-slate-200 cursor-pointer">
                <SelectValue placeholder="Select client" />
              </SelectTrigger>
              <SelectContent className="bg-white">
                {mockClients.map((client) => (
                  <SelectItem key={client.id} value={client.id}>
                    {client.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
          <DateRangePicker
            dateRange={dateRange}
            onDateRangeChange={setDateRange}
          />
          <Button variant="outline" size="icon" className="cursor-pointer">
            <RefreshCw className="w-4 h-4" />
          </Button>
          {/* <Button variant="outline" className="gap-2">
            <Download className="w-4 h-4" />
            Export
          </Button> */}
        </div>
      </div>

      {/* Platform Tabs */}
      <div className="mb-8">
        <PlatformTabs activeSource={activeSource} onChange={setActiveSource} />
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-8">
        <KPICard
          title="Total Spend"
          value={formatCurrency(mockKPIData.spend.value)}
          trend={mockKPIData.spend}
          icon={DollarSign}
          delay={0}
        />
        <KPICard
          title="Revenue"
          value={formatCurrency(mockKPIData.revenue.value)}
          trend={mockKPIData.revenue}
          icon={TrendingUp}
          delay={50}
        />
        <KPICard
          title="ROAS"
          value={`${mockKPIData.roas.value.toFixed(2)}x`}
          trend={mockKPIData.roas}
          icon={Target}
          delay={100}
        />
        <KPICard
          title="CPA"
          value={formatCurrency(mockKPIData.cpa.value)}
          trend={mockKPIData.cpa}
          icon={DollarSign}
          invertTrend
          delay={150}
        />
        <KPICard
          title="Impressions"
          value={formatNumber(mockKPIData.impressions.value)}
          trend={mockKPIData.impressions}
          icon={Eye}
          delay={200}
        />
        <KPICard
          title="Clicks"
          value={formatNumber(mockKPIData.clicks.value)}
          trend={mockKPIData.clicks}
          icon={MousePointer}
          delay={250}
        />
      </div>

      {/* Performance Chart */}
      <div className="bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 mb-8 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">
              Performance Trend
            </h2>
            <p className="text-sm text-slate-600">Spend vs Revenue over time</p>
          </div>
        </div>
        <PerformanceChart data={chartData} />
      </div>

      {/* Campaign Performance Table */}
      <div className="bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">
              Campaign Performance
            </h2>
            <p className="text-sm text-slate-600">
              {filteredCampaigns.length} active campaigns
            </p>
          </div>
        </div>
        <CampaignTable campaigns={filteredCampaigns} />
      </div>

      {/* Campaign Performance Chart */}
      <div className="mt-8 bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
        <MetricBarChart
          data={mockCampaignPerformance.map((item) => ({
            id: item.campaignId,
            name: item.campaignName,
            conversions: item.conversions,
            revenue: item.revenue,
            spend: item.spend,
            clicks: item.clicks,
          }))}
          title="Campaign Performance"
        />
      </div>

      {/* Campaign Performance Table */}
      <div className="mt-6 bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">
          Campaign Details
        </h3>
        <DataTable
          data={mockCampaignPerformance.map((item) => ({
            id: item.campaignId,
            name: item.campaignName,
            impressions: item.impressions,
            clicks: item.clicks,
            ctr: item.ctr,
            conversions: item.conversions,
            revenue: item.revenue,
            spend: item.spend,
            roas: item.roas,
          }))}
          columns={[
            { key: "name", label: "Campaign Name", format: "text" },
            { key: "impressions", label: "Impressions", format: "number" },
            { key: "clicks", label: "Clicks", format: "number" },
            { key: "ctr", label: "CTR", format: "percent" },
            { key: "conversions", label: "Conversions", format: "number" },
            { key: "revenue", label: "Revenue", format: "currency" },
            { key: "spend", label: "Spend", format: "currency" },
            { key: "roas", label: "ROAS", format: "number" },
          ]}
        />
      </div>

      {/* Strategy Performance Chart */}
      <div className="mt-8 bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
        <MetricBarChart
          data={mockStrategyPerformance.map((item) => ({
            id: item.id,
            name: item.name,
            conversions: item.conversions,
            revenue: item.revenue,
            spend: item.spend,
            clicks: item.clicks,
          }))}
          title="Strategy Performance"
        />
      </div>

      {/* Strategy Performance Table */}
      <div className="mt-6 bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">
          Strategy Details
        </h3>
        <DataTable
          data={mockStrategyPerformance}
          columns={[
            { key: "name", label: "Strategy", format: "text" },
            { key: "impressions", label: "Impressions", format: "number" },
            { key: "clicks", label: "Clicks", format: "number" },
            { key: "ctr", label: "CTR", format: "percent" },
            { key: "conversions", label: "Conversions", format: "number" },
            { key: "revenue", label: "Revenue", format: "currency" },
            { key: "spend", label: "Spend", format: "currency" },
            { key: "roas", label: "ROAS", format: "number" },
          ]}
        />
      </div>

      {/* Region Performance Chart */}
      <div className="mt-8 bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
        <MetricBarChart
          data={mockRegionPerformance.map((item) => ({
            id: item.id,
            name: item.name,
            conversions: item.conversions,
            revenue: item.revenue,
            spend: item.spend,
            clicks: item.clicks,
          }))}
          title="Region Performance"
        />
      </div>

      {/* Region Performance Table */}
      <div className="mt-6 bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">
          Region Details
        </h3>
        <DataTable
          data={mockRegionPerformance}
          columns={[
            { key: "name", label: "Region", format: "text" },
            { key: "impressions", label: "Impressions", format: "number" },
            { key: "clicks", label: "Clicks", format: "number" },
            { key: "ctr", label: "CTR", format: "percent" },
            { key: "conversions", label: "Conversions", format: "number" },
            { key: "revenue", label: "Revenue", format: "currency" },
            { key: "spend", label: "Spend", format: "currency" },
            { key: "roas", label: "ROAS", format: "number" },
          ]}
        />
      </div>

      {/* Creative Performance Chart */}
      <div className="mt-8 bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
        <MetricBarChart
          data={mockCreativePerformance.map((item) => ({
            id: item.id,
            name: item.name,
            conversions: item.conversions,
            revenue: item.revenue,
            spend: item.spend,
            clicks: item.clicks,
          }))}
          title="Creative Performance"
        />
      </div>

      {/* Creative Performance Table */}
      <div className="mt-6 bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">
          Creative Details
        </h3>
        <DataTable
          data={mockCreativePerformance}
          columns={[
            { key: "name", label: "Creative", format: "text" },
            { key: "impressions", label: "Impressions", format: "number" },
            { key: "clicks", label: "Clicks", format: "number" },
            { key: "ctr", label: "CTR", format: "percent" },
            { key: "conversions", label: "Conversions", format: "number" },
            { key: "revenue", label: "Revenue", format: "currency" },
            { key: "spend", label: "Spend", format: "currency" },
            { key: "roas", label: "ROAS", format: "number" },
          ]}
        />
      </div>
    </div>
  );
}
