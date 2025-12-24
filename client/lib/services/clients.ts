import { apiClient } from "@/lib/api-client";
import { Client, ClientSettings } from "@/types/dashboard";

interface CreateClientData {
    name: string;
    user_id: string; // Admin can assign a user_id or system generates one? Backend requires user_id. 
    // Looking at backend schema, ClientCreate requires user_id. 
    // For now, we might need to mock or fetch available users. 
    // Or if the backend auto-assigns for "new-user" logic, we'll see.
    // Actually router says: client_data: ClientCreate.
}

interface UpdateClientData {
    name?: string;
    status?: "active" | "disabled";
}

interface CpmSettingData {
    source: "surfside" | "facebook";
    cpm: number;
    currency?: string;
    effective_date?: string;
}

export const clientsService = {
    // Fetch all clients
    getClients: async (skip = 0, limit = 100) => {
        const response = await apiClient<{ total: number; clients: any[] }>(
            `/clients?skip=${skip}&limit=${limit}`,
            { method: "GET" }
        );

        // Map backend snake_case to frontend camelCase
        const mappedClients = response.clients.map(client => ({
            ...client,
            createdAt: client.created_at,
            updatedAt: client.updated_at,
            userId: client.user_id
        })) as Client[];

        return {
            total: response.total,
            clients: mappedClients
        };
    },

    // Get single client with settings
    getClient: async (id: string) => {
        const client = await apiClient<any>(`/clients/${id}`, { method: "GET" });
        return {
            ...client,
            createdAt: client.created_at,
            updatedAt: client.updated_at,
            userId: client.user_id,
            currentCpm: client.current_cpm,
            currentCurrency: client.current_currency
        } as Client & { currentCpm?: number; currentCurrency?: string };
    },

    // Create new client
    createClient: async (data: { name: string; user_id: string }) => {
        return apiClient<Client>("/clients", { method: "POST", body: JSON.stringify(data) });
    },

    // Update client
    updateClient: async (id: string, data: UpdateClientData) => {
        // Determine active/disabled status based on backend requirements
        return apiClient<Client>(`/clients/${id}`, { method: "PUT", body: JSON.stringify(data) });
    },

    // Disable/Delete client
    deleteClient: async (id: string) => {
        return apiClient(`/clients/${id}`, { method: "DELETE" });
    },

    // Get CPM history/settings
    getCpmSettings: async (clientId: string) => {
        return apiClient<ClientSettings[]>(`/clients/${clientId}/cpm/history`, { method: "GET" });
    },

    // Get Latest CPMs (Optimized)
    getLatestCpms: async (clientId: string) => {
        return apiClient<{ surfside: ClientSettings | null; facebook: ClientSettings | null }>(
            `/clients/${clientId}/cpm/latest`,
            { method: "GET" }
        );
    },

    // Add CPM setting
    addCpmSetting: async (clientId: string, data: CpmSettingData) => {
        return apiClient<ClientSettings>(`/clients/${clientId}/cpm`, { method: "POST", body: JSON.stringify(data) });
    },

    // Update CPM setting (for specific source/date)
    updateCpmSetting: async (clientId: string, data: CpmSettingData) => {
        return apiClient<ClientSettings>(`/clients/${clientId}/cpm`, { method: "PUT", body: JSON.stringify(data) });
    }
};
