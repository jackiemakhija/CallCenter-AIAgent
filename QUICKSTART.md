# Quick Start Guide - Retail Call Center Automation

## 🚀 Get Started in 5 Steps

### Step 1: Set Up Azure OpenAI (15 minutes)

1. **Create Azure OpenAI resource:**
   ```bash
   az cognitiveservices account create \
     --name openai-retail-callcenter \
     --resource-group rg-retail-callcenter \
     --kind OpenAI \
     --sku S0 \
     --location eastus
   ```

2. **Deploy models:**
   - GPT-4o-mini (for classification and response generation)
   - text-embedding-3-small (for semantic search)

3. **Get your API key:**
   ```bash
   az cognitiveservices account keys list \
     --name openai-retail-callcenter \
     --resource-group rg-retail-callcenter
   ```

4. **Save credentials:**
   - Endpoint: `https://openai-retail-callcenter.openai.azure.com/`
   - API Key: (from step 3)

### Step 2: Create Microsoft Fabric Workspace (10 minutes)

1. **Go to:** https://app.fabric.microsoft.com

2. **Create workspace:**
   - Click "Workspaces" → "New Workspace"
   - Name: "Retail Call Center"
   - Enable F2 capacity

3. **Create Lakehouse:**
   - In workspace, click "New" → "Lakehouse"
   - Name: "retail_callcenter_lakehouse"

4. **Run table creation scripts:**
   - Open SQL endpoint
   - Run scripts from `fabric/lakehouse/` folder in order:
     1. bronze_emails.sql
     2. silver_emails.sql
     3. gold_classified_emails.sql
     4. chat_conversations.sql
     5. chat_messages.sql
     6. customers.sql
     7. knowledge_base.sql
     8. performance_metrics.sql

5. **Create Data Warehouse:**
   - In workspace, click "New" → "Data Warehouse"
   - Name: "retail_callcenter_dw"
   - Run view scripts:
     - core_views.sql
     - analytics_views.sql

### Step 3: Configure Power Automate (20 minutes)

1. **Go to:** https://make.powerautomate.com

2. **Create connections:**
   - Office 365 Outlook
   - Microsoft Fabric
   - HTTP with Azure AD

3. **Import email ingestion flow:**
   - Import `power-automate/Email-Ingestion-Bronze.json`
   - Configure variables:
     ```
     WorkspaceId: [Your Fabric workspace ID]
     LakehouseId: [Your lakehouse ID]
     ```

4. **Import classification flow:**
   - Import `power-automate/Email-Classification-Gold.json`
   - Configure variables:
     ```
     AzureOpenAIEndpoint: [From Step 1]
     AzureOpenAIKey: [From Step 1]
     DeploymentName: gpt-4o-mini
     ```

5. **Test flows:**
   - Send test email to support inbox
   - Check flow run history
   - Verify data in Lakehouse

### Step 4: Set Up Configuration (5 minutes)

1. **Clone/download project:**
   ```bash
   cd retail-call-center
   ```

2. **Create environment file:**
   ```bash
   cp config/.env.example config/.env
   ```

