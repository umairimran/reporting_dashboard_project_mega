import {
  User,
  Client,
  ClientSettings,
  Campaign,
  IngestionLog,
  KPIData,
  CampaignPerformance,
  Report,
  DataSource,
} from "@/types/dashboard";

// Mock Users
export const mockUsers: User[] = [
  {
    id: "1",
    email: "admin@goldstandard.io",
    role: "admin",
    isActive: true,
    createdAt: "2024-01-15T00:00:00Z",
    updatedAt: "2024-12-01T00:00:00Z",
  },
  {
    id: "2",
    email: "client@acmecorp.com",
    role: "client",
    isActive: true,
    createdAt: "2024-03-01T00:00:00Z",
    updatedAt: "2024-12-01T00:00:00Z",
  },
];

// Mock Clients
export const mockClients: Client[] = [
  {
    id: "1",
    name: "Acme Corporation",
    status: "active",
    userId: "2",
    createdAt: "2024-03-01T00:00:00Z",
    updatedAt: "2024-12-01T00:00:00Z",
  },
  {
    id: "2",
    name: "TechStart Inc",
    status: "active",
    userId: "3",
    createdAt: "2024-04-15T00:00:00Z",
    updatedAt: "2024-12-01T00:00:00Z",
  },
  {
    id: "3",
    name: "Global Media",
    status: "disabled",
    userId: "4",
    createdAt: "2024-02-01T00:00:00Z",
    updatedAt: "2024-11-15T00:00:00Z",
  },
  {
    id: "4",
    name: "Retail Partners",
    status: "active",
    userId: "5",
    createdAt: "2024-05-20T00:00:00Z",
    updatedAt: "2024-12-01T00:00:00Z",
  },
  {
    id: "5",
    name: "Finance Plus",
    status: "active",
    userId: "6",
    createdAt: "2024-06-10T00:00:00Z",
    updatedAt: "2024-12-01T00:00:00Z",
  },
];

// Mock Client Settings
export const mockClientSettings: ClientSettings[] = [
  { id: "1", clientId: "1", source: "surfside", cpm: 12.5, currency: "USD" },
  { id: "2", clientId: "1", source: "vibe", cpm: 15.0, currency: "USD" },
  { id: "3", clientId: "1", source: "facebook", cpm: 8.75, currency: "USD" },
  { id: "4", clientId: "2", source: "surfside", cpm: 14.0, currency: "USD" },
  { id: "5", clientId: "2", source: "facebook", cpm: 9.5, currency: "USD" },
];

// Mock Campaigns
export const mockCampaigns: Campaign[] = [
  {
    id: "1",
    clientId: "1",
    name: "Holiday Sale 2024",
    source: "surfside",
    createdAt: "2024-11-01T00:00:00Z",
  },
  {
    id: "2",
    clientId: "1",
    name: "Brand Awareness Q4",
    source: "facebook",
    createdAt: "2024-10-15T00:00:00Z",
  },
  {
    id: "3",
    clientId: "1",
    name: "Retargeting - Cart Abandoners",
    source: "vibe",
    createdAt: "2024-09-01T00:00:00Z",
  },
  {
    id: "4",
    clientId: "1",
    name: "New Product Launch",
    source: "surfside",
    createdAt: "2024-12-01T00:00:00Z",
  },
];

// Mock Ingestion Logs
export const mockIngestionLogs: IngestionLog[] = [
  {
    id: "1",
    runDate: "2024-12-16",
    status: "success",
    message: "Successfully ingested 2,450 records",
    recordsLoaded: 2450,
    recordsFailed: 0,
    startedAt: "2024-12-16T06:00:00Z",
    finishedAt: "2024-12-16T06:05:23Z",
    source: "surfside",
    clientId: "1",
  },
  {
    id: "2",
    runDate: "2024-12-16",
    status: "success",
    message: "Successfully ingested 1,823 records",
    recordsLoaded: 1823,
    recordsFailed: 0,
    startedAt: "2024-12-16T06:10:00Z",
    finishedAt: "2024-12-16T06:14:12Z",
    source: "facebook",
    clientId: "1",
  },
  {
    id: "3",
    runDate: "2024-12-15",
    status: "partial",
    message: "15 records failed validation",
    recordsLoaded: 1985,
    recordsFailed: 15,
    startedAt: "2024-12-15T06:00:00Z",
    finishedAt: "2024-12-15T06:08:45Z",
    fileName: "vibe_report_2024-12-15.csv",
    source: "vibe",
    clientId: "2",
    resolutionStatus: "unresolved",
  },
  {
    id: "4",
    runDate: "2024-12-14",
    status: "failed",
    message: "Connection timeout to S3 bucket",
    recordsLoaded: 0,
    recordsFailed: 0,
    startedAt: "2024-12-14T06:00:00Z",
    finishedAt: "2024-12-14T06:02:30Z",
    source: "surfside",
    resolutionStatus: "resolved",
    resolutionNotes: "Retried manually - succeeded",
  },
  {
    id: "5",
    runDate: "2024-12-13",
    status: "success",
    message: "Successfully ingested 3,102 records",
    recordsLoaded: 3102,
    recordsFailed: 0,
    startedAt: "2024-12-13T06:00:00Z",
    finishedAt: "2024-12-13T06:07:11Z",
    source: "surfside",
    clientId: "1",
  },
];

