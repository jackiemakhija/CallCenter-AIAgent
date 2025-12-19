-- Chat Messages Table
-- Individual messages within chat conversations

CREATE TABLE chat_messages (
    -- Primary identifiers
    message_id STRING NOT NULL COMMENT 'Unique message ID',
    conversation_id STRING NOT NULL COMMENT 'Parent conversation ID',
    
    -- Timestamps
    timestamp TIMESTAMP NOT NULL COMMENT 'Message timestamp',
    
    -- Message properties
    sender_type STRING NOT NULL COMMENT 'user, bot, agent',
    sender_id STRING COMMENT 'User/agent ID if known',
    message_text STRING COMMENT 'Message content',
    message_type STRING COMMENT 'text, image, card, quick_reply, etc.',
    
    -- Bot metadata (if sender is bot)
    bot_topic STRING COMMENT 'PVA topic that generated response',
    bot_node STRING COMMENT 'Specific node in topic',
    bot_confidence DOUBLE COMMENT 'Intent confidence score',
    
    -- AI classification
    intent STRING COMMENT 'Detected user intent',
    intent_confidence DOUBLE COMMENT 'Intent confidence 0-1',
    entities_detected ARRAY<STRUCT<entity_type: STRING, entity_value: STRING, confidence: DOUBLE>> COMMENT 'NER results',
    
    -- Sentiment
    sentiment_label STRING COMMENT 'Positive, Neutral, Negative',
    sentiment_score DOUBLE COMMENT '-1.0 to 1.0',
    emotion STRING COMMENT 'Detected emotion',
    
    -- Attachments
    has_attachment BOOLEAN DEFAULT FALSE,
    attachment_type STRING COMMENT 'image, document, etc.',
    attachment_url STRING COMMENT 'URL to attachment',
    
    -- Rich content (for bot responses)
    has_quick_replies BOOLEAN DEFAULT FALSE,
    quick_reply_options ARRAY<STRING> COMMENT 'Quick reply button texts',
    has_adaptive_card BOOLEAN DEFAULT FALSE,
    adaptive_card_json STRING COMMENT 'Adaptive card definition',
    
    -- Business entities extracted
    order_number STRING COMMENT 'Order number if mentioned',
    tracking_number STRING COMMENT 'Tracking number if mentioned',
    product_id STRING COMMENT 'Product ID if mentioned',
    
    -- AI processing
    processed_by_openai BOOLEAN DEFAULT FALSE,
    openai_model STRING COMMENT 'Model used (if any)',
    openai_tokens_input INT COMMENT 'Input tokens',
    openai_tokens_output INT COMMENT 'Output tokens',
    openai_cost_usd DECIMAL(10,6) COMMENT 'Cost for this message',
    processing_time_ms LONG COMMENT 'Processing time',
    
    -- Quality
    flagged_inappropriate BOOLEAN DEFAULT FALSE,
    flagged_reason STRING COMMENT 'Why flagged',
    
    -- Metadata
    metadata MAP<STRING, STRING> COMMENT 'Additional metadata',
    
    -- Partitioning
    message_date DATE NOT NULL COMMENT 'Message date'
) 
USING DELTA
PARTITIONED BY (message_date)
COMMENT 'Individual messages within chat conversations'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Primary key
ALTER TABLE chat_messages 
ADD CONSTRAINT chat_messages_pk PRIMARY KEY (message_id);

-- Foreign key
ALTER TABLE chat_messages 
ADD CONSTRAINT fk_conversation FOREIGN KEY (conversation_id) REFERENCES chat_conversations(conversation_id);

-- Optimize
OPTIMIZE chat_messages ZORDER BY (conversation_id, timestamp);

-- Indexes
CREATE INDEX idx_message_conversation ON chat_messages (conversation_id);
CREATE INDEX idx_message_timestamp ON chat_messages (timestamp);
CREATE INDEX idx_message_sender ON chat_messages (sender_type);
