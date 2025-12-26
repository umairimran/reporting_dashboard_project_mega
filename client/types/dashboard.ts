// User types
export type UserRole = "admin" | "client";

export interface User {
  id: string;
  email: string;
  role: UserRole;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

// Client types
export type ClientStatus = "active" | "disabled";

export interface Client {
  id: string;
  name: string;
  status: ClientStatus;
  userId?: string;
  userRole?: string;
  createdAt: string;
  updatedAt: string;
}

export interface ClientSettings {
  id: string;
  clientId: string;
  source: DataSource;
  cpm: number;
  currency: string;
  effectiveDate?: string;
}

// Data source types
export type DataSource = "surfside" | "facebook";

// Campaign hierarchy types
export interface Campaign {
  id: string;
  clientId: string;
  name: string;
  source: DataSource;
  createdAt: string;
}

export interface Strategy {
  id: string;
  campaignId: string;
  name: string;
}

export interface Placement {
  id: string;
  strategyId: string;
  name: string;
}

export interface Creative {
  id: string;
  placementId: string;
  name: string;
  previewUrl?: string;
}

// Metrics types
export interface DailyMetrics {
  id: string;
  clientId: string;
  date: string;
  campaignId: string;
  strategyId: string;
  placementId: string;
  creativeId: string;
  source: DataSource;
  impressions: number;
  clicks: number;
  conversions: number;
  conversionRevenue: number;
  ctr: number;
  spend: number;
  cpc: number;
  cpa: number;
  roas: number;
}

export interface AggregatedMetrics {
  impressions: number;
  clicks: number;
  conversions: number;
  revenue: number;
  spend: number;
  ctr: number;
  cpc: number;
  cpa: number;
  roas: number;
}

export interface MetricTrend {
  value: number;
  previousValue: number;
  percentChange: number;
  direction: "up" | "down" | "flat";
}

export interface KPIData {
  spend: MetricTrend;
  revenue: MetricTrend;
  roas: MetricTrend;
  cpa: MetricTrend;
  impressions: MetricTrend;
  clicks: MetricTrend;
  ctr: MetricTrend;
  conversions: MetricTrend;
}

// Summary types
export interface WeeklySummary {
  id: string;
  clientId: string;
  weekStart: string;
  weekEnd: string;
  impressions: number;
  clicks: number;
  conversions: number;
  revenue: number;
  spend: number;
  ctr: number;
  cpc: number;
  cpa: number;
  roas: number;
  topCampaigns?: any[];
  topCreatives?: any[];
}

export interface MonthlySummary
  extends Omit<WeeklySummary, "weekStart" | "weekEnd"> {
  monthStart: string;
  monthEnd: string;
}

// Ingestion types
export type IngestionStatus = "success" | "failed" | "partial" | "processing";
export type ResolutionStatus = "unresolved" | "resolved" | "ignored";

export interface IngestionLog {
  id: string;
  runDate: string;
  status: IngestionStatus;
  message?: string;
  recordsLoaded: number;
  recordsFailed: number;
  startedAt: string;
  finishedAt?: string;
  fileName?: string;
  source: DataSource;
  clientId?: string;
  resolutionStatus?: ResolutionStatus;
  resolutionNotes?: string;
}

// Filter types
export interface DateRange {
  from: Date;
  to: Date;
}

export type DatePreset = "last7" | "last30" | "last90" | "custom";

// Chart data types
export interface ChartDataPoint {
  date: string;
  value: number;
  label?: string;
}

export interface CampaignPerformance {
  campaignId: string;
  campaignName: string;
  source: DataSource;
  impressions: number;
  clicks: number;
  conversions: number;
  spend: number;
  revenue: number;
  ctr: number;
  cpc: number;
  cpa: number;
  roas: number;
}

// Report types
export interface Report {
  id: string;
  clientId: string;
  type: "weekly" | "monthly";
  source?: "surfside" | "facebook";
  periodStart: string;
  periodEnd: string;
  generatedAt: string;
  status: "ready" | "generating" | "failed";
  pdfPath?: string;
  csvPath?: string;
  errorMessage?: string;
  clientName?: string;
  // clientId: string; // From computed_field
}
