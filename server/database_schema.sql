-- ============================================================================
-- DATABASE SCHEMA FOR DASHBOARD APPLICATION
-- ============================================================================
-- Database: dashboard_db
-- PostgreSQL Version: 14+
-- Date: December 13, 2025
-- ============================================================================

-- ============================================================================
-- SECTION 1: EXTENSIONS AND FUNCTIONS
-- ============================================================================

-- Enable UUID extension for generating UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

-- ============================================================================
-- SECTION 2: USER MANAGEMENT TABLES
-- ============================================================================

-- Users table - stores admin and client user accounts
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'client')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_users_email_unique ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE users IS 'Authenticated users (admins and clients)';
COMMENT ON COLUMN users.role IS 'User role: admin or client';

-- ============================================================================
-- SECTION 3: CLIENT MANAGEMENT TABLES
-- ============================================================================

-- Clients table
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'disabled')),
    user_id UUID REFERENCES users(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_clients_name ON clients(name);
CREATE INDEX idx_clients_status ON clients(status);
CREATE INDEX idx_clients_user_id ON clients(user_id);

CREATE TRIGGER update_clients_updated_at 
    BEFORE UPDATE ON clients 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE clients IS 'Client companies with associated user accounts';

-- Client settings table - stores CPM and other configurations
CREATE TABLE client_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON UPDATE CASCADE ON DELETE CASCADE,
    cpm DECIMAL(10,4) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    effective_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_client_settings_client_id ON client_settings(client_id);
CREATE INDEX idx_client_settings_effective_date ON client_settings(effective_date);

CREATE TRIGGER update_client_settings_updated_at 
    BEFORE UPDATE ON client_settings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE client_settings IS 'Client-specific CPM rates and configuration';
COMMENT ON COLUMN client_settings.cpm IS 'Client CPM rate (e.g., 15.0000)';

-- ============================================================================
-- SECTION 4: CAMPAIGN HIERARCHY TABLES
-- ============================================================================

-- Campaigns table
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON UPDATE CASCADE ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    source VARCHAR(50) NOT NULL CHECK (source IN ('surfside', 'vibe', 'facebook')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(client_id, name, source)
);

CREATE UNIQUE INDEX idx_campaign_client_name_source ON campaigns(client_id, name, source);
CREATE INDEX idx_campaigns_client_id ON campaigns(client_id);
CREATE INDEX idx_campaigns_source ON campaigns(source);

CREATE TRIGGER update_campaigns_updated_at 
    BEFORE UPDATE ON campaigns 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE campaigns IS 'Marketing campaigns from all sources';
COMMENT ON COLUMN campaigns.source IS 'Data source: surfside, vibe, or facebook';

-- Strategies table
CREATE TABLE strategies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON UPDATE CASCADE ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(campaign_id, name)
);

CREATE UNIQUE INDEX idx_strategy_campaign_name ON strategies(campaign_id, name);
CREATE INDEX idx_strategies_campaign_id ON strategies(campaign_id);

CREATE TRIGGER update_strategies_updated_at 
    BEFORE UPDATE ON strategies 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE strategies IS 'Strategies within campaigns';

-- Placements table
CREATE TABLE placements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    strategy_id UUID NOT NULL REFERENCES strategies(id) ON UPDATE CASCADE ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(strategy_id, name)
);

CREATE UNIQUE INDEX idx_placement_strategy_name ON placements(strategy_id, name);
CREATE INDEX idx_placements_strategy_id ON placements(strategy_id);

CREATE TRIGGER update_placements_updated_at 
    BEFORE UPDATE ON placements 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE placements IS 'Ad placements within strategies';

-- Creatives table
CREATE TABLE creatives (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    placement_id UUID NOT NULL REFERENCES placements(id) ON UPDATE CASCADE ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    preview_url TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(placement_id, name)
);

CREATE UNIQUE INDEX idx_creative_placement_name ON creatives(placement_id, name);
CREATE INDEX idx_creatives_placement_id ON creatives(placement_id);

CREATE TRIGGER update_creatives_updated_at 
    BEFORE UPDATE ON creatives 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE creatives IS 'Creative assets within placements';

-- ============================================================================
-- SECTION 5: METRICS TABLES
-- ============================================================================

