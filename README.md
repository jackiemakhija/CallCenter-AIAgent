---
title: Call Center Analytics Dashboard
emoji: 📊
colorFrom: indigo
colorTo: green
sdk: streamlit
sdk_version: 1.38.0
app_file: app.py
pinned: false
---

# Call Center AI Chatbot (Hugging Face Space)

## Live Demo
- Space: https://huggingface.co/spaces/jackiemakhija/callcenter-aiaagent
- If repository secrets are not configured, the app runs in Demo Mode with mock responses.

This repository hosts a streamlined, production-ready demo of a call center AI chatbot with:
- Intent classification (orders, returns, delivery, product, payments)
- Sentiment detection and automatic escalation to human agents
- Modern dark UI and session statistics

## 📋 Step-by-Step Setup Instructions

### Prerequisites
- Python 3.10 or higher
- Git installed
- Code editor (VS Code recommended)
- (Optional) Hugging Face account for deployment

### Step 1: Clone or Navigate to Repository
```bash
# If cloning from GitHub
git clone https://github.com/jackiemakhija/CallCenter-AIAgent.git
cd CallCenter-AIAgent

# Or if already have local copy
cd C:\MyCode\foundry-ui\CallCenter-AIAgent
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
py -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
# Upgrade pip
py -m pip install --upgrade pip

# Install required packages
py -m pip install -r requirements.txt
```

Expected output:
```
Successfully installed streamlit-1.38.0 plotly-5.24.1 pandas-2.2.3 numpy-2.1.3 python-dotenv-1.0.0 pyarrow-22.0.0
```

### Step 4: (Optional) Configure Environment Variables
Create a `.env` file in the root directory if you want to connect real services:
```bash
# Copy example (if exists) or create new
notepad .env
```

Add these variables:
```
FOUNDRY_BASE=your_foundry_endpoint
POWER_BI_WORKSPACE_ID=your_workspace_id
POWER_BI_DATASET_ID=your_dataset_id
AZURE_TENANT_ID=your_tenant_id
```

**Note:** App works in Demo Mode without these variables!

### Step 5: Run the Application
```bash
# Start Streamlit server
py -m streamlit run app.py
```

Expected output:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### Step 6: Test the Chatbot

1. **Open Browser**: Navigate to `http://localhost:8501`

2. **Check Environment Panel** (right sidebar):
   - Should show "Demo Mode: Enabled"
   - Foundry: ✓ demo
   - Power BI: ✓ demo
   - Azure: ✓ demo

3. **Test Quick Queries** (click sidebar buttons):
   - "Where is my order?" → Should show order tracking response
   - "I want to return my item" → Should show return process
   - "I'm very unhappy!" → Should escalate to human agent

4. **Test Custom Messages** (type in chat input):
   ```
   Can you track my order #12345?
   ```
   Expected: Order tracking response with intent classification

   ```
   This product is broken and I want a refund!
   ```
   Expected: Escalation message (red banner) + sentiment detection

5. **Check Session Stats** (sidebar):
   - Messages counter should increment
   - Escalations counter updates when escalated
   - Bot resolutions shows successful AI responses

### Step 7: Expected Output Examples

**Successful Query:**
- ✅ Bot response with formatted content
- 📊 Intent badge showing "Order Tracking" or similar
- 😊 Sentiment indicator (Positive/Neutral/Negative)

**Escalation Scenario:**
- 🚨 Red banner with "ESCALATION: Human Agent"
- Agent assignment details
- Full conversation context preserved

**Demo Mode Banner:**
- Light blue background with dark text
- "Demo Mode: Enabled — using mock data"
- Green checkmarks for each service in demo mode

### Step 8: Deploy to Hugging Face Spaces

#### Option A: Using Deploy Script
```bash
# Set Hugging Face token as environment variable
set HF_TOKEN=your_hugging_face_token

# Run deployment script
py scripts/deploy_to_hf.py --space your-username/space-name
```

#### Option B: Manual Upload
1. Create new Space at https://huggingface.co/new-space
2. Choose SDK: Streamlit
3. Clone Space repository:
   ```bash
   git clone https://huggingface.co/spaces/your-username/space-name
   ```
4. Copy files to Space directory:
   ```bash
   copy app.py space-name/
   copy requirements.txt space-name/
   copy runtime.txt space-name/
   ```
