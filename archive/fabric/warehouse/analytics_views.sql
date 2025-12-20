-- SLA Compliance View
-- Detailed SLA tracking and compliance reporting

CREATE OR REPLACE VIEW vw_sla_compliance AS
SELECT
    -- Time dimensions
    DATE(received_timestamp) AS date,
    HOUR(received_timestamp) AS hour,
    DAYOFWEEK(received_timestamp) AS day_of_week,
    
    -- Ticket dimensions
    category,
    priority,
    
    -- Counts
    COUNT(*) AS total_tickets,
    COUNT(CASE WHEN sla_met = TRUE THEN 1 END) AS sla_met_count,
    COUNT(CASE WHEN sla_met = FALSE THEN 1 END) AS sla_missed_count,
    COUNT(CASE WHEN sla_met IS NULL THEN 1 END) AS sla_pending_count,
    
    -- Percentages
    ROUND(COUNT(CASE WHEN sla_met = TRUE THEN 1 END) * 100.0 / COUNT(*), 2) AS sla_compliance_pct,
    
    -- Response times
    AVG(response_time_minutes) AS avg_response_time,
    MIN(response_time_minutes) AS min_response_time,
    MAX(response_time_minutes) AS max_response_time,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY response_time_minutes) AS median_response_time,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_minutes) AS p95_response_time,
    
    -- Resolution times
    AVG(resolution_time_minutes) AS avg_resolution_time,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY resolution_time_minutes) AS median_resolution_time,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY resolution_time_minutes) AS p95_resolution_time,
    
    -- Target comparison
    sla_target_minutes AS target_minutes,
    AVG(response_time_minutes) - sla_target_minutes AS avg_variance_from_target,
    
    -- Breach severity
    AVG(CASE 
        WHEN sla_met = FALSE 
        THEN response_time_minutes - sla_target_minutes 
        ELSE 0 
    END) AS avg_breach_minutes

FROM gold_classified_emails
WHERE received_timestamp >= CURRENT_DATE() - INTERVAL 30 DAYS

GROUP BY 
    DATE(received_timestamp),
    HOUR(received_timestamp),
    DAYOFWEEK(received_timestamp),
    category,
    priority,
    sla_target_minutes

ORDER BY date DESC, hour DESC;


-- Category Performance View
-- Performance metrics by ticket category

CREATE OR REPLACE VIEW vw_category_performance AS
WITH category_stats AS (
    SELECT
        category,
        DATE(received_timestamp) AS date,
        
        -- Volume
        COUNT(*) AS total_tickets,
        COUNT(CASE WHEN status = 'new' THEN 1 END) AS new_tickets,
        COUNT(CASE WHEN status = 'resolved' THEN 1 END) AS resolved_tickets,
        
        -- Performance
        AVG(response_time_minutes) AS avg_response_time,
        AVG(resolution_time_minutes) AS avg_resolution_time,
        AVG(category_confidence) AS avg_ai_confidence,
        
        -- Automation
        COUNT(CASE WHEN auto_response_sent = TRUE THEN 1 END) AS auto_responded,
        COUNT(CASE WHEN requires_human_review = TRUE THEN 1 END) AS required_human_review,
        COUNT(CASE WHEN human_reviewed = TRUE THEN 1 END) AS human_reviewed,
        
        -- Sentiment
        AVG(sentiment_score) AS avg_sentiment,
        COUNT(CASE WHEN sentiment_label = 'Negative' THEN 1 END) AS negative_sentiment_count,
        
        -- SLA
        COUNT(CASE WHEN sla_met = TRUE THEN 1 END) AS sla_met_count,
        COUNT(CASE WHEN sla_met = FALSE THEN 1 END) AS sla_missed_count,
        
        -- Quality
        AVG(customer_satisfaction_score) AS avg_csat,
        
        -- Cost
        SUM(openai_cost_usd) AS total_ai_cost,
        AVG(openai_cost_usd) AS avg_cost_per_ticket
        
    FROM gold_classified_emails
    WHERE received_timestamp >= CURRENT_DATE() - INTERVAL 30 DAYS
    GROUP BY category, DATE(received_timestamp)
)
SELECT
    category,
    date,
    
    -- Volume metrics
    total_tickets,
    new_tickets,
    resolved_tickets,
    ROUND(resolved_tickets * 100.0 / NULLIF(total_tickets, 0), 2) AS resolution_rate_pct,
    
    -- Performance metrics
    ROUND(avg_response_time, 2) AS avg_response_minutes,
    ROUND(avg_resolution_time, 2) AS avg_resolution_minutes,
    ROUND(avg_ai_confidence * 100, 2) AS avg_ai_confidence_pct,
    
    -- Automation metrics
    auto_responded,
    ROUND(auto_responded * 100.0 / NULLIF(total_tickets, 0), 2) AS automation_rate_pct,
    required_human_review,
    human_reviewed,
    
    -- Sentiment metrics
    ROUND(avg_sentiment, 3) AS avg_sentiment_score,
    negative_sentiment_count,
    ROUND(negative_sentiment_count * 100.0 / NULLIF(total_tickets, 0), 2) AS negative_sentiment_pct,
    
    -- SLA metrics
    sla_met_count,
    sla_missed_count,
    ROUND(sla_met_count * 100.0 / NULLIF(sla_met_count + sla_missed_count, 0), 2) AS sla_compliance_pct,
    
    -- Quality metrics
    ROUND(avg_csat, 2) AS avg_csat_score,
    
    -- Cost metrics
    ROUND(total_ai_cost, 2) AS total_ai_cost_usd,
    ROUND(avg_cost_per_ticket, 4) AS avg_cost_per_ticket_usd