// Mock KPI Data with trends
export const mockKPIData: KPIData = {
  spend: {
    value: 47832.5,
    previousValue: 42156.75,
    percentChange: 13.47,
    direction: "up",
  },
  revenue: {
    value: 156420.0,
    previousValue: 132890.0,
    percentChange: 17.71,
    direction: "up",
  },
  roas: {
    value: 3.27,
    previousValue: 3.15,
    percentChange: 3.81,
    direction: "up",
  },
  cpa: {
    value: 24.56,
    previousValue: 28.42,
    percentChange: -13.58,
    direction: "down",
  },
  impressions: {
    value: 4825600,
    previousValue: 4156200,
    percentChange: 16.11,
    direction: "up",
  },
  clicks: {
    value: 145680,
    previousValue: 124520,
    percentChange: 16.99,
    direction: "up",
  },
};

// Mock Campaign Performance
export const mockCampaignPerformance: CampaignPerformance[] = [
  {
    campaignId: "1",
    campaignName: "Holiday Sale 2024",
    source: "surfside",
    impressions: 1245000,
    clicks: 42350,
    conversions: 856,
    spend: 15562.5,
    revenue: 52890.0,
    ctr: 3.4,
    cpc: 0.37,
    cpa: 18.18,
    roas: 3.4,
  },
  {
    campaignId: "2",
    campaignName: "Brand Awareness Q4",
    source: "facebook",
    impressions: 2156000,
    clicks: 58920,
    conversions: 425,
    spend: 18860.0,
    revenue: 48750.0,
    ctr: 2.73,
    cpc: 0.32,
    cpa: 44.38,
    roas: 2.58,
  },
  {
    campaignId: "3",
    campaignName: "Retargeting - Cart Abandoners",
    source: "vibe",
    impressions: 856000,
    clicks: 32450,
    conversions: 612,
    spend: 12840.0,
    revenue: 42680.0,
    ctr: 3.79,
    cpc: 0.4,
    cpa: 20.98,
    roas: 3.32,
  },
  {
    campaignId: "4",
    campaignName: "New Product Launch",
    source: "surfside",
    impressions: 568600,
    clicks: 11960,
    conversions: 156,
    spend: 7110.0,
    revenue: 12100.0,
    ctr: 2.1,
    cpc: 0.59,
    cpa: 45.58,
    roas: 1.7,
  },
];

// Mock Daily Chart Data
export function generateChartData(
  days: number = 30
): { date: string; spend: number; revenue: number; impressions: number }[] {
  const data = [];
  const now = new Date();

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);

    const baseSpend = 1500 + Math.random() * 800;
    const roas = 2.8 + Math.random() * 1.2;

    data.push({
      date: date.toISOString().split("T")[0],
      spend: Math.round(baseSpend * 100) / 100,
      revenue: Math.round(baseSpend * roas * 100) / 100,
      impressions: Math.round(baseSpend * 100 + Math.random() * 20000),
    });
  }

  return data;
}

// Mock Reports
export const mockReports: Report[] = [
  {
    id: "1",
    clientId: "1",
    type: "weekly",
    periodStart: "2024-12-09",
    periodEnd: "2024-12-15",
    generatedAt: "2024-12-16T00:00:00Z",
    status: "ready",
  },
  {
    id: "2",
    clientId: "1",
    type: "weekly",
    periodStart: "2024-12-02",
    periodEnd: "2024-12-08",
    generatedAt: "2024-12-09T00:00:00Z",
    status: "ready",
  },
  {
    id: "3",
    clientId: "1",
    type: "monthly",
    periodStart: "2024-11-01",
    periodEnd: "2024-11-30",
    generatedAt: "2024-12-01T00:00:00Z",
    status: "ready",
  },
  {
    id: "4",
    clientId: "1",
    type: "monthly",
    periodStart: "2024-10-01",
    periodEnd: "2024-10-31",
    generatedAt: "2024-11-01T00:00:00Z",
    status: "ready",
  },
];