5. Commit and push:
   ```bash
   cd space-name
   git add .
   git commit -m "Initial chatbot deployment"
   git push
   ```

### Step 9: Verify Deployment

1. **Check Build Status**: Visit your Space URL
2. **Wait for Build**: Usually takes 2-3 minutes
3. **Test Live App**: Same testing steps as local
4. **Add Secrets** (Optional): Settings → Repository secrets

### Troubleshooting

**Issue: Module not found**
```bash
# Solution: Reinstall dependencies
py -m pip install -r requirements.txt --force-reinstall
```

**Issue: Port already in use**
```bash
# Solution: Specify different port
py -m streamlit run app.py --server.port 8502
```

**Issue: Streamlit not found**
```bash
# Solution: Install directly
py -m pip install streamlit==1.38.0
```

**Issue: Space build fails**
- Check runtime.txt contains `python-3.10`
- Verify requirements.txt has exact versions
- Review Space build logs for specific errors

## Repository Layout

Active demo files:
- `app.py` — Streamlit chatbot app
- `requirements.txt` — minimal deps for Spaces
- `runtime.txt` — Python 3.10 runtime pin
- `scripts/deploy_to_hf.py` — helper to upload to Spaces (optional)
- `.gitignore`, `README.md`

Archived solution artifacts:
- See `/archive/README.md` for details (architecture, Fabric, APIs, Power Platform, Azure OpenAI, docs)

# Retail Call Center Automation

## Overview
AI-powered retail call center automation handling 1200 emails/day and 800 chats/day using Microsoft Fabric, Power Platform, and Azure OpenAI.

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│   Outlook   │────▶│ Power Automate   │────▶│  Fabric Lakehouse   │
└─────────────┘     └──────────────────┘     │  (Bronze/Silver/    │
                                              │   Gold Layers)      │
┌─────────────┐     ┌──────────────────┐     └──────────┬──────────┘
│   Website   │────▶│ Power Virtual    │────────────────┘
│   Chatbot   │     │    Agents        │
└─────────────┘     └──────────────────┘
                            │
                            ▼
                    ┌──────────────────┐     ┌─────────────────────┐
                    │  Azure OpenAI    │────▶│  Fabric Data        │
                    │   GPT-4o-mini    │     │   Warehouse         │
                    └──────────────────┘     └──────────┬──────────┘
                                                        │
                    ┌──────────────────┐                │
                    │  External APIs   │◀───────────────┤
                    │ • Shopify        │                │
                    │ • FedEx/UPS      │                ▼
                    │ • Stripe         │     ┌─────────────────────┐
                    └──────────────────┘     │   Power Apps        │
                                             │    Dashboard        │
                                             └─────────────────────┘
