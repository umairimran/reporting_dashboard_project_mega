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
import DashboardCustomizer, {
  KPIConfig,
  SectionConfig,
} from "@/components/dashboard/DashboardCustomizer";
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

const DEFAULT_KPIS: KPIConfig[] = [
  { id: "clicks", label: "Clicks", enabled: true, order: 0 },
  { id: "impressions", label: "Impressions", enabled: true, order: 1 },
  { id: "revenue", label: "Revenue", enabled: true, order: 2 },
  { id: "ctr", label: "CTR", enabled: true, order: 3 },
  { id: "conversions", label: "Conversions", enabled: true, order: 4 },
  { id: "spend", label: "Spend", enabled: true, order: 5 },
  { id: "roas", label: "ROAS", enabled: true, order: 6 },
  { id: "cpa", label: "CPA", enabled: true, order: 7 },
];

const DEFAULT_SECTIONS: SectionConfig[] = [
  { id: "campaign", label: "Campaign Performance", order: 0 },
  { id: "strategy", label: "Strategy Performance", order: 1 },
  { id: "region", label: "Region Performance", order: 2 },
  { id: "creative", label: "Creative Performance", order: 3 },
];

const STORAGE_KEY_KPIS = "dashboard_kpis";
const STORAGE_KEY_SECTIONS = "dashboard_sections";

