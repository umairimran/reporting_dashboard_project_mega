
import { apiClient } from "@/lib/api-client";

// Define Types (simplified from backend schemas)
export interface DailyMetric {
    id: string;
    client_id: string;
    client_name: string;
    campaign_name?: string;
    strategy_name?: string;
    placement_name?: string;
    creative_name?: string;
    region_name?: string;
    date: string;

    impressions: number;
    clicks: number;
    conversions: number;
    conversion_revenue: number;
    ctr: number;
    spend: number;
    cpc: number;
    cpa: number;
    roas: number;
    source: string;
}

export interface MetricsFetchOptions {
    start_date: string;
    end_date: string;
    client_id?: string;
    campaign_name?: string;
    source?: string;
    limit?: number;
    offset?: number;
}


export interface PeriodMetrics {
    total_impressions: number;
    total_clicks: number;
    total_conversions: number;
    total_revenue: number;
    total_spend: number;
    overall_ctr: number;
    overall_cpc: number | null;
    overall_cpa: number | null;
    overall_roas: number | null;
}

export interface DashboardSummaryResponse extends PeriodMetrics {
    active_campaigns: number;
    data_sources: string[];
    previous_period: PeriodMetrics | null;
}

export const metricsService = {
    getDailyMetrics: async (options: MetricsFetchOptions) => {
        return apiClient<DailyMetric[]>("/metrics/daily", { params: options as any });
    },

    getSummary: async (options: MetricsFetchOptions) => {
        return apiClient<DashboardSummaryResponse>("/metrics/summary", { params: options as any });
    }
};
