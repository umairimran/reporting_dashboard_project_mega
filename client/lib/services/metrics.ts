
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

export const metricsService = {
    getDailyMetrics: async (options: MetricsFetchOptions) => {
        return apiClient<DailyMetric[]>("/metrics/daily", { params: options as any });
    },

    getSummary: async (options: MetricsFetchOptions) => {
        return apiClient<any>("/metrics/summary", { params: options as any });
    }
};
