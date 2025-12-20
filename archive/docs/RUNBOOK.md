# Operations Runbook - Retail Call Center Automation

## Daily Operations

### Morning Checks (9:00 AM)

1. **Review Real-Time Dashboard:**
   ```kql
   // Run in Fabric Real-Time Analytics
   EmailStream
   | where ingestion_timestamp >= startofday(now())
   | summarize 
       emails_today = count(),
       sla_compliance = countif(sla_met) * 100.0 / count(),
       avg_response_time = avg(response_time_minutes),
       open_tickets = countif(status in ("new", "in_progress"))
   ```
   
   **Expected Results:**
   - Emails today: 400-500 (by 9 AM)
   - SLA compliance: > 95%
   - Avg response time: < 30 minutes
   - Open tickets: < 100

2. **Check for Alerts:**
   - Review Power Apps dashboard for critical alerts
   - Check email for SLA breach notifications
   - Review negative sentiment spike alerts

3. **Review Queue:**
   - Open Power Apps dashboard
   - Sort by priority and SLA deadline
   - Assign urgent tickets to available agents

### Hourly Monitoring

1. **Volume Checks:**
   - Current hour volume vs. expected (50 emails/hour)
   - Chat volume (33 chats/hour)
   - Any unusual spikes?

2. **SLA Status:**
   - Tickets approaching SLA deadline (< 15 min)
   - Any breached SLAs requiring escalation

3. **Cost Monitoring:**
   - Azure OpenAI spend today
   - Projected daily cost vs. budget ($26.67/day)

### End of Day (5:00 PM)

1. **Daily Summary:**
   ```sql
   -- Run in Fabric Data Warehouse
   SELECT * FROM vw_realtime_metrics;
   ```
   
   **Report:**
   - Total emails: _____ (target: 1200)
   - Total chats: _____ (target: 800)
   - SLA compliance: _____ % (target: 95%)
   - Avg response time: _____ min (target: 30)
   - OpenAI cost: $ _____ (budget: $26.67)
   - Open tickets: _____

2. **Handoff to Night Shift (if applicable):**
   - List of high-priority open tickets
   - Any pending escalations
   - Issues to watch

## Weekly Operations

### Monday Morning (9:00 AM)

1. **Weekly Review:**
   ```sql
   -- Performance over last 7 days
   SELECT 
       category,
       COUNT(*) as ticket_count,
       AVG(response_time_minutes) as avg_response_time,
       AVG(category_confidence) as avg_ai_confidence,
       SUM(CASE WHEN sla_met THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as sla_compliance_pct
   FROM gold_classified_emails
   WHERE classified_timestamp >= CURRENT_DATE() - INTERVAL 7 DAYS
   GROUP BY category
   ORDER BY ticket_count DESC;
   ```

2. **Identify Trends:**
   - Which categories increased/decreased?
   - Are response times trending up or down?
   - Is AI classification accuracy stable?

3. **Action Items:**
   - Schedule additional agents for high-volume categories
   - Update response templates if needed
   - Review and improve low-confidence classifications

### Friday Afternoon (3:00 PM)

1. **Backup Configuration:**
   ```powershell
   # Export Power Automate flows
   pac flow export --environment <env-id> --flow <flow-id> --file backup_flows.zip
   
   # Export Power Apps
   pac canvas export --app-name "Call Center Dashboard" --file backup_app.msapp
   ```

2. **Review Cost Trends:**
   ```sql
   SELECT 
       date,
       total_cost_usd,
       projected_monthly_cost,
       variance_from_daily_target
   FROM vw_cost_analysis
   WHERE date >= CURRENT_DATE() - INTERVAL 7 DAYS
   ORDER BY date DESC;
   ```
   
   **Action:** If projected monthly cost > $880 (80% of budget), investigate:
   - Are prompts optimized?
   - Can we cache more responses?
   - Should we increase confidence threshold for auto-responses?

## Monthly Operations

