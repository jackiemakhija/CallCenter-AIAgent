# Retail Call Center Automation - Architecture Guide

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                             │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │   Outlook    │  │   Website    │  │  Power Apps  │                  │
│  │   (Email)    │  │  (Chatbot)   │  │  (Dashboard) │                  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                  │
└─────────┼──────────────────┼──────────────────┼──────────────────────────┘
          │                  │                  │
┌─────────┼──────────────────┼──────────────────┼──────────────────────────┐
│         │   INTEGRATION LAYER (Power Platform)│                          │
├─────────┼──────────────────┼──────────────────┼──────────────────────────┤
│  ┌──────▼──────────────────▼───┐       ┌──────▼─────────┐               │
│  │   Power Automate Flows     │       │Power Virtual   │               │
│  │  • Email ingestion          │       │   Agents       │               │
│  │  • Classification trigger   │       │  • Chatbot     │               │
│  │  • Response sending         │       │  • Topics      │               │
│  └──────┬─────────────────────┘       └──────┬─────────┘               │
└─────────┼────────────────────────────────────┼─────────────────────────┘
          │                                    │
┌─────────┼────────────────────────────────────┼─────────────────────────┐
│         │         AI PROCESSING LAYER        │                          │
├─────────┼────────────────────────────────────┼─────────────────────────┤
│  ┌──────▼────────────────────────────────────▼────────┐                │
│  │           Azure OpenAI (GPT-4o-mini)               │                │
│  │  • Email classification (30% order tracking, etc.) │                │
│  │  • Sentiment analysis                              │                │
│  │  • Response generation                             │                │
│  │  • Entity extraction                               │                │
│  │  • Embeddings (semantic search)                    │                │
│  └──────┬─────────────────────────────────────────────┘                │
└─────────┼──────────────────────────────────────────────────────────────┘
          │
┌─────────┼──────────────────────────────────────────────────────────────┐
│         │            DATA LAYER (Microsoft Fabric)                      │
├─────────┼──────────────────────────────────────────────────────────────┤
│  ┌──────▼─────────────────────────────────────────────────────┐        │
│  │                    Lakehouse (Delta Tables)                 │        │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │        │
│  │  │   BRONZE    │─▶│    SILVER    │─▶│      GOLD       │   │        │
│  │  │  Raw Emails │  │ Enriched Data│  │ Classified Data │   │        │
│  │  │  1200/day   │  │ + Customer   │  │ + AI Results    │   │        │
│  │  └─────────────┘  │ + Shopify    │  │ + SLA Tracking  │   │        │
│  │                   └──────────────┘  └─────────────────┘   │        │
│  │                                                             │        │
│  │  ┌─────────────────────────────────────────────────┐      │        │
│  │  │  Additional Tables:                             │      │        │
│  │  │  • chat_conversations (800/day)                 │      │        │
│  │  │  • chat_messages                                │      │        │
│  │  │  • customers (Shopify sync)                     │      │        │
│  │  │  • knowledge_base (w/ embeddings)               │      │        │
│  │  │  • performance_metrics                          │      │        │
│  │  └─────────────────────────────────────────────────┘      │        │
│  └─────────────────────────────────────────────────────────────┘        │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────┐         │
│  │                  Data Warehouse (SQL)                      │         │
│  │  Views:                                                    │         │
│  │  • vw_pending_tickets (real-time queue)                   │         │
│  │  • vw_customer_360 (unified customer view)                │         │
│  │  • vw_realtime_metrics (dashboard data)                   │         │
│  │  • vw_sla_compliance                                       │         │
│  │  • vw_category_performance                                │         │
│  │  • vw_agent_performance                                   │         │
│  │  • vw_cost_analysis                                       │         │
│  └───────────────────────────────────────────────────────────┘         │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────┐         │
│  │       Real-Time Analytics (KQL Database)                  │         │
│  │  EventStream: EmailStream                                 │         │
│  │  • Live monitoring (< 1 sec latency)                      │         │
│  │  • SLA breach alerts                                      │         │
│  │  • Volume spike detection                                 │         │
│  │  • Sentiment anomalies                                    │         │
│  └───────────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
          │