// Helper to filter by source
export function filterBySource<T extends { source: DataSource }>(
  items: T[],
  source?: DataSource
): T[] {
  if (!source) return items;
  return items.filter((item) => item.source === source);
}

// Helper to format currency
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

// Helper to format large numbers
export function formatNumber(value: number): string {
  if (value >= 1000000) {
    return (value / 1000000).toFixed(2) + "M";
  }
  if (value >= 1000) {
    return (value / 1000).toFixed(1) + "K";
  }
  return value.toLocaleString();
}

// Helper to format percentage
export function formatPercent(value: number): string {
  return value.toFixed(2) + "%";
}

// Mock Strategy Performance Data
export const mockStrategyPerformance = [
  {
    id: "1",
    name: "Prospecting",
    impressions: 2450000,
    clicks: 68500,
    ctr: 2.8,
    conversions: 1250,
    revenue: 95000,
    spend: 28500,
    roas: 3.33,
  },
  {
    id: "2",
    name: "Retargeting",
    impressions: 1850000,
    clicks: 62000,
    ctr: 3.35,
    conversions: 1580,
    revenue: 125000,
    spend: 34200,
    roas: 3.65,
  },
  {
    id: "3",
    name: "Brand Awareness",
    impressions: 3200000,
    clicks: 45000,
    ctr: 1.41,
    conversions: 580,
    revenue: 48500,
    spend: 22000,
    roas: 2.2,
  },
  {
    id: "4",
    name: "Lookalike Audiences",
    impressions: 1680000,
    clicks: 51200,
    ctr: 3.05,
    conversions: 1120,
    revenue: 89600,
    spend: 25800,
    roas: 3.47,
  },
];