-- Daily metrics table - core performance data
CREATE TABLE daily_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON UPDATE CASCADE ON DELETE CASCADE,
    date DATE NOT NULL,
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON UPDATE CASCADE ON DELETE CASCADE,
    strategy_id UUID NOT NULL REFERENCES strategies(id) ON UPDATE CASCADE ON DELETE CASCADE,
    placement_id UUID NOT NULL REFERENCES placements(id) ON UPDATE CASCADE ON DELETE CASCADE,
    creative_id UUID NOT NULL REFERENCES creatives(id) ON UPDATE CASCADE ON DELETE CASCADE,
    source VARCHAR(50) NOT NULL CHECK (source IN ('surfside', 'vibe', 'facebook')),
    
    -- Raw metrics
    impressions BIGINT NOT NULL DEFAULT 0,
    clicks BIGINT NOT NULL DEFAULT 0,
    conversions BIGINT NOT NULL DEFAULT 0,
    conversion_revenue DECIMAL(12,2) NOT NULL DEFAULT 0,
    
    -- Calculated metrics
    ctr DECIMAL(12,6),
    spend DECIMAL(12,2),
    cpc DECIMAL(12,4),
    cpa DECIMAL(12,4),
    roas DECIMAL(12,4),
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    UNIQUE(client_id, date, campaign_id, strategy_id, placement_id, creative_id, source)
);

CREATE INDEX idx_metrics_client_date ON daily_metrics(client_id, date DESC);
CREATE INDEX idx_metrics_campaign ON daily_metrics(campaign_id, date DESC);
CREATE INDEX idx_metrics_strategy ON daily_metrics(strategy_id, date DESC);
CREATE INDEX idx_metrics_placement ON daily_metrics(placement_id);
CREATE INDEX idx_metrics_creative ON daily_metrics(creative_id);
CREATE INDEX idx_metrics_date ON daily_metrics(date DESC);
CREATE INDEX idx_metrics_source ON daily_metrics(source);

CREATE TRIGGER update_daily_metrics_updated_at 
    BEFORE UPDATE ON daily_metrics 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE daily_metrics IS 'Daily performance metrics from all sources';
COMMENT ON COLUMN daily_metrics.source IS 'Data source: surfside, vibe, or facebook';
COMMENT ON COLUMN daily_metrics.spend IS 'CPM-adjusted spend: (impressions / 1000) * client_cpm';

-- Weekly summaries table
CREATE TABLE weekly_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON UPDATE CASCADE ON DELETE CASCADE,
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    
    -- Aggregated metrics
    impressions BIGINT NOT NULL DEFAULT 0,
    clicks BIGINT NOT NULL DEFAULT 0,
    conversions BIGINT NOT NULL DEFAULT 0,
    revenue DECIMAL(12,2) NOT NULL DEFAULT 0,
    spend DECIMAL(12,2) NOT NULL DEFAULT 0,
    
    -- Calculated metrics
    ctr DECIMAL(12,6),
    cpc DECIMAL(12,4),
    cpa DECIMAL(12,4),
    roas DECIMAL(12,4),
    
    -- Top performers
    top_campaigns JSONB,
    top_creatives JSONB,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    UNIQUE(client_id, week_start)
);

CREATE INDEX idx_weekly_summaries_client_week ON weekly_summaries(client_id, week_start DESC);

COMMENT ON TABLE weekly_summaries IS 'Aggregated weekly performance summaries';

-- Monthly summaries table
CREATE TABLE monthly_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON UPDATE CASCADE ON DELETE CASCADE,
    month_start DATE NOT NULL,
    month_end DATE NOT NULL,
    
    -- Aggregated metrics
    impressions BIGINT NOT NULL DEFAULT 0,
    clicks BIGINT NOT NULL DEFAULT 0,
    conversions BIGINT NOT NULL DEFAULT 0,
    revenue DECIMAL(12,2) NOT NULL DEFAULT 0,
    spend DECIMAL(12,2) NOT NULL DEFAULT 0,
    
    -- Calculated metrics
    ctr DECIMAL(12,6),
    cpc DECIMAL(12,4),
    cpa DECIMAL(12,4),
    roas DECIMAL(12,4),
    
    -- Top performers
    top_campaigns JSONB,
    top_creatives JSONB,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    UNIQUE(client_id, month_start)
);

CREATE INDEX idx_monthly_summaries_client_month ON monthly_summaries(client_id, month_start DESC);