export default function Dashboard() {
  const { currentClient, isAdmin, simulatedClient } = useAuth();
  const [selectedClientId, setSelectedClientId] = useState<string>("");
  const [activeSource, setActiveSource] = useState<DataSource>("surfside");
  const [dateRange, setDateRange] = useState<DateRange>({
    from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    to: new Date(),
  });
  const [kpis, setKpis] = useState<KPIConfig[]>(DEFAULT_KPIS);
  const [sections, setSections] = useState<SectionConfig[]>(DEFAULT_SECTIONS);

  // Load preferences from localStorage
  useEffect(() => {
    if (typeof window !== "undefined") {
      const savedKPIs = localStorage.getItem(STORAGE_KEY_KPIS);
      const savedSections = localStorage.getItem(STORAGE_KEY_SECTIONS);

      if (savedKPIs) {
        try {
          const parsed = JSON.parse(savedKPIs);
          // Merge with defaults to ensure new KPIs are included
          const mergedKPIs = DEFAULT_KPIS.map((defaultKPI) => {
            const saved = parsed.find((k: KPIConfig) => k.id === defaultKPI.id);
            return saved || defaultKPI;
          });
          setKpis(mergedKPIs);
        } catch (e) {
          console.error("Failed to parse KPIs from localStorage", e);
          setKpis(DEFAULT_KPIS);
        }
      }

      if (savedSections) {
        try {
          setSections(JSON.parse(savedSections));
        } catch (e) {
          console.error("Failed to parse sections from localStorage ", e);
        }
      }
    }
  }, []);

  // Save preferences to localStorage
  const handleKPIsChange = (newKPIs: KPIConfig[]) => {
    setKpis(newKPIs);
    if (typeof window !== "undefined") {
      localStorage.setItem(STORAGE_KEY_KPIS, JSON.stringify(newKPIs));
    }
  };

  const handleSectionsChange = (newSections: SectionConfig[]) => {
    setSections(newSections);
    if (typeof window !== "undefined") {
      localStorage.setItem(STORAGE_KEY_SECTIONS, JSON.stringify(newSections));
    }
  };

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

  const clientName = displayClient?.name || "Select Client";

  // Render section based on ID
  const renderSection = (sectionId: string) => {
    switch (sectionId) {
      case "campaign":
        return (
          <div key="campaign">
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
                  {
                    key: "impressions",
                    label: "Impressions",
                    format: "number",
                  },
                  { key: "clicks", label: "Clicks", format: "number" },
                  { key: "ctr", label: "CTR", format: "percent" },
                  {
                    key: "conversions",
                    label: "Conversions",
                    format: "number",
                  },
                  { key: "revenue", label: "Revenue", format: "currency" },
                  { key: "spend", label: "Spend", format: "currency" },
                  { key: "roas", label: "ROAS", format: "number" },
                ]}
              />
            </div>
          </div>
        );
      case "strategy":
        return (
          <div key="strategy">
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
                  {
                    key: "impressions",
                    label: "Impressions",
                    format: "number",
                  },
                  { key: "clicks", label: "Clicks", format: "number" },
                  { key: "ctr", label: "CTR", format: "percent" },
                  {
                    key: "conversions",
                    label: "Conversions",
                    format: "number",
                  },
                  { key: "revenue", label: "Revenue", format: "currency" },
                  { key: "spend", label: "Spend", format: "currency" },
                  { key: "roas", label: "ROAS", format: "number" },
                ]}
              />
            </div>
          </div>
        );
      case "region":
        return (
          <div key="region">
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
                  {
                    key: "impressions",
                    label: "Impressions",
                    format: "number",
                  },
                  { key: "clicks", label: "Clicks", format: "number" },
                  { key: "ctr", label: "CTR", format: "percent" },
                  {
                    key: "conversions",
                    label: "Conversions",
                    format: "number",
                  },
                  { key: "revenue", label: "Revenue", format: "currency" },
                  { key: "spend", label: "Spend", format: "currency" },
                  { key: "roas", label: "ROAS", format: "number" },
                ]}
              />
            </div>
          </div>
        );
      case "creative":
        return (
          <div key="creative">
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
                  {
                    key: "impressions",
                    label: "Impressions",
                    format: "number",
                  },
                  { key: "clicks", label: "Clicks", format: "number" },
                  { key: "ctr", label: "CTR", format: "percent" },
                  {
                    key: "conversions",
                    label: "Conversions",
                    format: "number",
                  },
                  { key: "revenue", label: "Revenue", format: "currency" },
                  { key: "spend", label: "Spend", format: "currency" },
                  { key: "roas", label: "ROAS", format: "number" },
                ]}
              />
            </div>
          </div>
        );
      default:
        return null;
    }
  };

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
          <Button variant="outline" className="gap-2">
            <Download className="w-4 h-4" />
            Export
          </Button>
        </div>
      </div>

      {/* Platform Tabs */}
      <div className="mb-8 flex items-center justify-between">
        <PlatformTabs activeSource={activeSource} onChange={setActiveSource} />
        <DashboardCustomizer
          kpis={kpis}
          sections={sections}
          onKPIsChange={handleKPIsChange}
          onSectionsChange={handleSectionsChange}
        />
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {kpis
          .filter((kpi) => kpi.enabled)
          .sort((a, b) => a.order - b.order)
          .map((kpi, index) => {
            const kpiData: Record<string, any> = {
              spend: {
                title: "Spend",
                value: formatCurrency(mockKPIData.spend.value),
                trend: mockKPIData.spend,
                icon: DollarSign,
              },
              revenue: {
                title: "Revenue",
                value: formatCurrency(mockKPIData.revenue.value),
                trend: mockKPIData.revenue,
                icon: TrendingUp,
              },
              roas: {
                title: "ROAS",
                value: `${mockKPIData.roas.value.toFixed(2)}x`,
                trend: mockKPIData.roas,
                icon: Target,
              },
              cpa: {
                title: "CPA",
                value: formatCurrency(mockKPIData.cpa.value),
                trend: mockKPIData.cpa,
                icon: DollarSign,
                invertTrend: true,
              },
              impressions: {
                title: "Impressions",
                value: formatNumber(mockKPIData.impressions.value),
                trend: mockKPIData.impressions,
                icon: Eye,
              },
              clicks: {
                title: "Clicks",
                value: formatNumber(mockKPIData.clicks.value),
                trend: mockKPIData.clicks,
                icon: MousePointer,
              },
              ctr: {
                title: "CTR",
                value: `${mockKPIData.ctr.value.toFixed(2)}%`,
                trend: mockKPIData.ctr,
                icon: Target,
              },
              conversions: {
                title: "Conversions",
                value: formatNumber(mockKPIData.conversions.value),
                trend: mockKPIData.conversions,
                icon: Target,
              },
            };

            const data = kpiData[kpi.id];
            if (!data) return null;

            return (
              <KPICard
                key={kpi.id}
                title={data.title}
                value={data.value}
                trend={data.trend}
                icon={data.icon}
                invertTrend={data.invertTrend}
                delay={index * 50}
              />
            );
          })}
      </div>

      {/* Dynamic Sections based on user preferences */}
      {sections
        .sort((a, b) => a.order - b.order)
        .map((section) => renderSection(section.id))}
    </div>
  );
}