3. **Edit .env with your values:**
   ```env
   # Azure OpenAI
   AZURE_OPENAI_ENDPOINT=https://openai-retail-callcenter.openai.azure.com/
   AZURE_OPENAI_API_KEY=your_key_here
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
   
   # Microsoft Fabric
   FABRIC_WORKSPACE_ID=your_workspace_id
   FABRIC_LAKEHOUSE_ID=your_lakehouse_id
   FABRIC_WAREHOUSE_ID=your_warehouse_id
   
   # Shopify (if available)
   SHOPIFY_STORE_URL=your-store.myshopify.com
   SHOPIFY_ACCESS_TOKEN=your_token
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Step 5: Deploy Power Apps Dashboard (15 minutes)

1. **Go to:** https://make.powerapps.com

2. **Create canvas app:**
   - Choose "Tablet" layout
   - Name: "Call Center Dashboard"

3. **Add data sources:**
   - Add SQL Server connection to Fabric Data Warehouse
   - Connection string: (from Fabric workspace)

4. **Import screens:**
   - Follow `power-apps/dashboard-spec.md`
   - Create main dashboard screen
   - Create ticket queue screen
   - Create ticket detail screen

5. **Test and publish:**
   - Test with sample data
   - Publish to organization
   - Share with support team

## ✅ Verification Checklist

After setup, verify:

- [ ] Azure OpenAI deployments are active
- [ ] Fabric Lakehouse tables created successfully
- [ ] Data Warehouse views accessible
- [ ] Power Automate flows enabled and running
- [ ] Test email processed through Bronze → Silver → Gold
- [ ] Power Apps dashboard loads data
- [ ] Cost monitoring configured

## 📊 Your First Day

### Morning (9:00 AM)

1. **Send test emails:**
   - Order tracking inquiry
   - Return request
   - Product question
   - Delivery issue
   - Payment question
   - Complaint

2. **Verify processing:**
   ```sql
   -- Check bronze layer
   SELECT COUNT(*) FROM bronze_emails WHERE ingestion_date = CURRENT_DATE();
   
   -- Check silver layer
   SELECT COUNT(*) FROM silver_emails WHERE processing_date = CURRENT_DATE();
   
   -- Check gold layer
   SELECT category, COUNT(*) 
   FROM gold_classified_emails 
   WHERE classified_date = CURRENT_DATE()
   GROUP BY category;
   ```

3. **Review classifications:**
   - Were emails classified correctly?
   - Check confidence scores
   - Review suggested responses

### Afternoon (2:00 PM)

1. **Test Power Apps dashboard:**
   - Open ticket queue
   - Filter by category
   - View ticket details
   - Test "Assign to Me" button
   - Test "Send Response" button

2. **Check metrics:**
   ```sql
   SELECT * FROM vw_realtime_metrics;
   ```

3. **Review costs:**
   ```sql
   SELECT * FROM vw_cost_analysis WHERE date = CURRENT_DATE();
   ```

### End of Day (5:00 PM)

1. **Generate daily report:**
   - Total emails processed
   - Classification accuracy
   - SLA compliance
   - OpenAI cost
   - Any errors/issues

2. **Adjust and optimize:**
   - Fine-tune AI prompts if needed
   - Update response templates
   - Adjust confidence thresholds

## 🔧 Common First-Day Issues

### Issue: Power Automate flow failing

**Solution:**
- Check connections haven't expired
- Verify Fabric workspace permissions
- Review flow run history for detailed errors

### Issue: No data in silver/gold tables

**Solution:**
- Verify bronze table has data
- Check notebook execution logs
- Run pipeline manually from Fabric

### Issue: AI classification seems wrong

**Solution:**
- Review prompt in `azure_openai/client.py`
- Check if enough context is provided
- Adjust temperature (lower = more deterministic)

### Issue: Power Apps can't connect to Data Warehouse

**Solution:**
- Verify SQL endpoint URL
- Check authentication method
- Ensure views are created

## 📚 Next Steps

1. **Week 1:**
   - Monitor email processing daily
   - Collect feedback from team
   - Adjust AI prompts and templates

2. **Week 2:**
   - Set up Power Virtual Agents chatbot
   - Configure chatbot flows
   - Test chat integration

3. **Week 3:**
   - Enable auto-responses for high-confidence tickets
   - Configure SLA alerts
   - Train support team on Power Apps

4. **Week 4:**
   - Review metrics and optimize
   - Plan for production rollout
   - Document learnings

## 💡 Pro Tips

1. **Start Small:**
   - Begin with one email category (e.g., order tracking)
   - Verify accuracy before expanding
   - Gradually increase auto-response rate

2. **Monitor Costs Daily:**
   - Set up budget alerts at 50%, 80%, 100%
   - Review token usage by category
   - Optimize high-cost categories first

3. **Iterate on Prompts:**
   - Save prompt versions
   - A/B test different prompts
   - Measure accuracy improvements

4. **Gather Feedback:**
   - Survey support agents weekly
   - Track customer satisfaction
   - Collect examples of good/bad AI responses

5. **Document Everything:**
   - Keep runbook updated
   - Document all configuration changes
   - Maintain troubleshooting guide

## 🆘 Getting Help

### Documentation
- [Architecture Guide](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Operations Runbook](docs/RUNBOOK.md)

### Microsoft Resources
- [Microsoft Fabric Docs](https://learn.microsoft.com/fabric/)
- [Azure OpenAI Docs](https://learn.microsoft.com/azure/ai-services/openai/)
- [Power Platform Docs](https://learn.microsoft.com/power-platform/)

### Support
- Fabric: https://support.fabric.microsoft.com
- Azure: https://portal.azure.com → Support
- Power Platform: https://aka.ms/pp-support

## 🎉 Success Metrics

After 2 weeks, you should see:

- ✅ **1200 emails/day** processed automatically
- ✅ **800 chats/day** handled by bot + automation
- ✅ **> 95% SLA compliance**
- ✅ **< 30 min average response time**
- ✅ **< $1,100/month** total cost
- ✅ **> 85% AI classification accuracy**
- ✅ **> 50% auto-response rate** (no human needed)

**Congratulations! You've built an AI-powered call center automation system! 🎉**
