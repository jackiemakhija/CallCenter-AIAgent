-- Performance Metrics Table
-- Aggregated metrics for monitoring and reporting

CREATE TABLE performance_metrics (
    -- Primary identifier
    metric_id STRING NOT NULL COMMENT 'Unique metric ID',
    
    -- Time dimensions
    metric_timestamp TIMESTAMP NOT NULL COMMENT 'Metric timestamp',
    metric_date DATE NOT NULL COMMENT 'Metric date',
    metric_hour INT COMMENT 'Hour of day (0-23)',
    metric_day_of_week INT COMMENT 'Day of week (1=Monday)',
    
    -- Metric type
    metric_category STRING NOT NULL COMMENT 'email, chat, sla, ai, cost, quality',
    metric_name STRING NOT NULL COMMENT 'Specific metric name',
    metric_value DOUBLE NOT NULL COMMENT 'Metric value',
    metric_unit STRING COMMENT 'count, seconds, percentage, dollars',
    
    -- Dimensions
    channel STRING COMMENT 'email, chat, etc.',
    category STRING COMMENT 'order_tracking, returns, etc.',
    priority STRING COMMENT 'urgent, high, medium, low',
    agent_id STRING COMMENT 'Agent identifier',
    team STRING COMMENT 'Team identifier',
    
    -- Aggregation level
    aggregation_level STRING NOT NULL COMMENT 'raw, hourly, daily, weekly, monthly',
    aggregation_count INT DEFAULT 1 COMMENT 'Number of data points aggregated',
    
    -- Statistical measures
    min_value DOUBLE COMMENT 'Minimum value in period',
    max_value DOUBLE COMMENT 'Maximum value in period',
    avg_value DOUBLE COMMENT 'Average value',
    median_value DOUBLE COMMENT 'Median value',
    stddev_value DOUBLE COMMENT 'Standard deviation',
    percentile_95 DOUBLE COMMENT '95th percentile',
    percentile_99 DOUBLE COMMENT '99th percentile',
    
    -- Context
    description STRING COMMENT 'Metric description',
    metadata MAP<STRING, STRING> COMMENT 'Additional metadata',
    
    -- Alerts
    threshold_warning DOUBLE COMMENT 'Warning threshold',
    threshold_critical DOUBLE COMMENT 'Critical threshold',
    is_above_warning BOOLEAN DEFAULT FALSE,
    is_above_critical BOOLEAN DEFAULT FALSE,
    
    -- Partitioning
    year INT NOT NULL,
    month INT NOT NULL
) 
USING DELTA
PARTITIONED BY (year, month, metric_category)
COMMENT 'Performance metrics for monitoring and reporting'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Primary key
ALTER TABLE performance_metrics 
ADD CONSTRAINT metrics_pk PRIMARY KEY (metric_id);

-- Optimize
OPTIMIZE performance_metrics ZORDER BY (metric_timestamp, metric_category, metric_name);

-- Indexes
CREATE INDEX idx_metrics_timestamp ON performance_metrics (metric_timestamp);
CREATE INDEX idx_metrics_category ON performance_metrics (metric_category);
CREATE INDEX idx_metrics_name ON performance_metrics (metric_name);
