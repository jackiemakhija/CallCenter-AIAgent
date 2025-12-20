-- Knowledge Base Table
-- Stores KB articles with embeddings for semantic search

CREATE TABLE knowledge_base (
    -- Primary identifier
    article_id STRING NOT NULL COMMENT 'Unique article ID',
    
    -- Content
    title STRING NOT NULL COMMENT 'Article title',
    content STRING NOT NULL COMMENT 'Full article content (markdown)',
    summary STRING COMMENT 'Brief summary',
    category STRING NOT NULL COMMENT 'Article category',
    subcategory STRING COMMENT 'Article subcategory',
    
    -- Metadata
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    created_by STRING COMMENT 'Author email',
    updated_by STRING COMMENT 'Last editor',
    version INT DEFAULT 1,
    
    -- Status
    status STRING DEFAULT 'draft' COMMENT 'draft, published, archived',
    published_at TIMESTAMP COMMENT 'Publication date',
    
    -- Keywords and tags
    keywords ARRAY<STRING> COMMENT 'Keywords for search',
    tags ARRAY<STRING> COMMENT 'Classification tags',
    
    -- Related content
    related_article_ids ARRAY<STRING> COMMENT 'Related articles',
    related_products ARRAY<STRING> COMMENT 'Related product IDs',
    
    -- Usage statistics
    view_count INT DEFAULT 0 COMMENT 'Number of views',
    helpful_count INT DEFAULT 0 COMMENT 'Marked as helpful',
    not_helpful_count INT DEFAULT 0 COMMENT 'Marked as not helpful',
    helpfulness_score DOUBLE COMMENT 'Helpful ratio',
    last_viewed_at TIMESTAMP,
    
    -- AI/Semantic search
    embedding ARRAY<DOUBLE> COMMENT 'OpenAI embedding vector (1536 dimensions)',
    embedding_model STRING DEFAULT 'text-embedding-3-small',
    embedding_generated_at TIMESTAMP,
    
    -- Automatic content features
    content_length INT COMMENT 'Character count',
    reading_time_minutes INT COMMENT 'Est. reading time',
    language STRING DEFAULT 'en',
    
    -- Questions this article answers
    common_questions ARRAY<STRING> COMMENT 'Questions this answers',
    
    -- Access control
    is_public BOOLEAN DEFAULT TRUE,
    is_internal_only BOOLEAN DEFAULT FALSE,
    required_permissions ARRAY<STRING> COMMENT 'Permissions needed to view',
    
    -- SEO
    seo_title STRING COMMENT 'SEO-optimized title',
    seo_description STRING COMMENT 'Meta description',
    url_slug STRING COMMENT 'URL-friendly slug',
    
    -- Partitioning
    category_partition STRING NOT NULL COMMENT 'Category for partitioning'
) 
USING DELTA
PARTITIONED BY (category_partition)
COMMENT 'Knowledge base articles with semantic embeddings'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Primary key
ALTER TABLE knowledge_base 
ADD CONSTRAINT kb_pk PRIMARY KEY (article_id);

-- Optimize
OPTIMIZE knowledge_base ZORDER BY (category, status, updated_at);

-- Indexes
CREATE INDEX idx_kb_category ON knowledge_base (category);
CREATE INDEX idx_kb_status ON knowledge_base (status);
CREATE INDEX idx_kb_helpful ON knowledge_base (helpfulness_score);

-- Note: For vector similarity search, use Azure AI Search or 
-- implement cosine similarity in Spark/Python notebooks
