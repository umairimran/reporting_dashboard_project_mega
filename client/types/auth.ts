
export interface User {
    id: string;
    email: string;
    role: 'admin' | 'client';
    is_active: boolean;
    full_name?: string;
    // Add other fields from backend model if needed
}

export interface LoginCredentials {
    email: string;
    password: string;
}

export interface RegisterData extends LoginCredentials {
    role: 'admin' | 'client';
}