```

## Features

### Email Automation (1200/day)
- Automatic email ingestion from Outlook
- AI-powered classification (30% Order Tracking, 25% Returns, 15% Product Info, 15% Delivery, 10% Payment, 5% Complaints)
- Intelligent routing and priority assignment
- Automated responses for common queries
- Escalation for complex issues

### Chatbot Automation (800/day)
- Power Virtual Agents integration
- Real-time customer support
- Context-aware conversations
- Seamless handoff to human agents
- Order tracking and status updates

### Analytics & Monitoring
- Real-time KQL dashboards
- Performance metrics tracking
- Customer 360° view
- SLA monitoring
- Cost and token usage tracking

## Budget Breakdown
- **Microsoft Fabric F2**: $263/month (2 capacity units)
- **Azure OpenAI**: $800/month (GPT-4o-mini)
- **Power Platform**: FREE (included with M365 E5)
- **Total**: $1,100/month

## Timeline
**16 Weeks Total**

### Phase 1: Foundation (Weeks 1-4)
- Fabric workspace setup
- Lakehouse and Data Warehouse creation
- Azure OpenAI deployment
- API connections setup

### Phase 2: Email Pipeline (Weeks 5-8)
- Power Automate flows for email ingestion
- Bronze/Silver/Gold pipeline implementation
- AI classification integration
- Automated response generation

### Phase 3: Chatbot Integration (Weeks 9-12)
- Power Virtual Agents bot creation
- Conversation flow design
- Integration with Fabric and OpenAI
- Testing and refinement

### Phase 4: Dashboard & Go-Live (Weeks 13-16)
- Power Apps dashboard development
- Real-time analytics setup
- UAT and training
- Production deployment

## Technology Stack

### Microsoft Fabric F2
- **Lakehouse**: Data storage (Bronze/Silver/Gold medallion)
- **Data Warehouse**: Analytics and reporting
- **Real-Time Analytics**: KQL streaming insights
- **Data Science**: ML model training and deployment

### Power Platform (M365 E5 - FREE)
- **Power Automate Premium**: Workflow orchestration
- **Power Virtual Agents**: Chatbot platform
- **Power Apps**: Agent dashboard and admin portal

### Azure OpenAI
- **GPT-4o-mini**: Classification, sentiment, response generation
- **Embeddings**: Semantic search for knowledge base
- **Function Calling**: API integration automation

### External APIs
- **Shopify API**: Customer and order data sync
- **FedEx/UPS APIs**: Real-time shipment tracking
- **Stripe API**: Payment and refund processing

## Project Structure

```
repository/
├── fabric/
│   ├── lakehouse/          # Delta table schemas
│   ├── warehouse/          # DW views and procedures
│   ├── kql/               # Real-time analytics queries
│   └── notebooks/         # Data processing notebooks
├── power-automate/
│   ├── email-flows/       # Email processing workflows
│   └── chatbot-flows/     # Chatbot integration workflows
├── power-apps/            # Agent/admin portal assets
├── azure-openai/
│   ├── classifiers/       # Email/chat classification
│   ├── generators/        # Response generation
│   └── embeddings/        # Knowledge base search
├── integrations/
│   ├── shopify/           # Shopify API integration
│   ├── shipping/          # FedEx/UPS integration
│   └── payments/          # Stripe integration
├── config/
│   └── settings.py        # Configuration management
└── docs/
    ├── DEPLOYMENT.md      # Deployment guide
    ├── API_GUIDE.md       # API documentation
    └── RUNBOOK.md         # Operations runbook
```

## Quick Start

1. **Prerequisites**
   - M365 E5 license
   - Azure subscription
   - Microsoft Fabric F2 capacity
   - Azure OpenAI access

2. **Setup**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Configure environment
   cp config/.env.example config/.env
   # Edit config/.env with your credentials
   
   # Deploy Fabric resources
   python scripts/deploy_fabric_resources.py
   
   # Setup Power Automate flows
   python scripts/import_power_automate_flows.py
   ```

3. **Configuration**
   - Update `config/settings.py` with your workspace IDs
   - Configure API credentials in Azure Key Vault
   - Set up Power Automate connections
   - Deploy Power Virtual Agents bot

## Hugging Face Spaces Deployment

This repo includes a Streamlit app at `CallCenter-AIAgent/app.py`. To deploy only the dashboard to Hugging Face Spaces:

1. Create a new Space (type: Streamlit).
2. Push the contents of the `CallCenter-AIAgent/` folder to the Space repository root (must include `app.py`, `requirements.txt`, `runtime.txt`).
3. In the Space, set required Secrets under Settings ➜ Repository secrets:
   - `FOUNDRY_BASE`, `FOUNDRY_MODEL_PHI`, `FOUNDRY_MODEL_QWEN`, `FOUNDRY_TIMEOUT`
   - `POWER_BI_WORKSPACE_ID`, `POWER_BI_DATASET_ID`, `POWER_BI_BASE_URL`
   - `AZURE_TENANT_ID`
4. The build uses Python 3.10 as specified in `runtime.txt`. No additional config is required; the Space will auto-run `app.py`.

Local run for quick validation:

```bash
cd CallCenter-AIAgent
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

## Release Notes
- v1.0.0: Initial chatbot app deployed to Hugging Face Spaces; repository cleaned and legacy content archived. Demo Mode enabled when secrets are absent.

## Monitoring

- **Real-Time Dashboard**: Monitor email/chat volumes, response times, AI accuracy
- **Cost Tracking**: Azure OpenAI token usage and cost analysis
- **SLA Metrics**: Response time, resolution rate, customer satisfaction
- **Error Alerts**: Automated notifications for failures and anomalies

## Support

For issues and questions:
- Review documentation in `/docs`
- Check runbook for common scenarios
- Contact: IT Support Team

## License

Internal Use Only - Proprietary