// Mock Region Performance Data
export const mockRegionPerformance = [
  {
    id: "1",
    name: "North America",
    impressions: 4250000,
    clicks: 142000,
    ctr: 3.34,
    conversions: 2850,
    revenue: 225000,
    spend: 62000,
    roas: 3.63,
  },
  {
    id: "2",
    name: "Europe",
    impressions: 2850000,
    clicks: 78500,
    ctr: 2.75,
    conversions: 1620,
    revenue: 138000,
    spend: 42500,
    roas: 3.25,
  },
  {
    id: "3",
    name: "Asia Pacific",
    impressions: 1650000,
    clicks: 42000,
    ctr: 2.55,
    conversions: 920,
    revenue: 74500,
    spend: 24800,
    roas: 3.0,
  },
  {
    id: "4",
    name: "Latin America",
    impressions: 980000,
    clicks: 28500,
    ctr: 2.91,
    conversions: 680,
    revenue: 52000,
    spend: 18200,
    roas: 2.86,
  },
  {
    id: "5",
    name: "United States",
    impressions: 3450000,
    clicks: 115000,
    ctr: 3.33,
    conversions: 2320,
    revenue: 185000,
    spend: 51000,
    roas: 3.63,
  },
  {
    id: "6",
    name: "Canada",
    impressions: 800000,
    clicks: 27000,
    ctr: 3.38,
    conversions: 530,
    revenue: 40000,
    spend: 11000,
    roas: 3.64,
  },
  {
    id: "7",
    name: "United Kingdom",
    impressions: 1250000,
    clicks: 35000,
    ctr: 2.8,
    conversions: 720,
    revenue: 62000,
    spend: 19500,
    roas: 3.18,
  },
  {
    id: "8",
    name: "Germany",
    impressions: 950000,
    clicks: 26500,
    ctr: 2.79,
    conversions: 550,
    revenue: 47500,
    spend: 14800,
    roas: 3.21,
  },
  {
    id: "9",
    name: "France",
    impressions: 650000,
    clicks: 17000,
    ctr: 2.62,
    conversions: 350,
    revenue: 28500,
    spend: 8200,
    roas: 3.48,
  },
  {
    id: "10",
    name: "Japan",
    impressions: 750000,
    clicks: 19500,
    ctr: 2.6,
    conversions: 430,
    revenue: 35000,
    spend: 11500,
    roas: 3.04,
  },
  {
    id: "11",
    name: "Australia",
    impressions: 620000,
    clicks: 15800,
    ctr: 2.55,
    conversions: 340,
    revenue: 27500,
    spend: 9200,
    roas: 2.99,
  },
  {
    id: "12",
    name: "South Korea",
    impressions: 280000,
    clicks: 6700,
    ctr: 2.39,
    conversions: 150,
    revenue: 12000,
    spend: 4100,
    roas: 2.93,
  },
  {
    id: "13",
    name: "Brazil",
    impressions: 520000,
    clicks: 15200,
    ctr: 2.92,
    conversions: 360,
    revenue: 28000,
    spend: 9800,
    roas: 2.86,
  },
  {
    id: "14",
    name: "Mexico",
    impressions: 460000,
    clicks: 13300,
    ctr: 2.89,
    conversions: 320,
    revenue: 24000,
    spend: 8400,
    roas: 2.86,
  },
  {
    id: "15",
    name: "Spain",
    impressions: 380000,
    clicks: 10200,
    ctr: 2.68,
    conversions: 210,
    revenue: 17500,
    spend: 5800,
    roas: 3.02,
  },
  {
    id: "16",
    name: "Italy",
    impressions: 320000,
    clicks: 8800,
    ctr: 2.75,
    conversions: 180,
    revenue: 15000,
    spend: 4900,
    roas: 3.06,
  },
  {
    id: "17",
    name: "Netherlands",
    ításions: 290000,
    clicks: 8200,
    ctr: 2.83,
    conversions: 170,
    revenue: 14000,
    spend: 4600,
    roas: 3.04,
  },
  {
    id: "18",
    name: "Sweden",
    impressions: 240000,
    clicks: 6900,
    ctr: 2.88,
    conversions: 145,
    revenue: 12000,
    spend: 3900,
    roas: 3.08,
  },
  {
    id: "19",
    name: "Singapore",
    impressions: 180000,
    clicks: 4800,
    ctr: 2.67,
    conversions: 105,
    revenue: 8500,
    spend: 2800,
    roas: 3.04,
  },
  {
    id: "20",
    name: "India",
    impressions: 420000,
    clicks: 10500,
    ctr: 2.5,
    conversions: 230,
    revenue: 18000,
    spend: 6200,
    roas: 2.9,
  },
  {
    id: "21",
    name: "China",
    impressions: 380000,
    clicks: 9200,
    ctr: 2.42,
    conversions: 200,
    revenue: 16500,
    spend: 5700,
    roas: 2.89,
  },
  {
    id: "22",
    name: "South Africa",
    impressions: 210000,
    clicks: 6100,
    ctr: 2.9,
    conversions: 140,
    revenue: 11000,
    spend: 3800,
    roas: 2.89,
  },
  {
    id: "23",
    name: "New Zealand",
    impressions: 150000,
    clicks: 3800,
    ctr: 2.53,
    conversions: 85,
    revenue: 6800,
    spend: 2300,
    roas: 2.96,
  },
  {
    id: "24",
    name: "Poland",
    impressions: 270000,
    clicks: 7400,
    ctr: 2.74,
    conversions: 155,
    revenue: 13000,
    spend: 4300,
    roas: 3.02,
  },
  {
    id: "25",
    name: "Belgium",
    impressions: 190000,
    clicks: 5300,
    ctr: 2.79,
    conversions: 110,
    revenue: 9200,
    spend: 3100,
    roas: 2.97,
  },
];

// Mock Creative Performance Data
export const mockCreativePerformance = [
  {
    id: "1",
    name: "Video - Product Demo 30s",
    impressions: 2180000,
    clicks: 89500,
    ctr: 4.11,
    conversions: 1850,
    revenue: 142000,
    spend: 38500,
    roas: 3.69,
  },
  {
    id: "2",
    name: "Carousel - Feature Highlights",
    impressions: 1920000,
    clicks: 65800,
    ctr: 3.43,
    conversions: 1320,
    revenue: 105000,
    spend: 29500,
    roas: 3.56,
  },
  {
    id: "3",
    name: "Static - Sale Announcement",
    impressions: 2450000,
    clicks: 58200,
    ctr: 2.38,
    conversions: 980,
    revenue: 78500,
    spend: 24200,
    roas: 3.24,
  },
  {
    id: "4",
    name: "Video - Testimonial 15s",
    impressions: 1580000,
    clicks: 52500,
    ctr: 3.32,
    conversions: 1180,
    revenue: 96000,
    spend: 27300,
    roas: 3.52,
  },
  {
    id: "5",
    name: "Collection - Product Grid",
    impressions: 1420000,
    clicks: 44800,
    ctr: 3.15,
    conversions: 920,
    revenue: 71500,
    spend: 22800,
    roas: 3.14,
  },
];