FROM category_stats
ORDER BY date DESC, total_tickets DESC;


-- Agent Performance View
-- Performance metrics by agent

CREATE OR REPLACE VIEW vw_agent_performance AS
WITH agent_stats AS (
    SELECT
        assigned_to AS agent_id,
        DATE(received_timestamp) AS date,
        
        -- Volume
        COUNT(*) AS tickets_handled,
        COUNT(CASE WHEN status = 'resolved' THEN 1 END) AS tickets_resolved,
        COUNT(CASE WHEN status IN ('new', 'in_progress') THEN 1 END) AS tickets_open,
        
        -- Category distribution
        COUNT(CASE WHEN category = 'order_tracking' THEN 1 END) AS order_tracking_count,
        COUNT(CASE WHEN category = 'returns' THEN 1 END) AS returns_count,
        COUNT(CASE WHEN category = 'product_info' THEN 1 END) AS product_info_count,
        COUNT(CASE WHEN category = 'delivery' THEN 1 END) AS delivery_count,
        COUNT(CASE WHEN category = 'payment' THEN 1 END) AS payment_count,
        COUNT(CASE WHEN category = 'complaints' THEN 1 END) AS complaints_count,
        
        -- Performance
        AVG(response_time_minutes) AS avg_response_time,
        AVG(resolution_time_minutes) AS avg_resolution_time,
        
        -- SLA
        COUNT(CASE WHEN sla_met = TRUE THEN 1 END) AS sla_met_count,
        COUNT(CASE WHEN sla_met = FALSE THEN 1 END) AS sla_missed_count,
        
        -- Quality
        AVG(customer_satisfaction_score) AS avg_csat,
        COUNT(CASE WHEN customer_satisfaction_score >= 4 THEN 1 END) AS positive_csat_count,
        COUNT(CASE WHEN customer_satisfaction_score IS NOT NULL THEN 1 END) AS total_csat_responses

    FROM gold_classified_emails
    WHERE assigned_to IS NOT NULL
      AND assignment_type IN ('manual', 'escalated')
      AND received_timestamp >= CURRENT_DATE() - INTERVAL 30 DAYS
    GROUP BY assigned_to, DATE(received_timestamp)
)
SELECT
    agent_id,
    date,
    
    -- Volume
    tickets_handled,
    tickets_resolved,
    tickets_open,
    ROUND(tickets_resolved * 100.0 / NULLIF(tickets_handled, 0), 2) AS resolution_rate_pct,
    
    -- Category distribution
    order_tracking_count,
    returns_count,
    product_info_count,
    delivery_count,
    payment_count,
    complaints_count,
    
    -- Performance
    ROUND(avg_response_time, 2) AS avg_response_minutes,
    ROUND(avg_resolution_time, 2) AS avg_resolution_minutes,
    
    -- SLA
    sla_met_count,
    sla_missed_count,
    ROUND(sla_met_count * 100.0 / NULLIF(sla_met_count + sla_missed_count, 0), 2) AS sla_compliance_pct,
    
    -- Quality
    ROUND(avg_csat, 2) AS avg_csat_score,
    positive_csat_count,
    total_csat_responses,
    ROUND(positive_csat_count * 100.0 / NULLIF(total_csat_responses, 0), 2) AS csat_satisfaction_pct,
    
    -- Rankings (within date)
    RANK() OVER (PARTITION BY date ORDER BY tickets_resolved DESC) AS tickets_rank,
    RANK() OVER (PARTITION BY date ORDER BY sla_met_count * 100.0 / NULLIF(sla_met_count + sla_missed_count, 0) DESC) AS sla_rank,
    RANK() OVER (PARTITION BY date ORDER BY avg_csat DESC) AS csat_rank

