-- FABRIC LAKEHOUSE: SILVER LAYER
-- Cleaned, deduplicated, enriched data
-- Retention: 2 years

-- EMAIL MESSAGES (Cleaned & Enriched)
CREATE TABLE silver_email_messages (
    email_id STRING PRIMARY KEY,
    message_id STRING,
    customer_id STRING,  -- Extracted from from_address
    from_address STRING,
    subject STRING,
    body_text STRING,
    body_html STRING,
    received_time TIMESTAMP,
    classified_intent STRING,  -- order_tracking, returns, product_info, delivery, payment, complaint
    confidence_score DECIMAL(3,2),
    extracted_order_id STRING,
    extracted_entities STRING,  -- JSON: {customer_id, order_id, product_id, ...}
    sentiment STRING,  -- positive, neutral, negative
    priority STRING,  -- low, normal, high, critical
    requires_human_review BOOLEAN,
    requires_escalation BOOLEAN,
    created_time TIMESTAMP,
    processed_time TIMESTAMP,
    processing_duration_ms INT
)
USING DELTA;

-- CHAT MESSAGES (Cleaned & Enriched)
CREATE TABLE silver_chat_messages (
    chat_id STRING PRIMARY KEY,
    conversation_id STRING,
    user_id STRING,
    user_email STRING,
    message_text STRING,
    message_timestamp TIMESTAMP,
    is_bot_response BOOLEAN,
    bot_intent STRING,  -- what the bot understood
    extracted_order_id STRING,
    extracted_entities STRING,  -- JSON
    sentiment STRING,
    session_duration_seconds INT,
    page_url STRING,
    user_device STRING,  -- mobile, tablet, desktop
    user_location STRING,  -- inferred from IP
    created_time TIMESTAMP,
    processed_time TIMESTAMP
)
USING DELTA;

-- CUSTOMER PROFILE (Merged from email, chat, Shopify)
CREATE TABLE silver_customer_profile (
    customer_id STRING PRIMARY KEY,
    email STRING,
    name STRING,
    phone STRING,
    account_created_date DATE,
    total_orders INT,
    total_spent DECIMAL(12,2),
    lifetime_value DECIMAL(12,2),
    last_order_date DATE,
    last_interaction_date TIMESTAMP,
    preferred_contact_method STRING,  -- email, chat, phone
    loyalty_tier STRING,  -- bronze, silver, gold, platinum
    has_complaints BOOLEAN,
    complaint_count INT,
    is_vip BOOLEAN,
    created_time TIMESTAMP,
    updated_time TIMESTAMP
)
USING DELTA;

-- ORDERS (Merged from Shopify)
CREATE TABLE silver_orders (
    order_id STRING PRIMARY KEY,
    order_number INT,
    customer_id STRING,
    created_date DATE,
    order_status STRING,  -- pending, processing, shipped, delivered, cancelled
    fulfillment_status STRING,
    total_amount DECIMAL(10,2),
    currency STRING,
    item_count INT,
    payment_status STRING,  -- pending, completed, refunded, failed
    shipping_carrier STRING,  -- fedex, ups, usps
    tracking_number STRING,
    estimated_delivery_date DATE,
    actual_delivery_date DATE,
    created_time TIMESTAMP,
    updated_time TIMESTAMP
)
USING DELTA;

-- TRACKING EVENTS (Merged from FedEx/UPS)
CREATE TABLE silver_tracking_events (
    tracking_event_id STRING PRIMARY KEY,
    order_id STRING,
    tracking_number STRING,
    carrier STRING,
    event_timestamp TIMESTAMP,
    event_status STRING,  -- picked_up, in_transit, out_for_delivery, delivered, exception
    location_city STRING,
    location_state STRING,
    location_zip STRING,
    location_country STRING,
    event_description STRING,
    exception_reason STRING,  -- if status = exception
    created_time TIMESTAMP
)
USING DELTA;

-- PAYMENT EVENTS (Merged from Stripe)
CREATE TABLE silver_payment_events (
    payment_event_id STRING PRIMARY KEY,
    order_id STRING,
    customer_id STRING,
    charge_id STRING,
    amount DECIMAL(10,2),
    currency STRING,
    payment_status STRING,  -- completed, failed, pending, refunded
    payment_method STRING,  -- card, bank, wallet
    card_brand STRING,  -- visa, mastercard, amex
    card_last_four STRING,
    transaction_date TIMESTAMP,
    refund_amount DECIMAL(10,2),
    refund_reason STRING,
    refund_date TIMESTAMP,
    created_time TIMESTAMP
)
USING DELTA;

-- INTERACTION SUMMARY (Email + Chat unified view)
CREATE TABLE silver_interactions (
    interaction_id STRING PRIMARY KEY,
    interaction_type STRING,  -- email, chat, call
    customer_id STRING,
    order_id STRING,
    intent STRING,
    sentiment STRING,
    priority STRING,
    received_timestamp TIMESTAMP,
    resolved_timestamp TIMESTAMP,
    resolution_time_minutes INT,
    agent_id STRING,
    requires_escalation BOOLEAN,
    created_time TIMESTAMP
)
USING DELTA;
