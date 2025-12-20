# Power Apps Dashboard - Main Application

## Overview
Agent dashboard for monitoring and managing customer service tickets.

## Screens

### 1. Dashboard Home
- Real-time metrics (emails, chats, SLA)
- Today's volume vs target
- Active alerts
- Quick actions

### 2. Ticket Queue
- Filterable ticket list
- Priority sorting
- Category filtering
- Assignmentcapability

### 3. Ticket Detail
- Full ticket information
- Customer 360 view
- AI-generated response
- Action buttons (Reply, Escalate, Close)

### 4. Customer Profile
- Customer information
- Order history
- Support history
- Sentiment trend

### 5. Analytics
- Performance charts
- SLA compliance
- Category breakdown
- Cost tracking

## Data Sources

Connect to:
- Microsoft Fabric Data Warehouse (SQL connection)
- Power Automate flows (for actions)
- SharePoint (for KB articles)

## Component Specifications

### Dashboard Metrics Gallery

```yaml
Gallery: gal_DashboardMetrics
DataSource: 
  Connection: Fabric Data Warehouse
  Query: SELECT * FROM vw_realtime_metrics
Items: 
  - Label: "Emails Today"
    Value: ThisItem.emails_today
    Target: ThisItem.target_emails_daily
    Icon: Mail
    Color: If(Value >= Target * 0.9, Green, Red)
  
  - Label: "Chats Today"
    Value: ThisItem.chats_today
    Target: ThisItem.target_chats_daily
    Icon: Chat
  
  - Label: "SLA Compliance"
    Value: ThisItem.sla_compliance_percentage & "%"
    Target: ThisItem.target_sla_compliance & "%"
    Icon: Clock
    Color: If(Value >= Target, Green, Red)
  
  - Label: "Avg Response Time"
    Value: ThisItem.avg_response_time_minutes & " min"
    Target: ThisItem.target_response_time_minutes & " min"
    Icon: Time
    Color: If(Value <= Target, Green, Red)
  
  - Label: "AI Cost Today"
    Value: "$" & Text(ThisItem.openai_cost_today_usd, "[$-en-US]0.00")
    Target: "$" & Text(ThisItem.budget_openai_monthly / 30, "[$-en-US]0.00")
    Icon: Money
  
  - Label: "Open Tickets"
    Value: ThisItem.emails_new + ThisItem.emails_in_progress
    Icon: Inbox
    Color: Orange
RefreshInterval: 60 seconds
```

### Ticket Queue Gallery

```yaml
Gallery: gal_TicketQueue
DataSource:
  Connection: Fabric Data Warehouse
  Query: |
    SELECT TOP 100 *
    FROM vw_pending_tickets
    WHERE assigned_to = @CurrentUser OR assigned_to IS NULL
    ORDER BY priority_score DESC, sla_deadline_timestamp ASC
Items:
  Layout: Vertical List
  Height: 120
  Fields:
    - ticket_id (Hidden ID)
    - subject (Title - Bold, 16pt)
    - customer_name (Subtitle - 12pt)
    - category_badge (Label with color)
    - priority_badge (Label with color)
    - age_minutes (Label - "Age: X min")
    - sla_remaining_minutes (Label with conditional color)
    - sentiment_icon (Icon - Happy/Neutral/Sad)
FilterOptions:
  - Category: Dropdown (All, Order Tracking, Returns, etc.)
  - Priority: Dropdown (All, Urgent, High, Medium, Low)
  - Status: Dropdown (All, New, In Progress, Waiting)
  - Assigned: Toggle (My Tickets / All Tickets)
OnSelect: Navigate(scrn_TicketDetail, ScreenTransition.Fade, {selectedTicket: ThisItem})
```

### Ticket Detail Screen

```yaml
Screen: scrn_TicketDetail
Parameter: selectedTicket
Layout:
  Header:
    - Back Button
    - Ticket ID: selectedTicket.ticket_id
    - Status: selectedTicket.status (with color badge)
    - Priority: selectedTicket.priority (with color badge)
  
  Left Panel (60% width):
    Section: Email Content
      - Subject: selectedTicket.subject
      - From: selectedTicket.customer_email
      - Received: selectedTicket.received_timestamp
      - Body: selectedTicket.body_preview (expandable)
    
    Section: AI Classification
      - Category: selectedTicket.category (confidence %)
      - Sentiment: selectedTicket.sentiment_label (score)
      - Urgency: selectedTicket.urgency_level
      - Extracted Entities: Order #s, Tracking #s
    
    Section: Suggested Response
      - AI Response Text (editable)
      - Confidence Score
      - Edit Button
      - Send Button
  
  Right Panel (40% width):
    Section: Customer Information
      DataSource: LookUp(vw_customer_360, customer_id = selectedTicket.customer_id)
      - Name
      - Email
      - Phone
      - Tier (VIP badge if applicable)
      - Total Orders
      - Total Spent
      - Recent Sentiment
    
    Section: Order History (if order numbers found)
      DataSource: Shopify API or Fabric
      - Order Number
      - Date
      - Status
      - Total
    
    Section: Support History
      - Total Tickets
      - Open Tickets
      - Last Interaction
      - Average Resolution Time
    
    Section: Actions
      - Button: "Assign to Me"
      - Button: "Send Response"
      - Button: "Escalate"
      - Button: "Mark Resolved"
      - Button: "Add Note"
      - Dropdown: "Change Priority"
      - Dropdown: "Change Category"
  
  Bottom Panel:
    Section: Timeline
      - Ticket creation
      - Status changes
      - Responses sent
      - Notes added
```

