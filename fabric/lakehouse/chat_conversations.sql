-- Chat Conversations Table
-- Stores chat session metadata from Power Virtual Agents

CREATE TABLE chat_conversations (
    -- Primary identifiers
    conversation_id STRING NOT NULL COMMENT 'Unique conversation ID from PVA',
    session_id STRING COMMENT 'Browser session ID',
    
    -- Timestamps
    started_timestamp TIMESTAMP NOT NULL COMMENT 'Conversation start time',
    ended_timestamp TIMESTAMP COMMENT 'Conversation end time',
    last_activity_timestamp TIMESTAMP NOT NULL COMMENT 'Last message timestamp',
    
    -- Customer information
    customer_id STRING COMMENT 'Matched customer ID',
    customer_email STRING COMMENT 'Customer email if provided',
    customer_name STRING COMMENT 'Customer name if provided',
    visitor_id STRING COMMENT 'Anonymous visitor ID',
    is_authenticated BOOLEAN DEFAULT FALSE COMMENT 'Whether customer logged in',
    
    -- Conversation metadata
    channel STRING NOT NULL COMMENT 'web, mobile, teams, etc.',
    language STRING DEFAULT 'en' COMMENT 'Conversation language',
    device_type STRING COMMENT 'desktop, mobile, tablet',
    browser STRING COMMENT 'Browser user agent',
    
    -- Conversation flow
    bot_id STRING NOT NULL COMMENT 'Power Virtual Agents bot ID',
    initial_topic STRING COMMENT 'First topic triggered',
    topics_triggered ARRAY<STRING> COMMENT 'All topics triggered',
    total_messages INT DEFAULT 0 COMMENT 'Total message count',
    bot_messages INT DEFAULT 0 COMMENT 'Bot message count',
    user_messages INT DEFAULT 0 COMMENT 'User message count',
    
    -- Classification
    primary_intent STRING COMMENT 'Main conversation intent',
    intents_detected ARRAY<STRING> COMMENT 'All detected intents',
    category STRING COMMENT 'order_tracking, returns, etc.',
    subcategory STRING COMMENT 'More specific category',
    
    -- Escalation
    escalated_to_human BOOLEAN DEFAULT FALSE COMMENT 'Whether escalated to agent',
    escalation_timestamp TIMESTAMP COMMENT 'When escalated',
    escalation_reason STRING COMMENT 'Why escalated',
    assigned_agent_id STRING COMMENT 'Assigned human agent',
    
    -- Outcomes
    conversation_outcome STRING COMMENT 'resolved, escalated, abandoned',
    resolution_type STRING COMMENT 'self_service, bot_resolved, agent_resolved',
    customer_satisfied BOOLEAN COMMENT 'Whether customer indicated satisfaction',
    csat_score INT COMMENT '1-5 satisfaction rating',
    csat_feedback STRING COMMENT 'Customer feedback text',
    
    -- Business entities
    order_numbers ARRAY<STRING> COMMENT 'Orders discussed',
    tracking_numbers ARRAY<STRING> COMMENT 'Tracking numbers provided',
    product_ids ARRAY<STRING> COMMENT 'Products discussed',
    
    -- Sentiment
    overall_sentiment STRING COMMENT 'Positive, Neutral, Negative',
    sentiment_score DOUBLE COMMENT '-1.0 to 1.0',
    sentiment_trend STRING COMMENT 'improving, declining, stable',
    
    -- Performance metrics
    duration_seconds INT COMMENT 'Total conversation duration',
    response_time_avg_seconds DOUBLE COMMENT 'Avg bot response time',
    first_response_time_seconds INT COMMENT 'Time to first bot response',
    
    -- AI metrics
    openai_calls_count INT DEFAULT 0 COMMENT 'Number of OpenAI API calls',
    openai_tokens_total INT DEFAULT 0 COMMENT 'Total tokens used',
    openai_cost_usd DECIMAL(10,6) COMMENT 'Total OpenAI cost',
    
    -- Session metadata
    referrer_url STRING COMMENT 'Page where chat started',
    user_agent STRING COMMENT 'Full user agent string',
    ip_address STRING COMMENT 'Customer IP address (hashed)',
    location_country STRING COMMENT 'Detected country',
    location_region STRING COMMENT 'Detected region',
    
    -- Tags
    tags ARRAY<STRING> COMMENT 'Custom tags',
    metadata MAP<STRING, STRING> COMMENT 'Additional metadata',
    
    -- Partitioning
    conversation_date DATE NOT NULL COMMENT 'Conversation start date'
) 
USING DELTA
PARTITIONED BY (conversation_date)
COMMENT 'Chat conversations from Power Virtual Agents'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Primary key
ALTER TABLE chat_conversations 
ADD CONSTRAINT chat_conversations_pk PRIMARY KEY (conversation_id);

-- Optimize
OPTIMIZE chat_conversations ZORDER BY (started_timestamp, customer_id, category);

-- Indexes
CREATE INDEX idx_chat_customer ON chat_conversations (customer_id);
CREATE INDEX idx_chat_outcome ON chat_conversations (conversation_outcome);
CREATE INDEX idx_chat_escalated ON chat_conversations (escalated_to_human);
