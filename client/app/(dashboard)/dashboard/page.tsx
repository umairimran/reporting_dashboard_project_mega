"use client";

import { useState, useMemo, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
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
import CampaignTable from "@/components/dashboard/CampaignTable";
import DashboardCustomizer, {
  KPIConfig,
  SectionConfig,
} from "@/components/dashboard/DashboardCustomizer";
import GenerateReportDialog from "@/components/dashboard/GenerateReportDialog";
import { useAuth } from "@/contexts/AuthContext";
import { DataSource, DateRange } from "@/types/dashboard";
import { mockRegionPerformance } from "@/lib/mock-data";
import { formatCurrency, formatNumber, formatRawNumber } from "@/lib/utils";

import MetricBarChart from "@/components/dashboard/MetricBarChart";
import DataTable from "@/components/dashboard/DataTable";
import { clientsService } from "@/lib/services/clients";
import { metricsService, DailyMetric } from "@/lib/services/metrics";
import { Client } from "@/types/dashboard";

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
  { id: "placement", label: "Placement Performance", order: 2 },
  { id: "creative", label: "Creative Performance", order: 3 },
  { id: "region", label: "Region Performance", order: 4 },
];


const STORAGE_KEY_KPIS = "dashboard_kpis";
const STORAGE_KEY_SECTIONS = "dashboard_sections";