┌─────────┼──────────────────────────────────────────────────────────────┐
│         │            EXTERNAL INTEGRATIONS                              │
├─────────┼──────────────────────────────────────────────────────────────┤
│  ┌──────▼───────┐  ┌─────────────┐  ┌─────────────┐                   │
│  │   Shopify    │  │  FedEx/UPS  │  │   Stripe    │                   │
│  │   (Orders)   │  │  (Tracking) │  │ (Payments)  │                   │
│  └──────────────┘  └─────────────┘  └─────────────┘                   │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Email Processing Flow

```
1. Email Arrives in Outlook
   ↓
2. Power Automate Trigger
   ↓
3. Insert to Lakehouse Bronze Layer (raw data)
   ↓
4. Trigger Bronze→Silver Pipeline
   ↓
5. Silver Processing:
   - Clean data
   - Match customer (Shopify lookup)
   - Extract entities (order #, tracking #)
   - Basic sentiment analysis
   ↓
6. Insert to Silver Layer
   ↓
7. Trigger Silver→Gold Pipeline
   ↓
8. Gold Processing:
   - Call Azure OpenAI for classification
   - Generate priority score
   - Calculate SLA deadline
   - Generate suggested response
   ↓
9. Insert to Gold Layer
   ↓
10. Decision: Auto-respond or Human Review?
    ├─ Auto (confidence > 85%): Send response
    └─ Human: Add to queue in Power Apps
```

### Chat Processing Flow

```
1. Customer starts chat on website
   ↓
2. Power Virtual Agents handles conversation
   ↓
3. For complex queries: Call Azure OpenAI
   ↓
4. PVA logs messages in real-time
   ↓
5. Conversation ends
   ↓
6. Power Automate triggered
   ↓
7. Insert to chat_conversations & chat_messages
   ↓
8. Update customer record with interaction
```

## Technology Stack Details

### Microsoft Fabric F2 ($263/month)

**Lakehouse:**
- Storage: Delta Lake format (ACID transactions)
- Compute: Apache Spark for processing
- Partitioning: Date-based for performance
- Optimization: Auto-optimize, Z-ordering

**Data Warehouse:**
- SQL endpoint for queries
- Views for business logic
- Materialized for performance
- T-SQL compatibility

**Real-Time Analytics:**
- Kusto Query Language (KQL)
- Sub-second latency
- EventStream for ingestion
- Continuous queries

**Data Science (if needed):**
- Jupyter notebooks
- ML model training
- Integration with Azure ML

### Azure OpenAI ($800/month budget)

**GPT-4o-mini Model:**
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens
- Average 1000 tokens per email (2 API calls)
- Average 4000 tokens per chat conversation

**Estimated Usage:**
- Emails: 1200/day × 2 calls × 1000 tokens = 2.4M tokens/day
- Chats: 800/day × 4000 tokens = 3.2M tokens/day
- Total: ~5.6M tokens/day = 168M tokens/month
- Cost: ~$50-$75/month (well under $800 budget)

**Embeddings (text-embedding-3-small):**
- $0.02 per 1M tokens
- Used for knowledge base semantic search

### Power Platform (FREE with M365 E5)

**Power Automate Premium:**
- 5,000 runs/day per user
- Premium connectors included
- Custom connectors supported

**Power Virtual Agents:**
- Unlimited conversations
- Azure OpenAI integration
- 25+ languages supported

**Power Apps:**
- Unlimited apps per environment
- Premium data sources
- Mobile app support

## Security Architecture

### Authentication & Authorization

```
┌─────────────────────────────────────┐
│   Azure Active Directory (Entra)   │
│   • Single Sign-On (SSO)           │
│   • Multi-Factor Authentication    │
│   • Role-Based Access Control      │
└───────────┬─────────────────────────┘
            │
    ┌───────┴──────────┬────────────┐
    │                  │            │
┌───▼────┐      ┌──────▼──────┐   ┌▼──────────┐
│ Power  │      │   Fabric    │   │  Azure    │
│Platform│      │  Workspace  │   │  OpenAI   │
└────────┘      └─────────────┘   └───────────┘
```

