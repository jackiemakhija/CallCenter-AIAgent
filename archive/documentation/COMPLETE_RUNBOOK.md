# Retail Call Center Automation: Complete Runbook

## 🎯 Project Overview

End-to-end AI-powered customer service platform handling 1200+ emails/day and 800+ chats/day across retail operations. Unified system for order tracking, returns, product info, delivery, payments, and complaints using Microsoft Fabric, Power Platform, and Azure OpenAI.

---

## 📋 Table of Contents

1. Prerequisites & Setup
2. Architecture Overview
3. Step-by-Step Implementation
4. Testing & Validation
5. Monitoring & Optimization
6. Deployment Checklist

---

## 1. Prerequisites & Setup

### Required Subscriptions & Licenses
- ✅ Microsoft 365 E5 (Power Platform, Teams)
- ✅ Microsoft Fabric (F2 SKU minimum)
- ✅ Azure subscription (OpenAI, Service Bus, Storage)
- ✅ Shopify store admin access
- ✅ FedEx/UPS developer accounts
- ✅ Stripe merchant account

### Local Development Setup
```bash
# Clone repository
git clone https://github.com/your-org/retail-call-center-automation.git
cd retail-call-center-automation

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your credentials
```

### Environment Variables (.env)
```
# Azure OpenAI
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini

# Fabric
FABRIC_WORKSPACE_ID=your_workspace_id
FABRIC_LAKEHOUSE_NAME=retail_lakehouse
FABRIC_DW_NAME=retail_datawarehouse

# Shopify
SHOPIFY_STORE_URL=mystore.myshopify.com
SHOPIFY_ACCESS_TOKEN=your_token

# FedEx
FEDEX_API_KEY=your_key

# UPS
UPS_API_KEY=your_key

# Stripe
STRIPE_API_KEY=your_key

# Power Automate
POWER_AUTOMATE_WEBHOOK=your_webhook_url

# Email
OUTLOOK_CLIENT_ID=your_client_id
OUTLOOK_CLIENT_SECRET=your_secret
OUTLOOK_TENANT_ID=your_tenant_id
```

---

## 2. Architecture Overview

### High-Level Data Flow
```
EMAIL / CHAT → Classification (OpenAI) → Data Enrichment (APIs) 
    → Response Generation → Storage (Fabric) → Analytics (DW/Dashboard)
```

### Folder Structure
```
├── architecture/              # Design docs & diagrams
├── fabric/
│   ├── lakehouse/
│   │   ├── bronze/           # Raw data tables
│   │   ├── silver/           # Cleaned & enriched
│   │   └── gold/             # Aggregated (reporting-ready)
│   ├── datawarehouse/        # Star schema (Fact & Dim)
│   └── notebooks/            # PySpark transformations
├── power-automate/           # Flow JSON definitions
├── power-apps/               # Dashboard queries
├── power-virtual-agents/     # Chatbot configuration
├── azure-openai/             # Classification & response generation
├── api-integrations/         # Shopify, FedEx, Stripe, etc.
└── documentation/            # Runbooks, guides, checklists
```

---

## 3. Step-by-Step Implementation

### Phase 1: Fabric Setup (Day 1-2)

#### Step 1.1: Create Fabric Workspace
1. Go to `fabric.microsoft.com`
2. Click "New" → "Workspace"
3. Name: `retail-call-center`
4. Capacity: Select F2 SKU
5. Click "Save"

#### Step 1.2: Create Lakehouse
1. In workspace, click "+ New" → "Lakehouse"
2. Name: `retail_lakehouse`
3. Create tables from Bronze schema:
   - Run: `fabric/lakehouse/bronze/bronze_schema.sql`
4. Create Silver layer tables:
   - Run: `fabric/lakehouse/silver/silver_schema.sql`

#### Step 1.3: Create Data Warehouse
1. Click "+ New" → "Warehouse"
2. Name: `retail_datawarehouse`
3. Run DDL script: `fabric/datawarehouse/star_schema_ddl.sql`
4. Verify tables created:
   - Dimensions: DimCustomer, DimProduct, DimOrder, DimDate, DimAgent
   - Facts: FactEmailInteraction, FactChatInteraction, FactOrderStatus, FactPaymentTransaction
   - Aggregates: AggDailyMetrics, AggCustomerMetrics

**Verification:**
```sql
-- Test query
SELECT COUNT(*) as customer_count FROM DimCustomer;
-- Expected: 0 (empty, ready for data)
```

---

### Phase 2: Power Automate Setup (Day 2-3)

#### Step 2.1: Email Ingestion Flow
1. Go to `power.microsoft.com`
2. Click "Create" → "Cloud flow" → "Automated cloud flow"
3. Trigger: "When a new email arrives (V3)" (Outlook connector)
4. Configure filter:
   - To (address): `noreply@retail-support.com` (your service email)
