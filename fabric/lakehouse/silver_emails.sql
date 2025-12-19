-- Silver Layer: Enriched Email Data
-- Cleaned, validated, and enriched email data with customer matching

CREATE TABLE silver_emails (
    -- Primary identifiers (from bronze)
    email_id STRING NOT NULL COMMENT 'Unique email identifier',
    ingestion_timestamp TIMESTAMP NOT NULL COMMENT 'Original ingestion timestamp',
    received_timestamp TIMESTAMP NOT NULL COMMENT 'Email received timestamp',
    
    -- Email content (cleaned)
    sender_email STRING NOT NULL COMMENT 'Validated sender email',
    sender_name STRING COMMENT 'Cleaned sender name',
    subject STRING COMMENT 'Cleaned subject line',
    body_text STRING COMMENT 'Cleaned plain text body',
    body_preview STRING COMMENT 'First 200 chars for preview',
    
    -- Email properties
    has_attachments BOOLEAN DEFAULT FALSE,
    attachment_count INT DEFAULT 0,
    attachment_names ARRAY<STRING>,
    conversation_id STRING,
    importance STRING,
    
    -- Customer matching (enrichment)
    customer_id STRING COMMENT 'Matched customer ID from Shopify',
    customer_email STRING COMMENT 'Primary customer email',
    customer_name STRING COMMENT 'Customer full name',
    customer_phone STRING COMMENT 'Customer phone number',
    is_known_customer BOOLEAN DEFAULT FALSE COMMENT 'Whether customer exists in system',
    customer_lifetime_value DECIMAL(10,2) COMMENT 'Total customer spending',
    customer_order_count INT COMMENT 'Number of orders',
    
    -- Content extraction (using regex/NLP)
    mentioned_order_numbers ARRAY<STRING> COMMENT 'Order numbers found in email',
    mentioned_tracking_numbers ARRAY<STRING> COMMENT 'Tracking numbers found',
    mentioned_product_names ARRAY<STRING> COMMENT 'Product names mentioned',
    extracted_phone_numbers ARRAY<STRING> COMMENT 'Phone numbers extracted',
    extracted_urls ARRAY<STRING> COMMENT 'URLs extracted',
    
    -- Sentiment analysis (basic)
    sentiment_score DOUBLE COMMENT 'Sentiment score -1.0 to 1.0',
    sentiment_label STRING COMMENT 'Positive, Neutral, Negative',
    urgency_indicators ARRAY<STRING> COMMENT 'Urgent, ASAP, Immediately, etc.',
    
    -- Email quality
    is_valid_email BOOLEAN DEFAULT TRUE COMMENT 'Passes validation checks',
    is_spam BOOLEAN DEFAULT FALSE COMMENT 'Detected as spam',
    is_auto_reply BOOLEAN DEFAULT FALSE COMMENT 'Detected as auto-reply',
    language_detected STRING DEFAULT 'en' COMMENT 'Detected language code',
    
    -- Processing metadata
    processing_timestamp TIMESTAMP NOT NULL COMMENT 'When silver processing completed',
    processing_duration_ms LONG COMMENT 'Processing time in milliseconds',
    
    -- Partitioning
    processing_date DATE NOT NULL COMMENT 'Processing date partition'
) 
USING DELTA
PARTITIONED BY (processing_date)
COMMENT 'Silver layer: Enriched and validated email data'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'delta.logRetentionDuration' = 'interval 90 days'
);

-- Primary key
ALTER TABLE silver_emails 
ADD CONSTRAINT silver_emails_pk PRIMARY KEY (email_id, processing_date);

-- Optimize for common queries
OPTIMIZE silver_emails ZORDER BY (customer_id, received_timestamp);

-- Create indexes for performance
CREATE INDEX idx_silver_customer ON silver_emails (customer_id);
CREATE INDEX idx_silver_sender ON silver_emails (sender_email);
CREATE INDEX idx_silver_received ON silver_emails (received_timestamp);
