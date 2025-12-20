-- Pending Tickets View
-- Real-time view of all pending/open tickets requiring action

CREATE OR REPLACE VIEW vw_pending_tickets AS
SELECT 
    -- Ticket identifiers
    t.ticket_id,
    t.email_id,
    t.customer_id,
    
    -- Customer info
    t.customer_name,
    t.customer_email,
    t.customer_tier,
    c.total_orders,
    c.total_spent,
    c.vip_status,
    
    -- Ticket details
    t.subject,
    t.body_preview,
    t.category,
    t.subcategory,
    t.priority,
    t.priority_score,
    
    -- Timing
    t.received_timestamp,
    t.classified_timestamp,
    t.sla_deadline_timestamp,
    
    -- Calculate time elapsed and remaining
    TIMESTAMPDIFF(MINUTE, t.received_timestamp, CURRENT_TIMESTAMP()) AS age_minutes,
    TIMESTAMPDIFF(MINUTE, CURRENT_TIMESTAMP(), t.sla_deadline_timestamp) AS sla_remaining_minutes,
    
    -- SLA status
    CASE 
        WHEN CURRENT_TIMESTAMP() > t.sla_deadline_timestamp THEN 'breached'
        WHEN TIMESTAMPDIFF(MINUTE, CURRENT_TIMESTAMP(), t.sla_deadline_timestamp) < 15 THEN 'critical'
        WHEN TIMESTAMPDIFF(MINUTE, CURRENT_TIMESTAMP(), t.sla_deadline_timestamp) < 30 THEN 'warning'
        ELSE 'ok'
    END AS sla_status,
    
    -- Status and assignment
    t.status,
    t.assigned_to,
    t.assignment_type,
    
    -- Sentiment and urgency
    t.sentiment_label,
    t.sentiment_score,
    t.emotion_detected,
    t.urgency_level,
    
    -- Related entities
    t.order_numbers,
    t.tracking_numbers,
    
    -- AI insights
    t.category_confidence,
    t.suggested_response,
    t.auto_response_sent,
    t.requires_human_review,
    t.human_reviewed,
    
    -- Classification
    CASE
        WHEN t.status = 'new' AND CURRENT_TIMESTAMP() > t.sla_deadline_timestamp THEN 'new_overdue'
        WHEN t.status = 'new' THEN 'new_ontime'
        WHEN t.status = 'in_progress' AND CURRENT_TIMESTAMP() > t.sla_deadline_timestamp THEN 'in_progress_overdue'
        WHEN t.status = 'in_progress' THEN 'in_progress_ontime'
        WHEN t.status = 'waiting_customer' THEN 'waiting_response'
        ELSE t.status
    END AS ticket_classification

FROM gold_classified_emails t
LEFT JOIN customers c ON t.customer_id = c.customer_id

WHERE t.status IN ('new', 'in_progress', 'waiting_customer')
  AND t.closed_timestamp IS NULL

ORDER BY 
    t.priority_score DESC,
    t.sla_deadline_timestamp ASC,
    t.received_timestamp ASC;


-- Customer 360 View
-- Comprehensive customer view with all interactions and history

CREATE OR REPLACE VIEW vw_customer_360 AS
WITH email_stats AS (
    SELECT 
        customer_id,
        COUNT(*) AS total_email_tickets,
        COUNT(CASE WHEN status IN ('new', 'in_progress') THEN 1 END) AS open_email_tickets,
        AVG(CASE WHEN response_time_minutes IS NOT NULL THEN response_time_minutes END) AS avg_response_time,
        AVG(CASE WHEN resolution_time_minutes IS NOT NULL THEN resolution_time_minutes END) AS avg_resolution_time,
        AVG(CASE WHEN sentiment_score IS NOT NULL THEN sentiment_score END) AS avg_sentiment,
        MAX(received_timestamp) AS last_email_date
    FROM gold_classified_emails
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
),
chat_stats AS (
    SELECT 
        customer_id,
        COUNT(*) AS total_chats,
        COUNT(CASE WHEN conversation_outcome IS NULL THEN 1 END) AS ongoing_chats,
        AVG(duration_seconds) AS avg_chat_duration,
        AVG(CASE WHEN csat_score IS NOT NULL THEN csat_score END) AS avg_csat_score,
        MAX(started_timestamp) AS last_chat_date
    FROM chat_conversations
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
)
SELECT 
    -- Customer basic info
    c.customer_id,
    c.email,
    c.first_name,
    c.last_name,
    c.full_name,
    c.phone,
    c.customer_tier,
    c.vip_status,
    
    -- Shopify data
    c.shopify_id,
    c.created_at AS customer_since,
    c.total_orders,
    c.total_spent,
    c.average_order_value,
    c.first_order_date,
    c.last_order_date,
    c.days_since_last_order,
    
    -- Email support history
    COALESCE(e.total_email_tickets, 0) AS total_email_tickets,
    COALESCE(e.open_email_tickets, 0) AS open_email_tickets,
    e.avg_response_time AS avg_email_response_minutes,
    e.avg_resolution_time AS avg_email_resolution_minutes,
    e.last_email_date,
    
    -- Chat support history
    COALESCE(ch.total_chats, 0) AS total_chats,
    COALESCE(ch.ongoing_chats, 0) AS ongoing_chats,
    ch.avg_chat_duration AS avg_chat_duration_seconds,
    ch.avg_csat_score,
    ch.last_chat_date,
    
    -- Overall support metrics
    COALESCE(e.total_email_tickets, 0) + COALESCE(ch.total_chats, 0) AS total_interactions,
    GREATEST(
        COALESCE(e.last_email_date, TIMESTAMP('1900-01-01')),
        COALESCE(ch.last_chat_date, TIMESTAMP('1900-01-01'))
    ) AS last_interaction_date,
    
    -- Sentiment
    c.overall_sentiment,
    c.average_sentiment_score,
    COALESCE(e.avg_sentiment, 0.0) AS recent_email_sentiment,
    
    -- Risk indicators
    c.is_at_risk,
    c.risk_score,
    c.risk_factors,
    
    -- Customer value
    CASE 
        WHEN c.total_spent > 5000 THEN 'high_value'
        WHEN c.total_spent > 1000 THEN 'medium_value'
        ELSE 'low_value'
    END AS value_segment,
    
    -- Engagement
    CASE
        WHEN c.days_since_last_order <= 30 THEN 'active'
        WHEN c.days_since_last_order <= 90 THEN 'occasional'
        WHEN c.days_since_last_order <= 180 THEN 'inactive'
        ELSE 'dormant'
    END AS engagement_status,
    
    -- Address
    c.default_address,
    
    -- Preferences
    c.preferred_channel,
    c.preferred_language,
    c.accepts_marketing,
    
    -- Tags
    c.tags