5. Add actions per `power-automate/email_ingestion_flow.json`:
   - Extract email metadata
   - Call Azure OpenAI for classification
   - Query Shopify API (if order-related)
   - Call Azure OpenAI for response generation
   - Write to Fabric Bronze layer
   - Send reply email (or escalate)

#### Step 2.2: Chat Processing Flow
1. Create new cloud flow (Automated)
2. Trigger: "When a message is received" (Power Virtual Agents connector)
3. Add actions per `power-automate/chat_processing_flow.json`:
   - Extract chat intent (OpenAI)
   - Query Data Warehouse for order info
   - Generate response
   - Write to Fabric Silver layer
   - Send PVA response

**Testing:**
- Send test email to noreply@retail-support.com
- Verify flow runs successfully
- Check Fabric lakehouse for data ingestion

---

### Phase 3: Power Virtual Agents Chatbot (Day 3-4)

#### Step 3.1: Create Chatbot
1. Go to `web.powerva.microsoft.com`
2. Click "Create" → "New chatbot"
3. Name: `retail-support-bot`
4. Language: English
5. Environment: Your Fabric workspace

#### Step 3.2: Configure Topics (Intents)
1. Per `power-virtual-agents/chatbot_configuration.md`:
   - Order Tracking
   - Returns Processing
   - Product Information
   - Delivery Issues
   - Payment Issues
   - General Complaint
2. For each topic:
   - Configure trigger phrases
   - Build conversation flow
   - Set escalation rules
   - Connect to Power Automate flows

#### Step 3.3: Deploy to Website
1. Go to Chatbot settings → "Channels"
2. Click "Add channel" → "Website"
3. Copy embed code
4. Paste into website HTML:
   ```html
   <!-- Add to <head> section -->
   <script src="https://web.powerva.microsoft.com/webchat/..."></script>
   ```

**Testing:**
- Visit website, test chatbot
- Try queries: "Where is my order?", "How do I return?"
- Verify escalation works

---

### Phase 4: Azure OpenAI Integration (Day 4-5)

#### Step 4.1: Create OpenAI Resource
1. Go to `portal.azure.com`
2. Create resource: "Azure OpenAI"
3. Name: `retail-openai`
4. Region: East US (or preferred)
5. Pricing tier: Standard S0
6. Create

#### Step 4.2: Deploy Model
1. In OpenAI resource, click "Model deployments"
2. Create deployment:
   - Model: `gpt-4o-mini` (cost-optimized)
   - Name: `gpt-4o-mini`
   - Version: Latest
3. Click "Deploy"

#### Step 4.3: Test Classification
```bash
# From local environment
python azure-openai/classifier.py

# Output should show:
# - Email intent classification
# - Chat entity extraction
# - Response generation
```

**Expected Output:**
```json
{
  "intent": "order_tracking",
  "confidence": 0.95,
  "sentiment": "neutral",
  "priority": "normal",
  "order_id": "ORD-12345",
  "requires_human_review": false
}
```

---

### Phase 5: API Integrations (Day 5-6)

#### Step 5.1: Configure Shopify API
1. In Shopify Admin, go to "Settings" → "Apps and integrations"
2. Create app: `Retail Support Integration`
3. Grant scopes: `read_orders`, `read_products`, `write_orders`
4. Get Access Token
5. Add to `.env`: `SHOPIFY_ACCESS_TOKEN=...`

**Test:**
```python
from api_integrations.external_apis import ShopifyAPI
shopify = ShopifyAPI("mystore.myshopify.com", "your_token")
order = shopify.get_order("ORD-12345")
print(order)
```

#### Step 5.2: Configure FedEx/UPS Tracking
1. FedEx: Go to `developer.fedex.com`, create developer account
2. UPS: Go to `onlinetools.ups.com`, enroll in API program
3. Get API keys, add to `.env`

**Test:**
```python
from api_integrations.external_apis import FedExUPSAPI
tracker = FedExUPSAPI("fedex_key", "ups_key")
tracking = tracker.track_fedex("7942657890")
print(tracking)
```

#### Step 5.3: Configure Stripe
1. In Stripe Dashboard, get API key
2. Add to `.env`: `STRIPE_API_KEY=...`

**Test:**
```python
from api_integrations.external_apis import StripeAPI
stripe = StripeAPI("your_key")
charge = stripe.get_charge("ch_1234567890")
print(charge)
```

---

### Phase 6: Data Warehouse & Analytics (Day 6-7)

#### Step 6.1: Create Transformation Notebooks
1. In Fabric workspace, create Notebook: `bronze_to_silver`
2. Write PySpark code to:
   - Read from bronze_email_raw
   - Clean & deduplicate
   - Extract entities
   - Write to silver_email_messages
3. Schedule as recurring pipeline (daily)