COMMENT ON TABLE monthly_summaries IS 'Aggregated monthly performance summaries';

-- ============================================================================
-- SECTION 6: STAGING TABLES (FOR ETL PROCESS)
-- ============================================================================

-- Staging table for raw data ingestion
CREATE TABLE staging_media_raw (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ingestion_run_id UUID NOT NULL,
    client_id UUID REFERENCES clients(id) ON UPDATE CASCADE ON DELETE CASCADE,
    source VARCHAR(50) NOT NULL CHECK (source IN ('surfside', 'vibe', 'facebook')),
    
    -- Raw CSV/API data
    date DATE NOT NULL,
    campaign_name VARCHAR(255),
    strategy_name VARCHAR(255),
    placement_name VARCHAR(255),
    creative_name VARCHAR(255),
    
    -- Raw metrics
    impressions BIGINT DEFAULT 0,
    clicks BIGINT DEFAULT 0,
    ctr DECIMAL(12,6),
    conversions BIGINT DEFAULT 0,
    conversion_revenue DECIMAL(12,2) DEFAULT 0,
    
    -- Source-specific data (JSONB for flexibility)
    raw_data JSONB,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_staging_ingestion_run ON staging_media_raw(ingestion_run_id);
CREATE INDEX idx_staging_client_date ON staging_media_raw(client_id, date);
CREATE INDEX idx_staging_source ON staging_media_raw(source);

COMMENT ON TABLE staging_media_raw IS 'Temporary staging table for data ingestion from all sources';
COMMENT ON COLUMN staging_media_raw.raw_data IS 'Original raw data in JSON format for debugging';

-- ============================================================================
-- SECTION 7: INGESTION TRACKING TABLES
-- ============================================================================

-- Ingestion logs table
CREATE TABLE ingestion_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('success', 'failed', 'partial', 'processing')),
    message TEXT,
    records_loaded INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP,
    file_name VARCHAR(255),
    source VARCHAR(50) NOT NULL CHECK (source IN ('surfside', 'vibe', 'facebook')),
    client_id UUID REFERENCES clients(id) ON UPDATE CASCADE ON DELETE SET NULL,
    
    -- Error resolution tracking
    resolution_status VARCHAR(20) CHECK (resolution_status IN ('unresolved', 'resolved', 'ignored')),
    resolution_notes TEXT,
    resolved_at TIMESTAMP,
    resolved_by UUID REFERENCES users(id) ON UPDATE CASCADE ON DELETE SET NULL,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ingestion_logs_status ON ingestion_logs(status);
CREATE INDEX idx_ingestion_logs_run_date ON ingestion_logs(run_date DESC);
CREATE INDEX idx_ingestion_logs_client ON ingestion_logs(client_id);
CREATE INDEX idx_ingestion_logs_source ON ingestion_logs(source);
CREATE INDEX idx_ingestion_logs_resolution ON ingestion_logs(resolution_status);

COMMENT ON TABLE ingestion_logs IS 'Tracks all data ingestion attempts from all sources';
COMMENT ON COLUMN ingestion_logs.source IS 'Data source: surfside, vibe, or facebook';
COMMENT ON COLUMN ingestion_logs.resolution_status IS 'Error resolution status: unresolved, resolved, or ignored';

-- ============================================================================
-- SECTION 8: VIBE API SPECIFIC TABLES
-- ============================================================================

-- Vibe API credentials table (for multi-client support)
CREATE TABLE vibe_credentials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON UPDATE CASCADE ON DELETE CASCADE,
    api_key TEXT NOT NULL,
    advertiser_id VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_vibe_credentials_client ON vibe_credentials(client_id);
CREATE INDEX idx_vibe_credentials_active ON vibe_credentials(is_active);

CREATE TRIGGER update_vibe_credentials_updated_at 
    BEFORE UPDATE ON vibe_credentials 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE vibe_credentials IS 'Stores Vibe API credentials per client';

-- Vibe API report tracking
CREATE TABLE vibe_report_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON UPDATE CASCADE ON DELETE CASCADE,
    report_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('created', 'processing', 'done', 'error')),
    request_params JSONB,
    download_url TEXT,
    url_expiration TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_vibe_reports_client ON vibe_report_requests(client_id);
CREATE INDEX idx_vibe_reports_status ON vibe_report_requests(status);
CREATE INDEX idx_vibe_reports_report_id ON vibe_report_requests(report_id);

