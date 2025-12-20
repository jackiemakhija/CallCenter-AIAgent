-- Bronze Layer: Raw Email Data
-- Stores unprocessed emails as received from Power Automate

CREATE TABLE bronze_emails (
    -- Primary identifiers
    email_id STRING NOT NULL COMMENT 'Unique email identifier from Outlook',
    ingestion_timestamp TIMESTAMP NOT NULL COMMENT 'When email was ingested into lakehouse',
    
    -- Email metadata
    received_timestamp TIMESTAMP NOT NULL COMMENT 'When email was received in Outlook',
    sender_email STRING NOT NULL COMMENT 'Email address of sender',
    sender_name STRING COMMENT 'Display name of sender',
    subject STRING COMMENT 'Email subject line',
    body_text STRING COMMENT 'Plain text body content',
    body_html STRING COMMENT 'HTML body content',
    
    -- Email properties
    has_attachments BOOLEAN DEFAULT FALSE COMMENT 'Whether email has attachments',
    attachment_count INT DEFAULT 0 COMMENT 'Number of attachments',
    attachment_names ARRAY<STRING> COMMENT 'List of attachment filenames',
    conversation_id STRING COMMENT 'Outlook conversation thread ID',
    importance STRING COMMENT 'Email importance: Normal, High, Low',
    
    -- Source tracking
    source_folder STRING COMMENT 'Outlook folder path',
    message_id STRING COMMENT 'Internet message ID',
    in_reply_to STRING COMMENT 'Message ID this email replies to',
    
    -- Raw data
    raw_json STRING COMMENT 'Complete raw email JSON from Power Automate',
    
    -- Partitioning
    ingestion_date DATE NOT NULL COMMENT 'Date partition (YYYY-MM-DD)'
) 
USING DELTA
PARTITIONED BY (ingestion_date)
COMMENT 'Bronze layer: Raw email data from Outlook via Power Automate'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'delta.logRetentionDuration' = 'interval 90 days',
    'delta.deletedFileRetentionDuration' = 'interval 7 days'
);

-- Create unique constraint
ALTER TABLE bronze_emails 
ADD CONSTRAINT bronze_emails_pk PRIMARY KEY (email_id, ingestion_date);

-- Optimize for queries
OPTIMIZE bronze_emails ZORDER BY (received_timestamp, sender_email);

-- Sample insert statement for testing
-- INSERT INTO bronze_emails VALUES (
--     'email_001',
--     current_timestamp(),
--     timestamp('2024-01-15 10:30:00'),
--     'customer@example.com',
--     'John Doe',
--     'Where is my order #12345?',
--     'Hi, I ordered a product last week but haven''t received tracking information. Order #12345.',
--     '<html><body>Hi, I ordered a product last week...</body></html>',
--     false,
--     0,
--     array(),
--     'conversation_001',
--     'Normal',
--     'Inbox',
--     'msg_001@outlook.com',
--     null,
--     '{"raw": "data"}',
--     date('2024-01-15')
-- );