### First of Month

1. **Monthly Report Generation:**
   ```sql
   -- Generate monthly metrics
   SELECT 
       MONTH(classified_timestamp) as month,
       COUNT(*) as total_tickets,
       AVG(response_time_minutes) as avg_response_time,
       AVG(resolution_time_minutes) as avg_resolution_time,
       SUM(CASE WHEN sla_met THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as sla_compliance,
       AVG(customer_satisfaction_score) as avg_csat,
       SUM(openai_cost_usd) as total_ai_cost
   FROM gold_classified_emails
   WHERE classified_timestamp >= DATE_TRUNC('month', CURRENT_DATE() - INTERVAL 1 MONTH)
     AND classified_timestamp < DATE_TRUNC('month', CURRENT_DATE())
   GROUP BY MONTH(classified_timestamp);
   ```

2. **Budget Review:**
   - Fabric F2 actual cost
   - Azure OpenAI actual cost
   - Total vs. $1,100 budget
   - Forecast for next month

3. **Optimize and Tune:**
   - Review AI classification accuracy by category
   - Update response templates based on feedback
   - Retrain agents on new procedures
   - Update knowledge base articles

### Quarterly Operations

1. **Capacity Planning:**
   - Review volume trends
   - Project next quarter volumes
   - Plan capacity upgrades if needed (F2 → F4)

2. **Cost Optimization:**
   - Review OpenAI usage patterns
   - Identify opportunities for caching
   - Consider batch processing strategies

3. **Stakeholder Reporting:**
   - Executive summary presentation
   - ROI analysis
   - Customer satisfaction trends
   - Recommendations for improvement

## Incident Response

### SLA Breach (> 10% of tickets)

**Severity:** High

**Detection:**
- Real-time alert in Power Apps
- Email notification to managers

**Response:**
1. Acknowledge alert within 15 minutes
2. Review queue in Power Apps
3. Identify root cause:
   - Volume spike?
   - Agent shortage?
   - System issue?
4. Take action:
   - Reassign tickets
   - Call in backup agents
   - Temporarily increase auto-response threshold
5. Document incident
6. Follow up to prevent recurrence

### Azure OpenAI Cost Alert (> $40/day)

**Severity:** Medium

**Detection:**
- Cost monitoring alert

**Response:**
1. Check token usage by category
2. Identify unusual patterns
3. Review recent prompt changes
4. Actions:
   - Temporarily reduce auto-response rate
   - Cache common responses
   - Review and optimize prompts
5. Adjust budget forecast

### Power Automate Flow Failure

**Severity:** High (if email ingestion)

**Detection:**
- Flow run failure notification
- Missing data in bronze layer

**Response:**
1. Check flow run history
2. Review error messages
3. Common issues:
   - Connection expired → Refresh connection
   - Rate limit exceeded → Add retry logic
   - API changes → Update flow
4. If email ingestion failing:
   - Manually process missed emails
   - Verify backup queue is collecting emails
5. Test fix
6. Document resolution

### Fabric Lakehouse/Warehouse Unavailable

**Severity:** Critical

**Detection:**
- Query failures
- Power Apps can't load data

**Response:**
1. Check Fabric service health
2. Verify capacity status
3. If regional outage:
   - Switch to manual queue (SharePoint)
   - Notify team
   - Monitor Microsoft status page
4. Once resolved:
   - Verify data integrity
   - Process backlog
   - Resume normal operations

### Customer Complaint About Auto-Response

**Severity:** Medium

**Detection:**
- Customer reply indicating dissatisfaction
- Escalation to manager

**Response:**
1. Review the specific ticket and AI response
2. Assess if response was appropriate
3. Have human agent respond immediately
4. Actions:
   - If AI response was wrong: Add to review queue for similar cases
   - If customer issue complex: Mark category for "requires_human_review"
   - Update knowledge base if needed
5. Follow up with customer
6. Document learnings

## Troubleshooting Guide

