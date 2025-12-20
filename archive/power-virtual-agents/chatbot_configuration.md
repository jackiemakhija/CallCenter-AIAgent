# Power Virtual Agents Chatbot Configuration

## Chatbot Overview
Conversational chatbot deployed on company website to handle customer inquiries (order tracking, product info, returns, delivery, payment, complaints).

---

## Chatbot Topics (Intents)

### 1. Order Tracking
**User says:** "Where is my order?", "Track order #123", "When will my order arrive?"

**Flow:**
1. Extract order ID (from message or customer context)
2. Query Data Warehouse for order status
3. Call Azure OpenAI to generate friendly response
4. Display: "Your order #ORD-123 is out for delivery. Expected today by 5 PM."

**Escalation:** If order not found or customer is confused → escalate to human agent

---

### 2. Product Information
**User says:** "What's your shipping cost?", "Do you have product X in stock?", "What's the return policy?"

**Flow:**
1. Extract product name/question
2. Query Shopify catalog or FAQ database
3. Generate response with product details, pricing, stock status
4. Offer "Add to cart" or "Connect with agent" option

---

### 3. Returns Processing
**User says:** "How do I return an item?", "I want to return order #456"

**Flow:**
1. Capture order ID and reason for return
2. Validate: Order is eligible (within 30 days, in returnable condition)
3. Generate return label and instructions
4. Log return request in silver_interactions table
5. Notify fulfillment team via Power Automate

---

### 4. Delivery Issues
**User says:** "My package didn't arrive", "Where is my shipment?", "Package is damaged"

**Flow:**
1. Extract order/tracking number
2. Query FedEx/UPS API for current status
3. If status = exception: escalate immediately to agent
4. If in transit: reassure customer with ETA
5. If delivered but not received: initiate investigation

---

### 5. Payment Issues
**User says:** "Charge appeared twice", "Why was I charged?", "Refund status?"

**Flow:**
1. **HIGH PRIORITY** - escalate to human agent
2. Log complaint in FactPaymentTransaction
3. Query Stripe for charge details (do NOT expose sensitive data in chat)
4. Agent handles refund/dispute

---

### 6. General Complaint
**User says:** "Your service is terrible", "I'm never ordering again"

**Flow:**
1. Acknowledge and empathize
2. Ask for specific issue
3. Escalate to supervisor
4. Log as complaint in gold layer for sentiment analysis

---

## Escalation Rules

| Condition | Action | Priority |
|-----------|--------|----------|
| Sentiment = negative | Escalate to senior agent | High |
| Intent = payment/refund | Escalate to payments team | Critical |
| Chat duration > 5 min | Escalate to supervisor | Medium |
| Customer sentiment = angry | Escalate to manager | Critical |
| Bot confidence < 0.6 | Escalate to agent | High |
| Customer requests human | Immediate escalation | Immediate |
| Order status = exception | Escalate to operations | High |
| Customer is VIP (loyalty_tier = platinum) | Escalate to VIP team | High |

---

## Hand-off to Human Agents

When escalating, pass:
```json
{
  "chat_id": "conversation_id",
  "customer_id": "customer_id",
  "order_id": "order_id (if relevant)",
  "intent": "original_intent",
  "conversation_history": [array of messages],
  "sentiment": "positive/neutral/negative",
  "priority": "low/medium/high/critical",
  "suggested_resolution": "..."
}
```

Agent sees:
- Full chat history
- Customer profile (previous orders, complaints, loyalty tier)
- Order details (if applicable)
- Recommended next steps

---

## Bot Response Quality Standards

### Metrics to Track
- **First contact resolution rate** (FCR): % of chats resolved without escalation (Target: >75%)
- **Average chat duration**: <5 minutes (Target)
- **Customer satisfaction (CSAT)**: Post-chat survey (Target: 4.5/5)
- **Bot confidence**: Only respond if confidence > 0.7 (Target: >90%)
- **Escalation rate**: % chats escalated to human (Target: <25%)

### Improvement Loop
1. Weekly review of failed chats
2. Identify new topics/intents
3. Retrain Azure OpenAI prompts
4. A/B test response variations
5. Update FAQ database

---

## Integration with Power Automate

**Trigger:** Chat message received in PVA
↓
**Call Power Automate flow:** "Chat Processing Flow"
↓
**Flow handles:** Intent classification, data enrichment, response generation
↓
**Flow returns:** Response text, escalation decision
↓
**PVA sends:** Response to customer or escalation to agent queue

---

## Deployment Checklist

- [ ] Configure PVA environment (tenant, licensing, channel)
- [ ] Create topics/intents
- [ ] Test escalation paths
- [ ] Integrate with Power Automate flows
- [ ] Configure Azure OpenAI connection
- [ ] Test data warehouse queries
- [ ] Set up agent notification system
- [ ] Deploy to website (embed chat widget)
- [ ] Monitor metrics (FCR, CSAT, response time)
- [ ] Weekly review & optimization

---

## Sample Conversations

### Conversation 1: Order Tracking (Successful)
```
Customer: Where is my order?
Bot: I'd be happy to help! Can you give me your order number?
Customer: Order 123456
Bot: [Query DW] Your order #123456 is out for delivery today! Expected arrival: 5:30 PM. 
      Track here: [FedEx link]
Customer: Great, thanks!
Bot: You're welcome! Let me know if you need anything else.
```
**Outcome:** Resolved, no escalation. FCR ✓

### Conversation 2: Payment Issue (Escalation)
```
Customer: I was charged twice!
Bot: I'm sorry to hear that. This is important. Let me connect you with our payments specialist.
[Escalates to human agent with customer profile, charge details, previous interactions]
Agent: I see the duplicate charge. We'll process a refund right away. You should see it in 3-5 business days.
Customer: Thank you!
```
**Outcome:** Escalated, resolved by human. Data logged for audit.

---

## Future Enhancements

1. **Sentiment-based routing**: Route angry customers to senior agents
2. **Proactive notifications**: "Your order has been delivered!" before customer asks
3. **Multi-language support**: Spanish, French, etc.
4. **Video support**: Escalate to video call for complex issues
5. **Self-service portal**: Link to account dashboard for tracking
6. **SMS channel**: Text-based support alongside web chat
