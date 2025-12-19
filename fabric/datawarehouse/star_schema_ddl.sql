-- FABRIC DATA WAREHOUSE: STAR SCHEMA
-- Optimized for analytics queries
-- Retention: 3 years

-- ============ DIMENSION TABLES ============

CREATE TABLE DimCustomer (
    customer_key INT PRIMARY KEY,
    customer_id STRING NOT NULL,
    email STRING,
    name STRING,
    phone STRING,
    account_created_date DATE,
    country STRING,
    loyalty_tier STRING,
    is_vip BOOLEAN,
    lifetime_value DECIMAL(12,2),
    created_date DATE DEFAULT CURRENT_DATE(),
    updated_date DATE,
    is_active BOOLEAN
)
USING DELTA;

CREATE TABLE DimProduct (
    product_key INT PRIMARY KEY,
    product_id STRING NOT NULL,
    product_name STRING,
    category STRING,
    subcategory STRING,
    price DECIMAL(10,2),
    supplier_id STRING,
    is_active BOOLEAN,
    created_date DATE DEFAULT CURRENT_DATE(),
    updated_date DATE
)
USING DELTA;

CREATE TABLE DimOrder (
    order_key INT PRIMARY KEY,
    order_id STRING NOT NULL,
    order_number INT,
    customer_key INT,
    order_date DATE,
    status STRING,  -- pending, processing, shipped, delivered, cancelled
    fulfillment_status STRING,
    total_amount DECIMAL(10,2),
    currency STRING,
    item_count INT,
    created_date DATE DEFAULT CURRENT_DATE(),
    updated_date DATE,
    FOREIGN KEY (customer_key) REFERENCES DimCustomer(customer_key)
)
USING DELTA;

CREATE TABLE DimDate (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    year INT,
    quarter INT,
    month INT,
    month_name STRING,
    day INT,
    day_name STRING,
    week_of_year INT,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN
)
USING DELTA;

CREATE TABLE DimAgent (
    agent_key INT PRIMARY KEY,
    agent_id STRING NOT NULL,
    agent_name STRING,
    department STRING,  -- support, operations, management
    email STRING,
    phone STRING,
    hire_date DATE,
    is_active BOOLEAN,
    created_date DATE DEFAULT CURRENT_DATE(),
    updated_date DATE
)
USING DELTA;

-- ============ FACT TABLES ============

CREATE TABLE FactEmailInteraction (
    fact_id BIGINT PRIMARY KEY,
    date_key INT NOT NULL,
    customer_key INT NOT NULL,
    order_key INT,
    agent_key INT,
    email_id STRING,
    intent STRING,  -- order_tracking, returns, product_info, etc
    confidence_score DECIMAL(3,2),
    sentiment STRING,
    priority STRING,
    processing_time_seconds INT,
    response_time_minutes INT,
    attachment_count INT,
    requires_escalation BOOLEAN,
    is_resolved BOOLEAN,
    resolved_date DATE,
    created_time TIMESTAMP,
    FOREIGN KEY (date_key) REFERENCES DimDate(date_key),
    FOREIGN KEY (customer_key) REFERENCES DimCustomer(customer_key),
    FOREIGN KEY (order_key) REFERENCES DimOrder(order_key),
    FOREIGN KEY (agent_key) REFERENCES DimAgent(agent_key)
)
USING DELTA;

CREATE TABLE FactChatInteraction (
    fact_id BIGINT PRIMARY KEY,
    date_key INT NOT NULL,
    customer_key INT NOT NULL,
    order_key INT,
    agent_key INT,
    chat_id STRING,
    conversation_id STRING,
    intent STRING,
    sentiment STRING,
    session_duration_seconds INT,
    message_count INT,
    is_bot_only BOOLEAN,
    escalated_to_human BOOLEAN,
    resolution_time_minutes INT,
    satisfaction_score DECIMAL(2,1),
    created_time TIMESTAMP,
    FOREIGN KEY (date_key) REFERENCES DimDate(date_key),
    FOREIGN KEY (customer_key) REFERENCES DimCustomer(customer_key),
    FOREIGN KEY (order_key) REFERENCES DimOrder(order_key),
    FOREIGN KEY (agent_key) REFERENCES DimAgent(agent_key)
)
USING DELTA;

CREATE TABLE FactOrderStatus (
    fact_id BIGINT PRIMARY KEY,
    date_key INT NOT NULL,
    order_key INT NOT NULL,
    customer_key INT NOT NULL,
    status_from STRING,
    status_to STRING,
    status_changed_time TIMESTAMP,
    days_in_previous_status INT,
    fulfillment_status STRING,
    tracking_number STRING,
    estimated_delivery_date DATE,
    actual_delivery_date DATE,
    is_on_time BOOLEAN,
    created_date DATE DEFAULT CURRENT_DATE(),
    FOREIGN KEY (date_key) REFERENCES DimDate(date_key),
    FOREIGN KEY (order_key) REFERENCES DimOrder(order_key),
    FOREIGN KEY (customer_key) REFERENCES DimCustomer(customer_key)
)
USING DELTA;

CREATE TABLE FactPaymentTransaction (
    fact_id BIGINT PRIMARY KEY,
    date_key INT NOT NULL,
    customer_key INT NOT NULL,
    order_key INT,
    charge_id STRING,
    amount DECIMAL(10,2),
    currency STRING,
    payment_status STRING,  -- completed, failed, pending, refunded
    payment_method STRING,
    card_brand STRING,
    refund_amount DECIMAL(10,2),
    refund_reason STRING,
    transaction_date TIMESTAMP,
    days_to_refund INT,
    created_date DATE DEFAULT CURRENT_DATE(),
    FOREIGN KEY (date_key) REFERENCES DimDate(date_key),
    FOREIGN KEY (customer_key) REFERENCES DimCustomer(customer_key),
    FOREIGN KEY (order_key) REFERENCES DimOrder(order_key)
)
USING DELTA;

-- ============ AGGREGATE TABLES (for performance) ============

CREATE TABLE AggDailyMetrics (
    date_key INT PRIMARY KEY,
    total_emails_received INT,
    total_chats_received INT,
    total_calls_received INT,
    avg_email_response_time_minutes DECIMAL(8,2),
    avg_chat_response_time_minutes DECIMAL(8,2),
    total_orders_created INT,
    total_orders_delivered INT,
    total_revenue DECIMAL(12,2),
    total_refunds DECIMAL(12,2),
    customer_satisfaction_score DECIMAL(3,2),
    agent_efficiency_score DECIMAL(3,2),
    sla_compliance_percent DECIMAL(5,2),
    created_date DATE DEFAULT CURRENT_DATE(),
    FOREIGN KEY (date_key) REFERENCES DimDate(date_key)
)
USING DELTA;

CREATE TABLE AggCustomerMetrics (
    customer_key INT PRIMARY KEY,
    total_interactions INT,
    total_emails INT,
    total_chats INT,
    total_complaints INT,
    avg_satisfaction_score DECIMAL(3,2),
    avg_resolution_time_minutes INT,
    total_spent DECIMAL(12,2),
    total_refunded DECIMAL(12,2),
    repeat_purchase_rate DECIMAL(3,2),
    churn_risk BOOLEAN,
    created_date DATE DEFAULT CURRENT_DATE(),
    FOREIGN KEY (customer_key) REFERENCES DimCustomer(customer_key)
)
USING DELTA;