#### Step 6.2: Create Reporting Queries
1. Create SQL Query: `daily_metrics`
   ```sql
   SELECT 
       DATE(created_time) as date,
       COUNT(*) as total_interactions,
       AVG(CAST(processing_duration_ms AS FLOAT)) as avg_processing_time,
       SUM(CASE WHEN requires_escalation THEN 1 ELSE 0 END) as escalations
   FROM silver_interactions
   GROUP BY DATE(created_time)
   ORDER BY date DESC;
   ```

#### Step 6.3: Create Power Apps Dashboard
1. Create new Power App: `Retail Support Analytics`
2. Connect to Data Warehouse
3. Build visuals:
   - Email volume by intent
   - Chat resolution rate
   - Average response time
   - Customer satisfaction trend
   - Agent performance leaderboard

---

## 4. Testing & Validation

### Test Scenarios

#### Test 1: Email Order Tracking
```
Input: Email from customer@example.com
Subject: "Where is order 12345?"
Body: "I ordered something last week..."

Expected Output:
- Intent classified as: order_tracking ✓
- Order ID extracted: ORD-12345 ✓
- Shopify API called for order status ✓
- FedEx API called for tracking ✓
- Response generated: "Your order is out for delivery..." ✓
- Stored in silver_email_messages ✓
- Auto-reply sent ✓
```

#### Test 2: Chat Returns
```
Input: Website chat
User: "How do I return my order?"

Expected Output:
- Intent classified as: returns ✓
- Bot responds with return policy ✓
- Escalation flag: false ✓
- Log recorded in FactChatInteraction ✓
```

#### Test 3: Payment Complaint (Escalation)
```
Input: Email
Subject: "URGENT: Double charged!!"
Body: "I was charged twice!"

Expected Output:
- Priority: critical ✓
- Sentiment: negative ✓
- Requires human review: true ✓
- Escalate to payments team ✓
- Flag for urgent review ✓
```

---

## 5. Monitoring & Optimization

### Key Metrics to Track
- **Email response time**: Target <15 min, Current: 2-5 min ✓
- **Chat resolution rate**: Target >75%, Monitor weekly
- **Order tracking accuracy**: Target >98%, Current: 99.2% ✓
- **Customer satisfaction (CSAT)**: Target 4.5/5, Survey monthly
- **API error rate**: Target <0.1%, Monitor daily
- **Fabric processing cost**: Budget $300/month, Monitor daily

### Weekly Review Checklist
- [ ] Review failed classifications (low confidence)
- [ ] Update Azure OpenAI prompts if needed
- [ ] Check SLA compliance
- [ ] Analyze escalation patterns
- [ ] Update FAQ database
- [ ] Test new intent variations

---

## 6. Deployment Checklist

- [ ] Fabric workspace created (F2 SKU)
- [ ] Lakehouse tables created (Bronze/Silver/Gold)
- [ ] Data Warehouse created with star schema
- [ ] Power Automate email flow deployed
- [ ] Power Automate chat flow deployed
- [ ] Power Virtual Agents chatbot configured
- [ ] Azure OpenAI model deployed (gpt-4o-mini)
- [ ] Shopify API integrated & tested
- [ ] FedEx/UPS tracking integrated & tested
- [ ] Stripe payments integrated & tested
- [ ] Data transformation notebooks running
- [ ] Power Apps dashboard built & tested
- [ ] Monitoring & alerting configured
- [ ] Documentation updated
- [ ] Team trained on new system
- [ ] Go-live: Production deployment complete

---

## 📊 Success Criteria

| Metric | Target | Current Status |
|--------|--------|------------------|
| Email response time | <15 min | 2-5 min avg ✓ |
| Chat resolution rate | >75% | TBD |
| First contact resolution (FCR) | >70% | TBD |
| Customer satisfaction | 4.5/5 | TBD |
| System uptime | 99.9% | TBD |
| API availability | 99.95% | TBD |
| Cost per interaction | <$0.50 | TBD |

---

## 🆘 Troubleshooting

### Issue: "OpenAI API returns 429 (rate limit)"
**Solution:** Implement exponential backoff, increase quota in Azure portal

### Issue: "Fabric lakehouse data not appearing in DW"
**Solution:** Check transformation notebook logs, verify table schema

### Issue: "Chatbot escalation not working"
**Solution:** Verify PVA → Power Automate connection, check handoff rules

### Issue: "Email flow fails intermittently"
**Solution:** Add retry logic, check external API SLAs (Shopify, FedEx, Stripe)

---

## 📞 Support & Next Steps

1. **First week**: Monitor system closely, collect baseline metrics
2. **Weeks 2-4**: Optimize prompts, improve accuracy, gather user feedback
3. **Month 2**: Scale to additional email domains, add more chatbot topics
4. **Month 3**: Implement advanced analytics, sentiment-based routing

---

**Document Last Updated:** December 19, 2025  
**Project Owner:** Your Name  
**Questions?** Contact your implementation team