COMMENT ON TABLE vibe_report_requests IS 'Tracks Vibe API async report requests';

-- ============================================================================
-- SECTION 9: FACEBOOK UPLOAD TRACKING
-- ============================================================================

-- Uploaded files table (for Facebook and other manual uploads)
CREATE TABLE uploaded_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON UPDATE CASCADE ON DELETE CASCADE,
    source VARCHAR(50) NOT NULL DEFAULT 'facebook',
    original_filename VARCHAR(500) NOT NULL,
    file_size INTEGER,
    file_path VARCHAR(1000),
    uploaded_by UUID REFERENCES users(id) ON UPDATE CASCADE ON DELETE SET NULL,
    upload_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    processed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_uploaded_files_client ON uploaded_files(client_id);
CREATE INDEX idx_uploaded_files_status ON uploaded_files(upload_status);
CREATE INDEX idx_uploaded_files_uploaded_by ON uploaded_files(uploaded_by);
CREATE INDEX idx_uploaded_files_source ON uploaded_files(source);

COMMENT ON TABLE uploaded_files IS 'Tracks manually uploaded files (Facebook, etc.)';

-- ============================================================================
-- SECTION 10: AUDIT LOGGING
-- ============================================================================

-- Audit logs table - tracks all user actions for security and compliance
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON UPDATE CASCADE ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

COMMENT ON TABLE audit_logs IS 'Tracks all user actions for security and compliance';
COMMENT ON COLUMN audit_logs.action IS 'Action performed: login, create_client, update_campaign, etc.';
COMMENT ON COLUMN audit_logs.old_values IS 'Previous state for updates/deletes';
COMMENT ON COLUMN audit_logs.new_values IS 'New state for creates/updates';

-- ============================================================================
-- SECTION 11: ROW-LEVEL SECURITY (OPTIONAL)
-- ============================================================================

-- Enable Row Level Security on sensitive tables
ALTER TABLE daily_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE weekly_summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE monthly_summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE placements ENABLE ROW LEVEL SECURITY;
ALTER TABLE creatives ENABLE ROW LEVEL SECURITY;

-- Example RLS policy (implement after auth system is ready)
-- CREATE POLICY client_isolation ON daily_metrics
--     FOR SELECT
--     USING (client_id = current_setting('app.current_client_id')::uuid);

-- ============================================================================
-- SECTION 12: UTILITY VIEWS (OPTIONAL)
-- ============================================================================

-- View for aggregated metrics by campaign
CREATE OR REPLACE VIEW v_campaign_metrics AS
SELECT 
    c.id AS campaign_id,
    c.name AS campaign_name,
    c.source,
    cl.id AS client_id,
    cl.name AS client_name,
    dm.date,
    SUM(dm.impressions) AS total_impressions,
    SUM(dm.clicks) AS total_clicks,
    SUM(dm.conversions) AS total_conversions,
    SUM(dm.spend) AS total_spend,
    SUM(dm.conversion_revenue) AS total_revenue,
    CASE 
        WHEN SUM(dm.impressions) > 0 
        THEN (SUM(dm.clicks)::DECIMAL / SUM(dm.impressions)) * 100 
        ELSE 0 
    END AS ctr,
    CASE 
        WHEN SUM(dm.clicks) > 0 
        THEN SUM(dm.spend) / SUM(dm.clicks) 
        ELSE 0 
    END AS cpc,
    CASE 
        WHEN SUM(dm.conversions) > 0 
        THEN SUM(dm.spend) / SUM(dm.conversions) 
        ELSE 0 
    END AS cpa,
    CASE 
        WHEN SUM(dm.spend) > 0 
        THEN (SUM(dm.conversion_revenue) / SUM(dm.spend)) * 100 
        ELSE 0 
    END AS roas
FROM daily_metrics dm
JOIN campaigns c ON dm.campaign_id = c.id
JOIN clients cl ON dm.client_id = cl.id
GROUP BY c.id, c.name, c.source, cl.id, cl.name, dm.date;

COMMENT ON VIEW v_campaign_metrics IS 'Aggregated metrics by campaign and date';

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

-- Verification queries (run these to verify schema creation)
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;
-- SELECT * FROM information_schema.table_constraints WHERE constraint_type = 'FOREIGN KEY';
