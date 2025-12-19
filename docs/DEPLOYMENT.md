# Deployment Guide - Retail Call Center Automation

## Prerequisites

### Azure Resources
- [ ] Azure subscription with Owner or Contributor role
- [ ] Azure OpenAI resource with GPT-4o-mini deployment
- [ ] Azure OpenAI API key and endpoint
- [ ] Azure Key Vault (recommended for production)

### Microsoft 365
- [ ] M365 E5 license (includes Power Platform)
- [ ] Power Platform admin access
- [ ] Global Admin or Power Platform Admin role

### Microsoft Fabric
- [ ] Fabric capacity (F2 minimum)
- [ ] Fabric workspace created
- [ ] Fabric admin role

### External Services
- [ ] Shopify store with API access
- [ ] Shopify API credentials
- [ ] FedEx/UPS API credentials (optional)
- [ ] Stripe API credentials (optional)

## Phase 1: Foundation Setup (Weeks 1-4)

### Week 1: Azure OpenAI Setup

1. **Deploy Azure OpenAI:**
   ```bash
   # Login to Azure
   az login
   
   # Create resource group
   az group create --name rg-retail-callcenter --location eastus
   
   # Create Azure OpenAI resource
   az cognitiveservices account create \
     --name openai-retail-callcenter \
     --resource-group rg-retail-callcenter \
     --kind OpenAI \
     --sku S0 \
     --location eastus
   
   # Deploy GPT-4o-mini model
   az cognitiveservices account deployment create \
     --name openai-retail-callcenter \
     --resource-group rg-retail-callcenter \
     --deployment-name gpt-4o-mini \
     --model-name gpt-4o-mini \
     --model-version "2024-07-18" \
     --model-format OpenAI \
     --sku-capacity 100 \
     --sku-name Standard
   
   # Deploy embedding model
   az cognitiveservices account deployment create \
     --name openai-retail-callcenter \
     --resource-group rg-retail-callcenter \
     --deployment-name text-embedding-3-small \
     --model-name text-embedding-3-small \
     --model-version "1" \
     --model-format OpenAI \
     --sku-capacity 100 \
     --sku-name Standard
   
   # Get API key
   az cognitiveservices account keys list \
     --name openai-retail-callcenter \
     --resource-group rg-retail-callcenter
   ```

2. **Create Key Vault (Production):**
   ```bash
   # Create Key Vault
   az keyvault create \
     --name kv-retail-callcenter \
     --resource-group rg-retail-callcenter \
     --location eastus
   
   # Store secrets
   az keyvault secret set --vault-name kv-retail-callcenter \
     --name "AzureOpenAI-ApiKey" --value "<your-api-key>"
   az keyvault secret set --vault-name kv-retail-callcenter \
     --name "Shopify-AccessToken" --value "<your-shopify-token>"
   az keyvault secret set --vault-name kv-retail-callcenter \
     --name "Stripe-ApiKey" --value "<your-stripe-key>"
   ```

### Week 2: Microsoft Fabric Setup

1. **Create Fabric Workspace:**
   - Go to https://app.fabric.microsoft.com
   - Click "Workspaces" → "New Workspace"
   - Name: "Retail Call Center"
   - Enable Fabric capacity (F2)
   - Assign license

2. **Create Lakehouse:**
   - In workspace, click "New" → "Lakehouse"
   - Name: "retail_callcenter_lakehouse"
   - Note the Lakehouse ID

3. **Create Tables:**
   ```bash
   # Connect to Fabric workspace
   # Run SQL scripts in Fabric SQL endpoint
   
   # Execute scripts in order:
   # 1. bronze_emails.sql
   # 2. silver_emails.sql
   # 3. gold_classified_emails.sql
   # 4. chat_conversations.sql
   # 5. chat_messages.sql
   # 6. customers.sql
   # 7. knowledge_base.sql
   # 8. performance_metrics.sql
   ```

4. **Create Data Warehouse:**
   - In workspace, click "New" → "Data Warehouse"
   - Name: "retail_callcenter_dw"
   - Run view creation scripts:
     - core_views.sql
     - analytics_views.sql

5. **Create Real-Time Analytics (KQL Database):**
   - In workspace, click "New" → "Real-Time Analytics"
   - Name: "retail_callcenter_kql"
   - Create EventStream for email ingestion
   - Load KQL queries from realtime_queries.kql

### Week 3: Power Platform Setup

1. **Power Automate Environment:**
   - Go to https://make.powerautomate.com
   - Select your environment (or create new)
   - Note environment ID

2. **Create Connections:**
   - Office 365 Outlook
   - Microsoft Fabric
   - HTTP with Azure AD
   - Shopify (custom connector)
   - Azure OpenAI (HTTP connector)

3. **Import Power Automate Flows:**
   - Import flow JSON files from power-automate/
   - Configure connections
   - Update variables (Workspace ID, Lakehouse ID, etc.)
   - Test flows
   - Turn on flows

4. **Create Power Virtual Agents Bot:**
   - Go to https://web.powerva.microsoft.com
   - Create new bot: "Retail Support Bot"
   - Configure topics:
     - Order Tracking
     - Returns & Refunds
     - Product Information
     - Delivery Issues
   - Add bot to website

### Week 4: Application Configuration

1. **Clone Repository:**
   ```bash
   git clone <your-repo-url>
   cd retail-call-center
   ```

2. **Configure Environment:**
   ```bash
   # Copy environment template
   cp config/.env.example config/.env
   
   # Edit .env with your values
   nano config/.env
   ```