FROM customers c
LEFT JOIN email_stats e ON c.customer_id = e.customer_id
LEFT JOIN chat_stats ch ON c.customer_id = ch.customer_id;


-- Real-Time Metrics View
-- Current performance metrics for live dashboards

CREATE OR REPLACE VIEW vw_realtime_metrics AS
WITH today_metrics AS (
    SELECT
        -- Email metrics
        COUNT(CASE WHEN DATE(received_timestamp) = CURRENT_DATE() THEN 1 END) AS emails_today,
        COUNT(CASE WHEN DATE(received_timestamp) = CURRENT_DATE() AND status = 'new' THEN 1 END) AS emails_new,
        COUNT(CASE WHEN DATE(received_timestamp) = CURRENT_DATE() AND status = 'in_progress' THEN 1 END) AS emails_in_progress,
        COUNT(CASE WHEN DATE(resolved_timestamp) = CURRENT_DATE() THEN 1 END) AS emails_resolved_today,
        AVG(CASE WHEN DATE(received_timestamp) = CURRENT_DATE() AND response_time_minutes IS NOT NULL THEN response_time_minutes END) AS avg_response_time_today,
        
        -- SLA compliance
        COUNT(CASE WHEN DATE(received_timestamp) = CURRENT_DATE() AND sla_met = TRUE THEN 1 END) AS sla_met_today,
        COUNT(CASE WHEN DATE(received_timestamp) = CURRENT_DATE() AND sla_met = FALSE THEN 1 END) AS sla_missed_today
    FROM gold_classified_emails
),
chat_metrics AS (
    SELECT
        COUNT(CASE WHEN DATE(started_timestamp) = CURRENT_DATE() THEN 1 END) AS chats_today,
        COUNT(CASE WHEN DATE(started_timestamp) = CURRENT_DATE() AND ended_timestamp IS NULL THEN 1 END) AS chats_active,
        COUNT(CASE WHEN DATE(started_timestamp) = CURRENT_DATE() AND escalated_to_human = TRUE THEN 1 END) AS chats_escalated_today,
        AVG(CASE WHEN DATE(started_timestamp) = CURRENT_DATE() AND csat_score IS NOT NULL THEN csat_score END) AS avg_csat_today
    FROM chat_conversations
),
cost_metrics AS (
    SELECT
        SUM(CASE WHEN DATE(classified_timestamp) = CURRENT_DATE() THEN openai_cost_usd ELSE 0 END) AS openai_cost_today,
        SUM(CASE WHEN YEAR(classified_timestamp) = YEAR(CURRENT_DATE()) AND MONTH(classified_timestamp) = MONTH(CURRENT_DATE()) THEN openai_cost_usd ELSE 0 END) AS openai_cost_month
    FROM gold_classified_emails
)
SELECT
    -- Timestamp
    CURRENT_TIMESTAMP() AS snapshot_timestamp,
    CURRENT_DATE() AS snapshot_date,
    
    -- Email volumes
    e.emails_today,
    e.emails_new,
    e.emails_in_progress,
    e.emails_resolved_today,
    
    -- Email performance
    ROUND(e.avg_response_time_today, 2) AS avg_response_time_minutes,
    ROUND(e.sla_met_today * 100.0 / NULLIF(e.sla_met_today + e.sla_missed_today, 0), 2) AS sla_compliance_percentage,
    
    -- Chat metrics
    c.chats_today,
    c.chats_active,
    c.chats_escalated_today,
    ROUND(c.avg_csat_today, 2) AS avg_csat_score,
    
    -- Cost tracking
    ROUND(cost.openai_cost_today, 2) AS openai_cost_today_usd,
    ROUND(cost.openai_cost_month, 2) AS openai_cost_month_usd,
    ROUND((cost.openai_cost_month / 800.0) * 100, 2) AS budget_used_percentage,
    
    -- Targets
    1200 AS target_emails_daily,
    800 AS target_chats_daily,
    30 AS target_response_time_minutes,
    95.0 AS target_sla_compliance,
    800.0 AS budget_openai_monthly

FROM today_metrics e
CROSS JOIN chat_metrics c
CROSS JOIN cost_metrics cost;