### Issue: Low AI Classification Accuracy

**Symptoms:**
- Category confidence < 70%
- Frequent misclassifications
- High human review rate

**Diagnosis:**
```sql
SELECT 
    category,
    AVG(category_confidence) as avg_confidence,
    COUNT(CASE WHEN requires_human_review THEN 1 END) * 100.0 / COUNT(*) as review_rate
FROM gold_classified_emails
WHERE classified_timestamp >= CURRENT_DATE() - INTERVAL 7 DAYS
GROUP BY category
HAVING avg_confidence < 0.7;
```

**Solutions:**
1. Review prompt engineering
2. Add more context (customer history) to classification
3. Provide few-shot examples in prompt
4. Consider fine-tuning model (advanced)
5. Update category definitions

### Issue: High Response Times

**Symptoms:**
- Avg response time > 45 minutes
- Growing queue depth

**Diagnosis:**
```sql
SELECT 
    HOUR(received_timestamp) as hour,
    COUNT(*) as ticket_count,
    AVG(response_time_minutes) as avg_response_time,
    COUNT(CASE WHEN status = 'new' THEN 1 END) as queue_depth
FROM gold_classified_emails
WHERE classified_timestamp >= CURRENT_DATE()
GROUP BY HOUR(received_timestamp)
ORDER BY avg_response_time DESC;
```

**Solutions:**
1. Identify peak hours → adjust staffing
2. Increase auto-response rate (lower confidence threshold temporarily)
3. Review and optimize manual agent workflow
4. Add more agents during peak periods

### Issue: Unexpected OpenAI Costs

**Symptoms:**
- Daily cost > $40
- Monthly projection > $900

**Diagnosis:**
```sql
SELECT 
    category,
    AVG(openai_tokens_used) as avg_tokens,
    AVG(openai_cost_usd) as avg_cost_per_ticket,
    COUNT(*) as ticket_count,
    SUM(openai_cost_usd) as total_cost
FROM gold_classified_emails
WHERE classified_timestamp >= CURRENT_DATE()
GROUP BY category
ORDER BY total_cost DESC;
```

**Solutions:**
1. Identify high-token categories
2. Optimize prompts for those categories (reduce prompt length)
3. Implement response caching for common queries
4. Reduce max_tokens parameter if responses are too long
5. Consider batch processing non-urgent tickets

## Maintenance Tasks

### Daily
- [ ] Review dashboard metrics (9 AM, 12 PM, 5 PM)
- [ ] Check for critical alerts
- [ ] Monitor queue depth
- [ ] Verify Power Automate flows running

### Weekly
- [ ] Review weekly performance report
- [ ] Export configuration backups (Friday)
- [ ] Check cost trends
- [ ] Update knowledge base articles

### Monthly
- [ ] Generate monthly report
- [ ] Review budget vs. actual
- [ ] Optimize AI prompts and templates
- [ ] Update documentation
- [ ] Review and archive old data

### Quarterly
- [ ] Stakeholder presentation
- [ ] Capacity planning review
- [ ] Major optimizations
- [ ] Team training updates

## Contact Information

### Support Escalation

**Level 1: Team Lead**
- Name: _______________
- Email: _______________
- Phone: _______________
- Hours: 8 AM - 6 PM

**Level 2: IT Manager**
- Name: _______________
- Email: _______________
- Phone: _______________
- Hours: On-call 24/7

**Level 3: Microsoft Support**
- Fabric Support: https://support.fabric.microsoft.com
- Azure Support: https://portal.azure.com → Support
- Power Platform: https://aka.ms/pp-support

### Vendor Support

**Shopify:**
- Support: https://help.shopify.com
- API Status: https://status.shopify.com

**Azure OpenAI:**
- Docs: https://learn.microsoft.com/azure/ai-services/openai/
- Status: https://status.azure.com

**Stripe:**
- Support: https://support.stripe.com
- Dashboard: https://dashboard.stripe.com