3. **Install Dependencies:**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install packages
   pip install -r requirements.txt
   ```

4. **Test Connections:**
   ```bash
   # Test Azure OpenAI
   python scripts/test_openai_connection.py
   
   # Test Fabric connection
   python scripts/test_fabric_connection.py
   
   # Test Shopify connection
   python scripts/test_shopify_connection.py
   ```

## Phase 2: Email Pipeline (Weeks 5-8)

### Week 5: Bronze Layer Implementation

1. **Configure Outlook Inbox:**
   - Create support folder: "Inbox/Support"
   - Set up mail rules to route support emails
   - Configure Power Automate trigger

2. **Test Bronze Ingestion:**
   - Send test email to support inbox
   - Verify Power Automate flow runs
   - Check bronze_emails table in Lakehouse
   - Review any errors

### Week 6: Silver Layer Pipeline

1. **Create Data Engineering Notebook:**
   - In Fabric workspace, create Notebook
   - Name: "Bronze_to_Silver_Email_Processing"
   - Implement:
     - Email cleaning
     - Customer matching (Shopify lookup)
     - Entity extraction (order numbers, etc.)
     - Sentiment analysis
   
2. **Schedule Pipeline:**
   - Create Data Pipeline in Fabric
   - Trigger: Every 5 minutes
   - Run notebook
   - Test with sample data

### Week 7: Gold Layer & AI Integration

1. **Deploy Classification Logic:**
   - Test Azure OpenAI classification locally
   - Deploy as Azure Function (optional) or use in Power Automate
   - Integrate with silver_emails trigger

2. **Implement Auto-Response:**
   - Test response generation
   - Configure send rules
   - Set up human review queue

### Week 8: Testing & Optimization

1. **End-to-End Testing:**
   - Send test emails for each category
   - Verify classification accuracy
   - Test auto-response generation
   - Check SLA tracking

2. **Performance Tuning:**
   - Optimize Fabric queries
   - Adjust AI prompts for better accuracy
   - Fine-tune confidence thresholds

## Phase 3: Chatbot Integration (Weeks 9-12)

### Week 9: Bot Configuration

1. **Configure PVA Topics:**
   - Order tracking flow
   - Returns process
   - Product info search
   - Escalation to human

2. **Integrate Azure OpenAI:**
   - Add generative answers
   - Configure fallback topics
   - Test conversations

### Week 10: Fabric Integration

1. **Create Chat Logging:**
   - Implement Power Automate flow
   - Log conversations to Fabric
   - Track conversation metrics

### Week 11: Testing

1. **User Acceptance Testing:**
   - Test all conversation flows
   - Verify Fabric logging
   - Check escalation process

### Week 12: Optimization

1. **Refine Bot Responses:**
   - Analyze conversation data
   - Improve topic triggers
   - Enhance generative answers

## Phase 4: Dashboard & Go-Live (Weeks 13-16)

### Week 13: Power Apps Development

1. **Create Dashboard App:**
   - Follow power-apps/dashboard-spec.md
   - Build screens
   - Connect to Fabric Data Warehouse
   - Test all functions

### Week 14: Analytics & Reporting

1. **Create Power BI Reports:**
   - Connect to Fabric Data Warehouse
   - Build executive dashboard
   - Set up email subscriptions

2. **Configure Alerts:**
   - SLA breach alerts
   - High-priority ticket alerts
   - Cost threshold alerts

### Week 15: User Acceptance Testing

1. **UAT with Support Team:**
   - Train agents on Power Apps
   - Test ticket management
   - Gather feedback
   - Make adjustments

### Week 16: Production Deployment

1. **Go-Live Checklist:**
   - [ ] All flows tested and enabled
   - [ ] Power Apps shared with team
   - [ ] Monitoring configured
   - [ ] Backup procedures in place
   - [ ] Documentation complete
   - [ ] Training completed
   - [ ] Support plan established

2. **Launch:**
   - Enable production flows
   - Monitor first 48 hours closely
   - Address any issues immediately
   - Collect feedback

## Post-Deployment

### Monitoring

1. **Daily Checks:**
   - Review Real-Time Analytics dashboard
   - Check SLA compliance
   - Monitor AI costs
   - Review error logs

2. **Weekly Review:**
   - Analyze category performance
   - Review agent metrics
   - Check customer satisfaction
   - Budget tracking

3. **Monthly Optimization:**
   - Fine-tune AI prompts
   - Update knowledge base
   - Review and adjust SLAs
   - Cost optimization

### Maintenance

1. **Regular Updates:**
   - Keep dependencies updated
   - Monitor Azure OpenAI model updates
   - Update Fabric capacity as needed

2. **Backup:**
   - Daily Fabric backups
   - Weekly configuration backups
   - Monthly full system backup

## Troubleshooting

### Common Issues

**Issue: Power Automate flow failing**
- Check connection expiration
- Verify permissions
- Review flow run history
- Check API rate limits

**Issue: High Azure OpenAI costs**
- Review token usage per request
- Optimize prompts
- Adjust temperature settings
- Consider caching common responses

**Issue: SLA breaches**
- Review volume vs capacity
- Check agent availability
- Optimize auto-response rules
- Consider adding automation

## Support Contacts

- Fabric Support: [Microsoft Support]
- Azure OpenAI: [Azure Support]
- Power Platform: [Power Platform Support]

## Cost Monitoring

Track monthly costs:
- Fabric F2: $263/month (fixed)
- Azure OpenAI: Monitor daily (budget $800/month)
- Total target: $1,100/month

Set up budget alerts at:
- 50% ($550)
- 80% ($880)
- 100% ($1,100)