### Formula Examples

**SLA Status Color:**
```powerx
If(
    DateDiff(Now(), ThisItem.sla_deadline_timestamp, Minutes) < 0,
    RGBA(220, 53, 69, 1),  // Red - Breached
    If(
        DateDiff(Now(), ThisItem.sla_deadline_timestamp, Minutes) < 15,
        RGBA(255, 193, 7, 1),  // Yellow - Warning
        RGBA(40, 167, 69, 1)   // Green - OK
    )
)
```

**Send Response Action:**
```powerx
// Button OnSelect
Set(varSendingResponse, true);

// Power Automate trigger
Power_Automate_Send_Response.Run(
    selectedTicket.ticket_id,
    selectedTicket.customer_email,
    selectedTicket.subject,
    txt_ResponseBody.Text,
    User().Email
);

// Update ticket status
Patch(
    vw_pending_tickets,
    LookUp(vw_pending_tickets, ticket_id = selectedTicket.ticket_id),
    {
        status: "resolved",
        resolved_timestamp: Now(),
        assigned_to: User().Email
    }
);

Set(varSendingResponse, false);
Back();
```

**Assign Ticket:**
```powerx
Patch(
    gold_classified_emails,
    LookUp(gold_classified_emails, ticket_id = selectedTicket.ticket_id),
    {
        assigned_to: User().Email,
        assignment_type: "manual",
        status: "in_progress"
    }
);
Notify("Ticket assigned to you", NotificationType.Success);
```

### Analytics Charts

```yaml
Chart: chr_VolumeByCategory
Type: Pie Chart
DataSource: 
  Query: |
    SELECT category, COUNT(*) as count
    FROM gold_classified_emails
    WHERE DATE(classified_timestamp) = CURRENT_DATE()
    GROUP BY category
Labels: category
Values: count
Colors: 
  order_tracking: Blue
  returns: Orange
  product_info: Green
  delivery: Purple
  payment: Red
  complaints: DarkRed
```

```yaml
Chart: chr_ResponseTimeTrend
Type: Line Chart
DataSource:
  Query: |
    SELECT 
      DATE(received_timestamp) as date,
      AVG(response_time_minutes) as avg_response_time
    FROM gold_classified_emails
    WHERE received_timestamp >= CURRENT_DATE() - INTERVAL 7 DAYS
    GROUP BY DATE(received_timestamp)
    ORDER BY date
XAxis: date
YAxis: avg_response_time
TargetLine: 30 (Target SLA)
```

```yaml
Chart: chr_SLACompliance
Type: Donut Chart
DataSource:
  Query: |
    SELECT 
      CASE WHEN sla_met THEN 'Met' ELSE 'Missed' END as status,
      COUNT(*) as count
    FROM gold_classified_emails
    WHERE DATE(received_timestamp) = CURRENT_DATE()
    GROUP BY sla_met
Labels: status
Values: count
Colors:
  Met: Green
  Missed: Red
CenterText: "95% Target"
```

## Setup Instructions

1. **Create New Canvas App:**
   - Go to Power Apps (https://make.powerapps.com)
   - Create Canvas App from blank
   - Choose Tablet layout (1366 x 768)

2. **Add Data Sources:**
   - Add connection to Microsoft Fabric
   - Add SQL Server connection to Data Warehouse
   - Add SharePoint for KB articles
   - Add Power Automate flows

3. **Import Screens:**
   - Create screens as specified above
   - Add galleries, forms, and controls
   - Configure formulas and actions

4. **Configure Permissions:**
   - Set up Azure AD authentication
   - Configure role-based access
   - Limit actions based on user role

5. **Test and Publish:**
   - Test all screens and actions
   - Verify data connections
   - Publish app to organization

6. **Deploy:**
   - Share with support team
   - Set up mobile app (optional)
   - Configure notifications

## Mobile Considerations

For mobile version:
- Simplified layout (single column)
- Larger buttons and touch targets
- Voice input for notes
- Camera for attachment capture
- Push notifications for urgent tickets