FROM agent_stats
WHERE agent_id IS NOT NULL
ORDER BY date DESC, tickets_handled DESC;


-- Cost Analysis View
-- Detailed cost tracking and forecasting

CREATE OR REPLACE VIEW vw_cost_analysis AS
WITH daily_costs AS (
    SELECT
        DATE(classified_timestamp) AS date,
        
        -- Email costs
        COUNT(*) AS total_tickets,
        SUM(openai_tokens_used) AS total_tokens,
        SUM(openai_cost_usd) AS total_cost_usd,
        AVG(openai_cost_usd) AS avg_cost_per_ticket,
        
        -- By category
        SUM(CASE WHEN category = 'order_tracking' THEN openai_cost_usd ELSE 0 END) AS cost_order_tracking,
        SUM(CASE WHEN category = 'returns' THEN openai_cost_usd ELSE 0 END) AS cost_returns,
        SUM(CASE WHEN category = 'product_info' THEN openai_cost_usd ELSE 0 END) AS cost_product_info,
        SUM(CASE WHEN category = 'delivery' THEN openai_cost_usd ELSE 0 END) AS cost_delivery,
        SUM(CASE WHEN category = 'payment' THEN openai_cost_usd ELSE 0 END) AS cost_payment,
        SUM(CASE WHEN category = 'complaints' THEN openai_cost_usd ELSE 0 END) AS cost_complaints
        
    FROM gold_classified_emails
    WHERE classified_timestamp >= CURRENT_DATE() - INTERVAL 90 DAYS
    GROUP BY DATE(classified_timestamp)
)
SELECT
    date,
    
    -- Volume and cost
    total_tickets,
    total_tokens,
    ROUND(total_cost_usd, 2) AS total_cost_usd,
    ROUND(avg_cost_per_ticket, 4) AS avg_cost_per_ticket_usd,
    
    -- Monthly projections
    ROUND(total_cost_usd * 30, 2) AS projected_monthly_cost,
    ROUND((total_cost_usd * 30 / 800.0) * 100, 2) AS projected_budget_utilization_pct,
    
    -- Category costs
    ROUND(cost_order_tracking, 2) AS cost_order_tracking,
    ROUND(cost_returns, 2) AS cost_returns,
    ROUND(cost_product_info, 2) AS cost_product_info,
    ROUND(cost_delivery, 2) AS cost_delivery,
    ROUND(cost_payment, 2) AS cost_payment,
    ROUND(cost_complaints, 2) AS cost_complaints,
    
    -- Rolling averages
    ROUND(AVG(total_cost_usd) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS avg_7day_cost,
    ROUND(AVG(total_cost_usd) OVER (ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW), 2) AS avg_30day_cost,
    
    -- Budget tracking
    800.0 AS monthly_budget,
    ROUND(800.0 / 30, 2) AS daily_budget_target,
    ROUND(total_cost_usd - (800.0 / 30), 2) AS variance_from_daily_target

FROM daily_costs
ORDER BY date DESC;
