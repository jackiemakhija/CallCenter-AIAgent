-- Customers Table
-- Synced from Shopify, enriched with support history

CREATE TABLE customers (
    -- Primary identifier
    customer_id STRING NOT NULL COMMENT 'Unique customer ID (from Shopify)',
    
    -- Basic information
    email STRING NOT NULL COMMENT 'Primary email address',
    alternate_emails ARRAY<STRING> COMMENT 'Additional email addresses',
    first_name STRING,
    last_name STRING,
    full_name STRING,
    phone STRING COMMENT 'Primary phone number',
    alternate_phones ARRAY<STRING> COMMENT 'Additional phone numbers',
    
    -- Shopify data
    shopify_id BIGINT COMMENT 'Shopify customer ID',
    created_at TIMESTAMP COMMENT 'Account creation date',
    updated_at TIMESTAMP COMMENT 'Last update from Shopify',
    
    -- Customer status
    status STRING DEFAULT 'active' COMMENT 'active, inactive, blocked',
    accepts_marketing BOOLEAN DEFAULT FALSE,
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE,
    
    -- Segmentation
    customer_tier STRING COMMENT 'VIP, Regular, New, At-Risk',
    loyalty_points INT DEFAULT 0,
    vip_status BOOLEAN DEFAULT FALSE,
    
    -- Purchase history (from Shopify)
    total_orders INT DEFAULT 0,
    total_spent DECIMAL(10,2) DEFAULT 0.00,
    average_order_value DECIMAL(10,2) DEFAULT 0.00,
    first_order_date DATE,
    last_order_date DATE,
    days_since_last_order INT,
    
    -- Address information
    default_address STRUCT<
        address1: STRING,
        address2: STRING,
        city: STRING,
        province: STRING,
        country: STRING,
        zip: STRING
    >,
    addresses ARRAY<STRUCT<
        address1: STRING,
        address2: STRING,
        city: STRING,
        province: STRING,
        country: STRING,
        zip: STRING
    >>,
    
    -- Support history
    total_tickets INT DEFAULT 0 COMMENT 'Total support tickets',
    open_tickets INT DEFAULT 0 COMMENT 'Currently open tickets',
    total_emails_received INT DEFAULT 0,
    total_chats INT DEFAULT 0,
    
    -- Last interactions
    last_email_date DATE,
    last_chat_date DATE,
    last_ticket_date DATE,
    last_interaction_date DATE,
    
    -- Sentiment analysis
    overall_sentiment STRING COMMENT 'Positive, Neutral, Negative',
    average_sentiment_score DOUBLE COMMENT '-1.0 to 1.0',
    satisfaction_score DOUBLE COMMENT 'Average CSAT score',
    satisfaction_count INT DEFAULT 0 COMMENT 'Number of CSAT responses',
    
    -- Risk indicators
    is_at_risk BOOLEAN DEFAULT FALSE COMMENT 'At risk of churning',
    risk_score DOUBLE COMMENT '0-1 churn risk score',
    risk_factors ARRAY<STRING> COMMENT 'Reasons for risk',
    
    -- Communication preferences
    preferred_channel STRING COMMENT 'email, chat, phone',
    preferred_language STRING DEFAULT 'en',
    timezone STRING COMMENT 'Customer timezone',
    do_not_contact BOOLEAN DEFAULT FALSE,
    
    -- Tags and notes
    tags ARRAY<STRING> COMMENT 'Shopify and custom tags',
    notes STRING COMMENT 'Internal notes',
    
    -- Data quality
    data_quality_score DOUBLE COMMENT '0-1 completeness score',
    last_data_quality_check TIMESTAMP,
    
    -- Sync metadata
    last_synced_from_shopify TIMESTAMP,
    sync_status STRING DEFAULT 'synced',
    
    -- Partitioning
    customer_since_date DATE NOT NULL COMMENT 'Customer creation date for partitioning'
) 
USING DELTA
PARTITIONED BY (customer_tier)
COMMENT 'Customer master data synced from Shopify with support history'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'delta.logRetentionDuration' = 'interval 365 days'
);

-- Primary key
ALTER TABLE customers 
ADD CONSTRAINT customers_pk PRIMARY KEY (customer_id);

-- Unique constraint on email
ALTER TABLE customers 
ADD CONSTRAINT customers_email_unique UNIQUE (email);

-- Optimize
OPTIMIZE customers ZORDER BY (email, shopify_id, last_interaction_date);

-- Indexes
CREATE INDEX idx_customer_email ON customers (email);
CREATE INDEX idx_customer_shopify ON customers (shopify_id);
CREATE INDEX idx_customer_tier ON customers (customer_tier);
CREATE INDEX idx_customer_risk ON customers (is_at_risk);