### Data Security

1. **Encryption:**
   - At rest: AES-256 (automatic in Fabric)
   - In transit: TLS 1.2+
   - Key management: Azure Key Vault

2. **Access Control:**
   - Fabric workspace roles (Admin, Member, Contributor, Viewer)
   - Row-level security for sensitive data
   - Power Apps role-based permissions

3. **Data Privacy:**
   - PII handling (customer emails, phones)
   - GDPR compliance (data retention, deletion)
   - Audit logging

4. **API Security:**
   - OAuth 2.0 for Shopify
   - API keys in Key Vault
   - Rate limiting

## Scalability

### Current Capacity (F2)

- **Email Volume:** 1200/day → Can scale to 5000/day
- **Chat Volume:** 800/day → Can scale to 3000/day
- **Storage:** Delta tables auto-scale
- **Compute:** Spark auto-scales based on workload

### Scaling Path

1. **Phase 1 (Current): F2 Capacity**
   - 2 capacity units
   - 1200 emails + 800 chats/day
   - $263/month

2. **Phase 2 (Growth): F4 Capacity**
   - 4 capacity units
   - 3000 emails + 2000 chats/day
   - $526/month

3. **Phase 3 (Scale): F8 Capacity**
   - 8 capacity units
   - 6000+ emails + 4000+ chats/day
   - $1,052/month

### Performance Optimization

1. **Lakehouse Optimization:**
   - Partitioning by date and category
   - Z-ordering on frequently queried columns
   - Auto-optimize enabled
   - Vacuum old files weekly

2. **Query Optimization:**
   - Materialized views for dashboards
   - Indexed columns for fast lookups
   - Query result caching

3. **AI Optimization:**
   - Response caching for common queries
   - Batch processing for non-urgent tickets
   - Token usage monitoring

## Disaster Recovery

### Backup Strategy

1. **Fabric Data:**
   - Automatic point-in-time restore (30 days)
   - Manual snapshots before major changes
   - Cross-region replication (optional)

2. **Configuration:**
   - Power Automate flows exported weekly
   - Power Apps exported monthly
   - Infrastructure as Code (Bicep/Terraform)

### Recovery Time Objectives

- **RTO (Recovery Time Objective):** 4 hours
- **RPO (Recovery Point Objective):** 1 hour

### Failover Plan

1. Email ingestion failures → Store in SharePoint list
2. Fabric unavailable → Route to manual queue
3. OpenAI unavailable → Human takeover immediately

## Monitoring & Alerting

### Key Metrics

1. **Volume Metrics:**
   - Emails received per hour
   - Chats started per hour
   - Deviation from expected volume

2. **Performance Metrics:**
   - Average response time
   - SLA compliance percentage
   - Queue depth

3. **Quality Metrics:**
   - AI classification accuracy
   - Customer satisfaction (CSAT)
   - Resolution rate

4. **Cost Metrics:**
   - Daily OpenAI spend
   - Fabric compute usage
   - Monthly budget tracking

### Alerts

1. **Critical Alerts (immediate):**
   - SLA breach rate > 10%
   - OpenAI cost > $40/day
   - Volume spike > 50% above normal
   - System errors > 5 in 15 minutes

2. **Warning Alerts (15-minute review):**
   - Queue depth > 50 tickets
   - Average response time > 45 minutes
   - Negative sentiment spike
   - VIP customer ticket

3. **Info Alerts (daily digest):**
   - Daily volume summary
   - Performance metrics
   - Cost tracking
   - Top issues

## Compliance & Governance

### Data Retention

- **Bronze emails:** 90 days
- **Silver emails:** 365 days
- **Gold classified emails:** 365 days
- **Chat conversations:** 365 days
- **Performance metrics:** 730 days (2 years)

### Audit Trail

- All ticket status changes logged
- All AI API calls logged with costs
- All human interventions recorded
- Access logs retained for 365 days

### Privacy Controls

- Customer data access restricted by role
- PII masked in non-production
- Right to be forgotten process
- Data export capability