export default function Dashboard() {
  const { currentClient, isAdmin, simulatedClient } = useAuth();

  // 1. DRAFT STATE (UI Controls for Client & Date)
  const [selectedClientId, setSelectedClientId] = useState<string>("");
  const [selectedDateRange, setSelectedDateRange] = useState<DateRange>({
    from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    to: new Date(),
  });

  // 2. APPLIED STATE (Query Dependencies) - Initialized same as draft
  const [appliedClientId, setAppliedClientId] = useState<string>("");
  const [appliedDateRange, setAppliedDateRange] = useState<DateRange>({
    from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    to: new Date(),
  });

  // 3. VIEW STATE (Source Tab - Instant Switch)
  const [activeSource, setActiveSource] = useState<DataSource>("surfside");

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
          const mergedKPIs = DEFAULT_KPIS.map((defaultKPI) => {
            const saved = parsed.find((k: KPIConfig) => k.id === defaultKPI.id);
            return saved || defaultKPI;
          });
          setKpis(mergedKPIs);
        } catch (e) {
          console.error("Failed to parse KPIs from localStorage ", e);
          setKpis(DEFAULT_KPIS);
        }
      }

      if (savedSections) {
        try {
          const parsed = JSON.parse(savedSections);
          // Merge strategy: Start with defaults to ensure all required sections exist.
          // If a section is in saved prefs, use its order/visibility (if we had visibility).
          // Since sections only track order currently, we want to respect saved order but inject new available sections.

          // 1. Get all saved IDs
          const savedIds = new Set(parsed.map((s: SectionConfig) => s.id));

          // 2. Find any new default sections that aren't in saved
          const newSections = DEFAULT_SECTIONS.filter(s => !savedIds.has(s.id));

          // 3. Combine saved + new
          // We append new sections at the end for now, or we could re-sort based on default order if preferred.
          // A safer bet to keep user prefs is: keep saved, append new.
          setSections([...parsed, ...newSections]);
        } catch (e) {
          console.error("Failed to parse sections from localStorage ", e);
          setSections(DEFAULT_SECTIONS);
        }
      }

    }
  }, []);

  // Fetch Clients
  const { data: clientsData } = useQuery({
    queryKey: ["clients"],
    queryFn: () => clientsService.getClients(0, 100),
    enabled: isAdmin && !simulatedClient,
  });

  const clients = clientsData?.clients || [];

  // Ensure we always have a client selected and applied defaults
  useEffect(() => {
    if (
      isAdmin &&
      !simulatedClient &&
      !selectedClientId &&
      clients.length > 0
    ) {
      const defaultId = clients[0].id;
      setSelectedClientId(defaultId);
      setAppliedClientId(defaultId); // Apply immediately on initial load
    }
  }, [isAdmin, simulatedClient, selectedClientId, clients]);

  // Handle Client Context (Non-Admin)
  // Handle Client Context (Non-Admin or Simulation)
  useEffect(() => {
    // If we have a current client (regular user OR simulated), enforce that selection
    if (currentClient && (!isAdmin || simulatedClient)) {
      setSelectedClientId(currentClient.id);
      setAppliedClientId(currentClient.id);
    }
  }, [currentClient, isAdmin, simulatedClient]);

  // Check if filters have changed (Dirty State) - ONLY Client and Date
  const hasChanges =
    selectedClientId !== appliedClientId ||
    selectedDateRange.from?.getTime() !== appliedDateRange.from?.getTime() ||
    selectedDateRange.to?.getTime() !== appliedDateRange.to?.getTime();

  // Apply Filters Handler
  const handleApplyFilters = () => {
    setAppliedClientId(selectedClientId);
    setAppliedDateRange(selectedDateRange);
  };

  const showSelector = isAdmin && !simulatedClient;

  const effectiveClient = showSelector
    ? clients.find((c) => c.id === selectedClientId) // Display based on selection
    : currentClient;

  // For Display Name
  const displayClient = effectiveClient || (showSelector ? clients[0] : null);
  const clientName = displayClient?.name || "Select Client";

  // Format dates for API (Use APPLIED state)
  const formattedDateFrom = appliedDateRange.from
    ? appliedDateRange.from.toISOString().split("T")[0]
    : "";
  const formattedDateTo = appliedDateRange.to
    ? appliedDateRange.to.toISOString().split("T")[0]
    : "";

  // =========================================================================
  // SIMULTANEOUS FETCHING
  // We fetch BOTH Surfside and Facebook data whenever Applied filters change
  // =========================================================================

  // 1. SURFSIDE QUERIES
  const { data: surfsideDaily = [], isLoading: loadingSurfsideDaily } =
    useQuery({
      queryKey: [
        "metrics",
        "daily",
        appliedClientId,
        "surfside",
        formattedDateFrom,
        formattedDateTo,
      ],
      queryFn: () =>
        metricsService.getDailyMetrics({
          start_date: formattedDateFrom,
          end_date: formattedDateTo,
          client_id: appliedClientId!,
          source: "surfside",
          limit: 100000,
        }),
      enabled: !!appliedClientId && !!formattedDateFrom && !!formattedDateTo,
    });

  const { data: surfsideSummary, isLoading: loadingSurfsideSummary } = useQuery(
    {
      queryKey: [
        "metrics",
        "summary",
        appliedClientId,
        "surfside",
        formattedDateFrom,
        formattedDateTo,
      ],
      queryFn: () =>
        metricsService.getSummary({
          start_date: formattedDateFrom,
          end_date: formattedDateTo,
          client_id: appliedClientId!,
          source: "surfside",
        }),
      enabled: !!appliedClientId && !!formattedDateFrom && !!formattedDateTo,
    }
  );

  // 2. FACEBOOK QUERIES
  const { data: facebookDaily = [], isLoading: loadingFacebookDaily } =
    useQuery({
      queryKey: [
        "metrics",
        "daily",
        appliedClientId,
        "facebook",
        formattedDateFrom,
        formattedDateTo,
      ],
      queryFn: () =>
        metricsService.getDailyMetrics({
          start_date: formattedDateFrom,
          end_date: formattedDateTo,
          client_id: appliedClientId!,
          source: "facebook",
          limit: 100000,
        }),
      enabled: !!appliedClientId && !!formattedDateFrom && !!formattedDateTo,
    });

  const { data: facebookSummary, isLoading: loadingFacebookSummary } = useQuery(
    {
      queryKey: [
        "metrics",
        "summary",
        appliedClientId,
        "facebook",
        formattedDateFrom,
        formattedDateTo,
      ],
      queryFn: () =>
        metricsService.getSummary({
          start_date: formattedDateFrom,
          end_date: formattedDateTo,
          client_id: appliedClientId!,
          source: "facebook",
        }),
      enabled: !!appliedClientId && !!formattedDateFrom && !!formattedDateTo,
    }
  );

  // SWITCH DATA BASED ON ACTIVE TAB (Instant Switch)
  const dailyMetrics =
    activeSource === "surfside" ? surfsideDaily : facebookDaily;
  const summaryMetrics =
    activeSource === "surfside" ? surfsideSummary : facebookSummary;

  const isLoading =
    activeSource === "surfside"
      ? loadingSurfsideDaily || loadingSurfsideSummary
      : loadingFacebookDaily || loadingFacebookSummary;

  // Aggregate Data
  const aggregatedData = useMemo(() => {
    const campaigns: Record<string, any> = {};
    const strategies: Record<string, any> = {};
    const placements: Record<string, any> = {};
    const creatives: Record<string, any> = {};
    const regions: Record<string, any> = {};


    const initMetric = {
      impressions: 0,
      clicks: 0,
      conversions: 0,
      revenue: 0,
      spend: 0,
    };

    const accumulate = (target: any, source: DailyMetric) => {
      target.impressions += Number(source.impressions || 0);
      target.clicks += Number(source.clicks || 0);
      target.conversions += Number(source.conversions || 0);
      target.revenue += Number(source.conversion_revenue || 0);
      target.spend += Number(source.spend || 0);
    };

    dailyMetrics.forEach((m) => {
      // Campaign
      const campName = m.campaign_name || "Unknown";
      if (!campaigns[campName]) {
        campaigns[campName] = { ...initMetric, name: campName, id: campName };
      }
      accumulate(campaigns[campName], m);

      // Strategy
      const stratName = m.strategy_name || "Unknown";
      if (!strategies[stratName]) {
        strategies[stratName] = {
          ...initMetric,
          name: stratName,
          id: stratName,
        };
      }
      accumulate(strategies[stratName], m);

      // Placement
      const placeName = m.placement_name || "Unknown";
      if (!placements[placeName]) {
        placements[placeName] = {
          ...initMetric,
          name: placeName,
          id: placeName,
        };
      }
      accumulate(placements[placeName], m);

      // Creative
      const creatName = m.creative_name || "Unknown";
      if (!creatives[creatName]) {
        creatives[creatName] = {
          ...initMetric,
          name: creatName,
          id: creatName,
        };
      }
      accumulate(creatives[creatName], m);

      // Region (Only if present)
      if (m.region_name) {
        const regName = m.region_name;
        if (!regions[regName]) {
          regions[regName] = { ...initMetric, name: regName, id: regName };
        }
        accumulate(regions[regName], m);
      }
    });

    const calculateComputed = (item: any) => ({
      ...item,
      ctr: item.impressions ? (item.clicks / item.impressions) * 100 : 0,
      roas: item.spend ? item.revenue / item.spend : 0,
    });

    return {
      campaigns: Object.values(campaigns).map(calculateComputed),
      strategies: Object.values(strategies).map(calculateComputed),
      placements: Object.values(placements).map(calculateComputed),
      creatives: Object.values(creatives).map(calculateComputed),
      regions: Object.values(regions).map(calculateComputed),
    };

  }, [dailyMetrics]);

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

  // Render section based on ID
  const renderSection = (sectionId: string) => {
    switch (sectionId) {
      case "campaign":
        // ####### here we commented a working code for xyz section ####
        if (activeSource === "surfside") return null;

        const campaignAllowedMetrics = activeSource === 'facebook' ? ['clicks', 'spend'] : undefined;

        return (

          <div key="campaign">
            <div className="mt-8 bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
              <MetricBarChart
                data={aggregatedData.campaigns.map((item) => ({
                  id: item.id,
                  name: item.name,
                  conversions: item.conversions,
                  revenue: item.revenue,
                  spend: item.spend,
                  clicks: item.clicks,
                }))}
                title="Campaign Performance"
                allowedMetrics={campaignAllowedMetrics as any}
                color="#3b82f6" // Blue
              />
            </div>
            <div className="mt-6 bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-slate-900">
                  Campaign Details
                </h3>
                <span className="text-sm text-slate-600">
                  Total: {aggregatedData.campaigns.length} records
                </span>
              </div>
              <DataTable
                data={aggregatedData.campaigns}
                columns={[
                  { key: "name", label: "Campaign Name", format: "text" },
                  {
                    key: "impressions",
                    label: "Impressions",
                    format: "raw",
                  },
                  { key: "clicks", label: "Clicks", format: "raw" },
                  { key: "ctr", label: "CTR", format: "percent" },
                  ...(activeSource !== 'facebook' ? [
                    { key: "conversions", label: "Conversions", format: "raw" } as any,
                    { key: "revenue", label: "Revenue", format: "currency" } as any,
                    { key: "roas", label: "ROAS", format: "raw" } as any,
                  ] : []),
                  { key: "spend", label: "Spend", format: "currency" },
                ]}

              />
            </div>
          </div>
        );
      case "strategy":
        if (activeSource === "facebook") return null;
        return (
          <div key="strategy">
            <div className="mt-8 bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
              <MetricBarChart
                data={aggregatedData.strategies.map((item) => ({

                  id: item.id,
                  name: item.name,
                  conversions: item.conversions,
                  revenue: item.revenue,
                  spend: item.spend,
                  clicks: item.clicks,
                }))}
                title="Strategy Performance"
                color="#8b5cf6" // Purple
              />
            </div>
            <div className="mt-6 bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-slate-900">
                  Strategy Details
                </h3>
                <span className="text-sm text-slate-600">
                  Total: {aggregatedData.strategies.length} records
                </span>
              </div>
              <DataTable
                data={aggregatedData.strategies}
                columns={[
                  { key: "name", label: "Strategy", format: "text" },
                  {
                    key: "impressions",
                    label: "Impressions",
                    format: "raw",
                  },
                  { key: "clicks", label: "Clicks", format: "raw" },
                  { key: "ctr", label: "CTR", format: "percent" },
                  {
                    key: "conversions",
                    label: "Conversions",
                    format: "raw",
                  },
                  { key: "revenue", label: "Revenue", format: "currency" },
                  { key: "spend", label: "Spend", format: "currency" },
                  { key: "roas", label: "ROAS", format: "raw" },
                ]}

              />
            </div>
          </div>
        );
      case "placement":
        if (activeSource === "facebook") return null;
        return (
          <div key="placement">
            <div className="mt-8 bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
              <MetricBarChart
                data={aggregatedData.placements.map((item) => ({
                  id: item.id,
                  name: item.name,
                  conversions: item.conversions,
                  revenue: item.revenue,
                  spend: item.spend,
                  clicks: item.clicks,
                }))}
                title="Placement Performance"
                color="#14b8a6" // Teal
              />
            </div>
            <div className="mt-6 bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-slate-900">
                  Placement Details
                </h3>
                <span className="text-sm text-slate-600">
                  Total: {aggregatedData.placements.length} records
                </span>
              </div>
              <DataTable
                data={aggregatedData.placements}
                columns={[
                  { key: "name", label: "Placement", format: "text" },
                  {
                    key: "impressions",
                    label: "Impressions",
                    format: "raw",
                  },
                  { key: "clicks", label: "Clicks", format: "raw" },
                  { key: "ctr", label: "CTR", format: "percent" },
                  {
                    key: "conversions",
                    label: "Conversions",
                    format: "raw",
                  },
                  { key: "revenue", label: "Revenue", format: "currency" },
                  { key: "spend", label: "Spend", format: "currency" },
                  { key: "roas", label: "ROAS", format: "raw" },
                ]}
              />
            </div>
          </div>
        );
      case "region":

        // ####### here we commented a working code for xyz section ####
        if (activeSource === "surfside") return null;

        const regionAllowedMetrics = activeSource === 'facebook' ? ['clicks', 'spend'] : undefined;

        return (

          <div key="region">
            <div className="mt-8 bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
              <MetricBarChart
                data={aggregatedData.regions.map((item) => ({
                  id: item.id,
                  name: item.name,
                  conversions: item.conversions,
                  revenue: item.revenue,
                  spend: item.spend,
                  clicks: item.clicks,
                }))}
                title="Region Performance"
                allowedMetrics={regionAllowedMetrics as any}
                color="#f43f5e" // Rose
              />
            </div>
            <div className="mt-6 bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-slate-900">
                  Region Details
                </h3>
                <span className="text-sm text-slate-600">
                  Total: {aggregatedData.regions.length} records
                </span>
              </div>
              <DataTable
                data={aggregatedData.regions}
                columns={[
                  { key: "name", label: "Region", format: "text" },
                  {
                    key: "impressions",
                    label: "Impressions",
                    format: "raw",
                  },
                  { key: "clicks", label: "Clicks", format: "raw" },
                  { key: "ctr", label: "CTR", format: "percent" },
                  ...(activeSource !== 'facebook' ? [
                    { key: "conversions", label: "Conversions", format: "raw" } as any,
                    { key: "revenue", label: "Revenue", format: "currency" } as any,
                    { key: "roas", label: "ROAS", format: "raw" } as any,
                  ] : []),
                  { key: "spend", label: "Spend", format: "currency" },
                ]}

              />
            </div>
          </div>
        );
      case "creative":

        const creativeAllowedMetrics = activeSource === 'facebook' ? ['clicks', 'spend'] : undefined;

        return (
          <div key="creative">
            <div className="mt-8 bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
              <MetricBarChart
                data={aggregatedData.creatives.map((item) => ({
                  id: item.id,
                  name: item.name,
                  conversions: item.conversions,
                  revenue: item.revenue,
                  spend: item.spend,
                  clicks: item.clicks,
                }))}
                title="Creative Performance"
                allowedMetrics={creativeAllowedMetrics as any}
                color="#f59e0b" // Orange
              />
            </div>
            <div className="mt-6 bg-white/80 backdrop-blur-2xl border border-slate-200 rounded-xl p-6 opacity-0 animate-[fadeIn_0.5s_ease-out_forwards]">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-slate-900">
                  Creative Details
                </h3>
                <span className="text-sm text-slate-600">
                  Total: {aggregatedData.creatives.length} records
                </span>
              </div>
              <DataTable
                data={aggregatedData.creatives}
                columns={[
                  { key: "name", label: "Creative", format: "text" },
                  {
                    key: "impressions",
                    label: "Impressions",
                    format: "raw",
                  },
                  { key: "clicks", label: "Clicks", format: "raw" },
                  { key: "ctr", label: "CTR", format: "percent" },
                  ...(activeSource !== 'facebook' ? [
                    { key: "conversions", label: "Conversions", format: "raw" } as any,
                    { key: "revenue", label: "Revenue", format: "currency" } as any,
                    { key: "roas", label: "ROAS", format: "raw" } as any,
                  ] : []),
                  { key: "spend", label: "Spend", format: "currency" },
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
    <div className="p-8 px-48">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-blue-600">{clientName}</h1>
          <div className="flex items-center gap-3 mt-1">
            <div className="w-px h-6 bg-slate-300"></div>
            <p className="text-lg text-slate-500">Performance Overview</p>
          </div>
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
                {clients.map((client) => (
                  <SelectItem key={client.id} value={client.id}>
                    {client.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
          <DateRangePicker
            dateRange={selectedDateRange}
            onDateRangeChange={setSelectedDateRange}
          />

          <Button
            onClick={handleApplyFilters}
            disabled={!hasChanges && !isLoading}
            className={`transition-all duration-300 ${hasChanges
              ? "bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-200"
              : ""
              }`}
            size="default"
          >
            {isLoading
              ? "Updating..."
              : hasChanges
                ? "Apply Changes"
                : "Up to Date"}
          </Button>

          <GenerateReportDialog clientId={appliedClientId}>
            <Button variant="outline" className="gap-2">
              <Download className="w-4 h-4" />
              Export
            </Button>
          </GenerateReportDialog>
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

      {/* Loading Overlay or Content */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-32 space-y-4 animate-in fade-in duration-500">
          <div className="relative">
            <div className="w-16 h-16 border-4 border-blue-100 border-t-blue-600 rounded-full animate-spin"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-8 h-8 bg-white rounded-full"></div>
            </div>
          </div>
          <p className="text-slate-500 font-medium animate-pulse">
            Fetching fresh insights...
          </p>
        </div>
      ) : (
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
          {/* KPI Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {kpis
              .filter((kpi) => {
                if (!kpi.enabled) return false;
                if (activeSource === 'facebook') {
                  // Hide revenue, conversions, roas, cpa for Facebook
                  if (['revenue', 'conversions', 'roas', 'cpa'].includes(kpi.id)) return false;
                }
                return true;
              })
              .sort((a, b) => a.order - b.order)
              .map((kpi, index) => {
                // Calculate Trend
                let trendValue = 0;
                let isPositive = true;
                const prev = summaryMetrics?.previous_period;

                // Helper for trend % calculation: ((Curr - Prev) / Prev) * 100
                const calcTrend = (
                  curr: number = 0,
                  prev: number = 0,
                  inverse: boolean = false
                ) => {
                  if (!prev) return { value: 0, isPositive: true }; // No previous data
                  const change = ((curr - prev) / prev) * 100;
                  // For costs (CPA, CPC), negative change is "Positive" (Good)
                  const isPos = inverse ? change <= 0 : change >= 0;
                  return {
                    value: Math.abs(change),
                    isPositive: isPos,
                    hasData: true,
                  };
                };

                // default 'hasData' check to hide trend if no previous period
                let trendInfo = { value: 0, isPositive: true, hasData: !!prev };

                const kpiData: Record<string, any> = {
                  spend: {
                    title: "Spend",
                    value: formatCurrency(summaryMetrics?.total_spend || 0),
                    trend: calcTrend(
                      summaryMetrics?.total_spend,
                      prev?.total_spend
                    ),
                    icon: DollarSign,
                  },
                  revenue: {
                    title: "Revenue",
                    value: formatCurrency(summaryMetrics?.total_revenue || 0),
                    trend: calcTrend(
                      summaryMetrics?.total_revenue,
                      prev?.total_revenue
                    ),
                    icon: TrendingUp,
                  },
                  roas: {
                    title: "ROAS",
                    value: `${Number(summaryMetrics?.overall_roas || 0).toFixed(
                      2
                    )}x`,
                    trend: calcTrend(
                      summaryMetrics?.overall_roas || 0,
                      prev?.overall_roas || 0
                    ),
                    icon: Target,
                  },
                  cpa: {
                    title: "CPA",
                    value: formatCurrency(summaryMetrics?.overall_cpa || 0),
                    trend: calcTrend(
                      summaryMetrics?.overall_cpa || 0,
                      prev?.overall_cpa || 0,
                      true
                    ), // Inverse
                    icon: DollarSign,
                    invertTrend: true,
                  },
                  impressions: {
                    title: "Impressions",
                    value: formatRawNumber(summaryMetrics?.total_impressions || 0),
                    trend: calcTrend(
                      summaryMetrics?.total_impressions,
                      prev?.total_impressions
                    ),

                    icon: Eye,
                  },
                  clicks: {
                    title: "Clicks",
                    value: formatRawNumber(summaryMetrics?.total_clicks || 0),
                    trend: calcTrend(
                      summaryMetrics?.total_clicks,
                      prev?.total_clicks
                    ),

                    icon: MousePointer,
                  },
                  ctr: {
                    title: "CTR",
                    value: `${(Number(summaryMetrics?.overall_ctr || 0) * 100).toFixed(
                      2
                    )}%`,
                    trend: calcTrend(
                      summaryMetrics?.overall_ctr || 0,
                      prev?.overall_ctr || 0
                    ),
                    icon: Target,
                  },
                  conversions: {
                    title: "Conversions",
                    value: formatRawNumber(summaryMetrics?.total_conversions || 0),
                    trend: calcTrend(
                      summaryMetrics?.total_conversions,
                      prev?.total_conversions
                    ),

                    icon: Target,
                  },
                };

                const data = kpiData[kpi.id];
                if (!data) return null;

                // Only pass trend if previous data exists
                const finalTrend = trendInfo.hasData ? data.trend : undefined;

                return (
                  <KPICard
                    key={kpi.id}
                    title={data.title}
                    value={data.value}
                    trend={finalTrend}
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
      )}
    </div>
  );
}
