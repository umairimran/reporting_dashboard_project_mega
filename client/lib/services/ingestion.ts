import { apiClient } from "@/lib/api-client";
import { IngestionLog } from "@/types/dashboard";

interface IngestionLogsResponse {
    total: number;
    logs: any[]; // The backend returns a specific shape, we map it to our frontend type if needed
}

export const ingestionService = {
    // Fetch ingestion logs
    getLogs: async (params?: {
        skip?: number;
        limit?: number;
        source?: string;
        status?: string;
        client_id?: string
    }) => {
        const queryParams = new URLSearchParams();
        if (params?.skip) queryParams.append("skip", params.skip.toString());
        if (params?.limit) queryParams.append("limit", params.limit.toString());
        if (params?.source) queryParams.append("source", params.source);
        if (params?.status) queryParams.append("status", params.status);
        if (params?.client_id) queryParams.append("client_id", params.client_id);

        return apiClient<IngestionLogsResponse>(`/ingestion-logs?${queryParams.toString()}`, { method: "GET" });
    },

    // Upload Facebook Data
    uploadFacebook: async (clientId: string, file: File) => {
        const formData = new FormData();
        formData.append("file", file);
        return apiClient(`/facebook/upload?client_id=${clientId}`, { method: "POST", body: formData });
    },

    // Upload Surfside Data
    uploadSurfside: async (clientId: string, file: File) => {
        const formData = new FormData();
        formData.append("file", file);
        return apiClient(`/surfside/upload?client_id=${clientId}`, { method: "POST", body: formData });
    },

};
