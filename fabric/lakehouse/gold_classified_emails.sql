-- Gold Layer: AI-Classified Email Data
-- Business-ready data with AI classification, routing, and responses

CREATE TABLE gold_classified_emails (
    -- Primary identifiers
    ticket_id STRING NOT NULL COMMENT 'Unique ticket ID (generated)',
    email_id STRING NOT NULL COMMENT 'Reference to silver_emails',
    customer_id STRING COMMENT 'Customer identifier',
    
    -- Timestamps
    received_timestamp TIMESTAMP NOT NULL COMMENT 'Original email timestamp',
    classified_timestamp TIMESTAMP NOT NULL COMMENT 'AI classification timestamp',
    first_response_timestamp TIMESTAMP COMMENT 'When first response was sent',
    resolved_timestamp TIMESTAMP COMMENT 'When ticket was resolved',
    closed_timestamp TIMESTAMP COMMENT 'When ticket was closed',
    
    -- Customer information
    customer_name STRING,
    customer_email STRING NOT NULL,
    customer_tier STRING COMMENT 'VIP, Regular, New',
    customer_lifetime_value DECIMAL(10,2),
    
    -- Email content
    subject STRING,
    body_preview STRING,
    
    -- AI Classification
    category STRING NOT NULL COMMENT 'order_tracking, returns, product_info, delivery, payment, complaints',
    category_confidence DOUBLE NOT NULL COMMENT 'AI confidence score 0-1',
    subcategory STRING COMMENT 'More specific classification',
    
    -- Priority and routing
    priority STRING NOT NULL COMMENT 'urgent, high, medium, low',
    priority_score INT NOT NULL COMMENT '1-10 priority score',
    assigned_to STRING COMMENT 'Agent ID or queue name',
    assignment_type STRING DEFAULT 'auto' COMMENT 'auto, manual, escalated',
    
    -- Sentiment and tone
    sentiment_label STRING COMMENT 'Positive, Neutral, Negative',
    sentiment_score DOUBLE COMMENT '-1.0 to 1.0',
    emotion_detected STRING COMMENT 'angry, frustrated, happy, confused',
    urgency_level STRING COMMENT 'critical, high, normal, low',
    
    -- Related entities
    order_numbers ARRAY<STRING> COMMENT 'Related order numbers',
    tracking_numbers ARRAY<STRING> COMMENT 'Related tracking numbers',
    product_ids ARRAY<STRING> COMMENT 'Related product IDs',
    
    -- AI-generated response
    suggested_response STRING COMMENT 'AI-generated response text',
    response_template_used STRING COMMENT 'Template ID used',
    auto_response_sent BOOLEAN DEFAULT FALSE COMMENT 'Whether auto-response was sent',
    auto_response_timestamp TIMESTAMP COMMENT 'When auto-response was sent',
    
    -- Human intervention
    requires_human_review BOOLEAN DEFAULT FALSE COMMENT 'Needs human review',
    human_reviewed BOOLEAN DEFAULT FALSE COMMENT 'Has been reviewed by human',
    reviewed_by STRING COMMENT 'Agent who reviewed',
    reviewed_timestamp TIMESTAMP COMMENT 'Review timestamp',
    human_response STRING COMMENT 'Human-written response',
    
    -- Status and lifecycle
    status STRING NOT NULL DEFAULT 'new' COMMENT 'new, in_progress, waiting_customer, resolved, closed',
    resolution_type STRING COMMENT 'auto_resolved, agent_resolved, escalated',
    resolution_notes STRING COMMENT 'Resolution details',
    
    -- SLA tracking
    sla_target_minutes INT COMMENT 'Target response time in minutes',
    sla_deadline_timestamp TIMESTAMP COMMENT 'SLA deadline',
    response_time_minutes INT COMMENT 'Actual response time',
    resolution_time_minutes INT COMMENT 'Time to resolution',
    sla_met BOOLEAN COMMENT 'Whether SLA was met',
    
    -- Follow-up
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    follow_up_notes STRING,
    
    -- Related tickets
    parent_ticket_id STRING COMMENT 'Parent ticket if this is follow-up',
    related_ticket_ids ARRAY<STRING> COMMENT 'Related ticket IDs',
    
    -- Quality metrics
    customer_satisfaction_score INT COMMENT '1-5 rating',
    customer_feedback STRING COMMENT 'Customer feedback text',
    
    -- AI metrics
    ai_processing_time_ms LONG COMMENT 'AI processing duration',
    openai_tokens_used INT COMMENT 'Total tokens consumed',
    openai_cost_usd DECIMAL(10,6) COMMENT 'Cost of OpenAI API calls',
    
    -- Tags and metadata
    tags ARRAY<STRING> COMMENT 'Custom tags for filtering',
    metadata MAP<STRING, STRING> COMMENT 'Additional metadata',
    
    -- Partitioning
    classified_date DATE NOT NULL COMMENT 'Classification date partition'
) 
USING DELTA
PARTITIONED BY (classified_date, category)
COMMENT 'Gold layer: AI-classified and business-ready email tickets'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'delta.logRetentionDuration' = 'interval 365 days',
    'delta.columnMapping.mode' = 'name'
);

-- Primary key
ALTER TABLE gold_classified_emails 
ADD CONSTRAINT gold_classified_pk PRIMARY KEY (ticket_id);

-- Foreign key reference
ALTER TABLE gold_classified_emails 
ADD CONSTRAINT fk_email_id FOREIGN KEY (email_id) REFERENCES silver_emails(email_id);

-- Optimize for dashboard queries
OPTIMIZE gold_classified_emails ZORDER BY (
    classified_timestamp, 
    status, 
    priority, 
    category, 
    customer_id
);

-- Create indexes
CREATE INDEX idx_gold_status ON gold_classified_emails (status);
CREATE INDEX idx_gold_priority ON gold_classified_emails (priority);
CREATE INDEX idx_gold_category ON gold_classified_emails (category);
CREATE INDEX idx_gold_customer ON gold_classified_emails (customer_id);
CREATE INDEX idx_gold_assigned ON gold_classified_emails (assigned_to);
CREATE INDEX idx_gold_sla ON gold_classified_emails (sla_met, sla_deadline_timestamp);
