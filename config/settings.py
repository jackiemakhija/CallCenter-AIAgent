"""
Configuration settings for Retail Call Center Automation
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4o-mini"
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = "text-embedding-3-small"
    
    # Microsoft Fabric Configuration
    FABRIC_WORKSPACE_ID: str
    FABRIC_LAKEHOUSE_ID: str
    FABRIC_WAREHOUSE_ID: str
    FABRIC_KQL_DATABASE_ID: str
    FABRIC_CAPACITY: str = "F2"
    
    # Power Platform Configuration
    POWER_AUTOMATE_ENVIRONMENT_ID: str
    POWER_APPS_ENVIRONMENT_URL: str
    POWER_VIRTUAL_AGENTS_BOT_ID: str
    
    # External API Keys
    SHOPIFY_API_KEY: str
    SHOPIFY_API_SECRET: str
    SHOPIFY_STORE_URL: str
    SHOPIFY_ACCESS_TOKEN: str
    
    FEDEX_API_KEY: str
    FEDEX_SECRET_KEY: str
    FEDEX_ACCOUNT_NUMBER: str
    
    UPS_API_KEY: str
    UPS_USERNAME: str
    UPS_PASSWORD: str
    UPS_ACCOUNT_NUMBER: str
    
    STRIPE_API_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    
    # Email Configuration
    OUTLOOK_CLIENT_ID: str
    OUTLOOK_CLIENT_SECRET: str
    OUTLOOK_TENANT_ID: str
    SUPPORT_EMAIL_ADDRESS: str = "support@retailcompany.com"
    
    # Business Rules
    EMAIL_VOLUME_DAILY: int = 1200
    CHAT_VOLUME_DAILY: int = 800
    
    # Category Distribution (percentages)
    CATEGORY_ORDER_TRACKING: int = 30
    CATEGORY_RETURNS: int = 25
    CATEGORY_PRODUCT_INFO: int = 15
    CATEGORY_DELIVERY: int = 15
    CATEGORY_PAYMENT: int = 10
    CATEGORY_COMPLAINTS: int = 5
    
    # SLA Settings (in minutes)
    SLA_RESPONSE_TIME: int = 30
    SLA_RESOLUTION_TIME: int = 240
    SLA_ESCALATION_TIME: int = 120
    
    # AI Settings
    AI_CONFIDENCE_THRESHOLD: float = 0.75
    AI_MAX_TOKENS: int = 500
    AI_TEMPERATURE: float = 0.7
    EMBEDDING_DIMENSION: int = 1536
    
    # Budget Monitoring
    MONTHLY_BUDGET_FABRIC: float = 263.0
    MONTHLY_BUDGET_OPENAI: float = 800.0
    MONTHLY_BUDGET_TOTAL: float = 1100.0
    
    # Cost per 1M tokens (GPT-4o-mini)
    COST_INPUT_TOKEN: float = 0.15 / 1_000_000  # $0.15 per 1M
    COST_OUTPUT_TOKEN: float = 0.60 / 1_000_000  # $0.60 per 1M
    
    # Azure Key Vault (for production)
    KEY_VAULT_NAME: Optional[str] = None
    
    # Monitoring
    APPLICATION_INSIGHTS_CONNECTION_STRING: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True


# Global settings instance
settings = Settings()


# Category mapping
CATEGORY_MAPPING = {
    "order_tracking": {
        "name": "Order Tracking",
        "priority": "medium",
        "auto_respond": True,
        "sla_minutes": 30
    },
    "returns": {
        "name": "Returns & Refunds",
        "priority": "high",
        "auto_respond": True,
        "sla_minutes": 60
    },
    "product_info": {
        "name": "Product Information",
        "priority": "low",
        "auto_respond": True,
        "sla_minutes": 120
    },
    "delivery": {
        "name": "Delivery Issues",
        "priority": "high",
        "auto_respond": True,
        "sla_minutes": 30
    },
    "payment": {
        "name": "Payment Issues",
        "priority": "high",
        "auto_respond": False,
        "sla_minutes": 60
    },
    "complaints": {
        "name": "Complaints",
        "priority": "urgent",
        "auto_respond": False,
        "sla_minutes": 15
    }
}


# Response templates
RESPONSE_TEMPLATES = {
    "order_tracking": """
Hi {customer_name},

Thank you for contacting us about your order #{order_number}.

{tracking_info}

If you have any other questions, please don't hesitate to reach out.

Best regards,
Customer Support Team
""",
    "returns": """
Hi {customer_name},

We've received your return request for order #{order_number}.

{return_instructions}

Your refund will be processed within 5-7 business days after we receive your return.

Best regards,
Customer Support Team
""",
    "product_info": """
Hi {customer_name},

Thank you for your inquiry about {product_name}.

{product_details}

Is there anything else we can help you with?

Best regards,
Customer Support Team
""",
    "delivery": """
Hi {customer_name},

We apologize for the delivery issue with your order #{order_number}.

{delivery_update}

We're working to resolve this as quickly as possible.

Best regards,
Customer Support Team
""",
    "escalation": """
Hi {customer_name},

Thank you for contacting us. Your case has been escalated to our specialist team.

Case Reference: {case_id}

A team member will contact you within {sla_hours} hours.

Best regards,
Customer Support Team
"""
}


# Fabric table names
FABRIC_TABLES = {
    "bronze_emails": "bronze_emails",
    "silver_emails": "silver_emails",
    "gold_classified_emails": "gold_classified_emails",
    "chat_conversations": "chat_conversations",
    "chat_messages": "chat_messages",
    "customers": "customers",
    "knowledge_base": "knowledge_base",
    "performance_metrics": "performance_metrics",
    "api_logs": "api_logs",
    "cost_tracking": "cost_tracking"
}


# Data Warehouse views
WAREHOUSE_VIEWS = {
    "pending_tickets": "vw_pending_tickets",
    "customer_360": "vw_customer_360",
    "realtime_metrics": "vw_realtime_metrics",
    "sla_compliance": "vw_sla_compliance",
    "category_performance": "vw_category_performance",
    "agent_performance": "vw_agent_performance",
    "cost_analysis": "vw_cost_analysis"
}
