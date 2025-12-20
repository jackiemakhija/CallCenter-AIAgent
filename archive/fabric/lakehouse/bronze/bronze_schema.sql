-- FABRIC LAKEHOUSE: BRONZE LAYER
-- Raw, unprocessed data from inbound channels
-- Retention: 90 days

-- EMAIL MESSAGES (Raw)
CREATE EXTERNAL TABLE bronze_email_raw (
    email_id STRING,
    message_id STRING,
    from_address STRING,
    to_address STRING,
    cc_address STRING,
    subject STRING,
    body STRING,
    received_time TIMESTAMP,
    has_attachments BOOLEAN,
    attachment_count INT,
    attachment_names STRING,  -- JSON array
    is_read BOOLEAN,
    importance STRING,  -- low, normal, high
    categories STRING,  -- JSON array
    raw_json STRING,  -- Full outlook API response
    ingestion_time TIMESTAMP
)
USING PARQUET;

-- CHAT MESSAGES (Raw)
CREATE EXTERNAL TABLE bronze_chat_raw (
    chat_id STRING,
    conversation_id STRING,
    user_id STRING,
    user_name STRING,
    user_email STRING,
    message_text STRING,
    message_timestamp TIMESTAMP,
    is_bot_response BOOLEAN,
    session_id STRING,
    page_url STRING,
    referrer STRING,
    raw_json STRING,  -- Full PVA payload
    ingestion_time TIMESTAMP
)
USING PARQUET;

-- SHOPIFY ORDERS (Raw)
CREATE EXTERNAL TABLE bronze_shopify_orders_raw (
    order_id STRING,
    order_number INT,
    customer_id STRING,
    customer_email STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    status STRING,  -- pending, processing, shipped, delivered, cancelled
    fulfillment_status STRING,
    total_price DECIMAL(10,2),
    currency STRING,
    order_items STRING,  -- JSON array
    shipping_address STRING,  -- JSON
    billing_address STRING,  -- JSON
    raw_json STRING,
    ingestion_time TIMESTAMP
)
USING PARQUET;

-- FEDEX/UPS TRACKING (Raw)
CREATE EXTERNAL TABLE bronze_tracking_raw (
    tracking_id STRING,
    tracking_number STRING,
    carrier STRING,  -- fedex, ups
    order_id STRING,
    status STRING,  -- picked_up, in_transit, out_for_delivery, delivered, exception
    current_location STRING,
    estimated_delivery TIMESTAMP,
    latest_event TIMESTAMP,
    latest_event_description STRING,
    raw_json STRING,
    ingestion_time TIMESTAMP
)
USING PARQUET;

-- STRIPE TRANSACTIONS (Raw)
CREATE EXTERNAL TABLE bronze_stripe_transactions_raw (
    charge_id STRING,
    customer_id STRING,
    amount DECIMAL(10,2),
    currency STRING,
    status STRING,  -- succeeded, failed, pending
    payment_method STRING,  -- card, bank_account, etc
    card_last_four STRING,
    created TIMESTAMP,
    refunded BOOLEAN,
    refund_amount DECIMAL(10,2),
    refund_reason STRING,
    raw_json STRING,
    ingestion_time TIMESTAMP
)
USING PARQUET;

-- CALL TRANSCRIPTS (Raw, async)
CREATE EXTERNAL TABLE bronze_call_transcripts_raw (
    call_id STRING,
    customer_id STRING,
    agent_id STRING,
    call_duration_seconds INT,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    transcript_text STRING,
    recording_url STRING,
    sentiment_raw STRING,
    raw_json STRING,
    ingestion_time TIMESTAMP
)
USING PARQUET;
