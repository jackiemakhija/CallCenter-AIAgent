"""
Email Processing Pipeline - Bronze to Silver to Gold
Run this notebook in Microsoft Fabric to process emails through the medallion architecture
"""

# METADATA
# name: email_processing_pipeline
# cluster: Default Spark Pool
# language: python

# =============================================================================
# IMPORTS AND CONFIGURATION
# =============================================================================

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *
from delta.tables import DeltaTable
from datetime import datetime, timedelta
import requests
import json
import re

# Configuration (set these as notebook parameters)
workspace_id = "<YOUR_WORKSPACE_ID>"
lakehouse_id = "<YOUR_LAKEHOUSE_ID>"
openai_endpoint = "<YOUR_OPENAI_ENDPOINT>"
openai_key = "<YOUR_OPENAI_KEY>"
shopify_store = "<YOUR_SHOPIFY_STORE>"
shopify_token = "<YOUR_SHOPIFY_TOKEN>"

# Initialize Spark
spark = SparkSession.builder \
    .appName("EmailProcessingPipeline") \
    .getOrCreate()

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def extract_order_numbers(text):
    """Extract order numbers from text"""
    if not text:
        return []
    # Pattern: # followed by 4-6 digits
    pattern = r'#?(\d{4,6})'
    matches = re.findall(pattern, text)
    return list(set(matches))

def extract_tracking_numbers(text):
    """Extract tracking numbers (FedEx, UPS format)"""
    if not text:
        return []
    patterns = [
        r'\b\d{12}\b',  # FedEx 12 digits
        r'\b\d{15}\b',  # FedEx 15 digits
        r'\b1Z[0-9A-Z]{16}\b',  # UPS
    ]
    matches = []
    for pattern in patterns:
        matches.extend(re.findall(pattern, text, re.IGNORECASE))
    return list(set(matches))

def extract_phone_numbers(text):
    """Extract phone numbers"""
    if not text:
        return []
    pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    matches = re.findall(pattern, text)
    return list(set(matches))

def calculate_sentiment_score(text):
    """Calculate basic sentiment score"""
    if not text:
        return 0.0
    
    positive_words = ['thank', 'thanks', 'great', 'excellent', 'love', 'happy', 'perfect']
    negative_words = ['disappointed', 'unhappy', 'terrible', 'awful', 'hate', 'worst', 'issue', 'problem', 'never']
    
    text_lower = text.lower()
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if pos_count + neg_count == 0:
        return 0.0
    
    score = (pos_count - neg_count) / (pos_count + neg_count)
    return score

def get_sentiment_label(score):
    """Convert sentiment score to label"""
    if score > 0.2:
        return "Positive"
    elif score < -0.2:
        return "Negative"
    else:
        return "Neutral"

def lookup_customer_shopify(email):
    """Lookup customer in Shopify"""
    try:
        url = f"https://{shopify_store}/admin/api/2024-01/customers/search.json?query=email:{email}"
        headers = {"X-Shopify-Access-Token": shopify_token}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('customers'):
                customer = data['customers'][0]
                return {
                    'customer_id': f"shopify_{customer['id']}",
                    'shopify_id': customer['id'],
                    'customer_email': customer['email'],
                    'customer_name': f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip(),
                    'customer_phone': customer.get('phone'),
                    'is_known_customer': True,
                    'customer_lifetime_value': float(customer.get('total_spent', 0)),
                    'customer_order_count': customer.get('orders_count', 0)
                }
    except Exception as e:
        print(f"Error looking up customer: {e}")
    
    return {
        'customer_id': None,
        'is_known_customer': False
    }

# Register UDFs
extract_order_numbers_udf = udf(extract_order_numbers, ArrayType(StringType()))
extract_tracking_numbers_udf = udf(extract_tracking_numbers, ArrayType(StringType()))
extract_phone_numbers_udf = udf(extract_phone_numbers, ArrayType(StringType()))
calculate_sentiment_score_udf = udf(calculate_sentiment_score, DoubleType())
get_sentiment_label_udf = udf(get_sentiment_label, StringType())

# =============================================================================
# BRONZE TO SILVER PROCESSING
# =============================================================================

def process_bronze_to_silver():
    """
    Process bronze emails to silver layer
    - Clean and validate data
    - Match customers
    - Extract entities
    - Calculate basic sentiment
    """
    print("Starting Bronze to Silver processing...")
    
    # Read new bronze records (last hour)
    bronze_df = spark.read.format("delta") \
        .table("bronze_emails") \
        .filter(col("ingestion_timestamp") > lit(datetime.now() - timedelta(hours=1)))
    
    # Check if already processed in silver
    try:
        silver_df = spark.read.format("delta").table("silver_emails")
        processed_ids = silver_df.select("email_id").distinct()
        bronze_df = bronze_df.join(processed_ids, "email_id", "left_anti")
    except:
        print("Silver table doesn't exist yet, processing all bronze records")
    
    if bronze_df.count() == 0:
        print("No new bronze records to process")
        return
    
    print(f"Processing {bronze_df.count()} bronze records...")
    
    # Clean and enrich data
    silver_df = bronze_df.select(
        col("email_id"),
        col("ingestion_timestamp"),
        col("received_timestamp"),
        # Clean email fields
        lower(col("sender_email")).alias("sender_email"),
        trim(col("sender_name")).alias("sender_name"),
        trim(col("subject")).alias("subject"),
        col("body_text"),
        substring(col("body_text"), 1, 200).alias("body_preview"),
        col("has_attachments"),
        col("attachment_count"),
        col("attachment_names"),
        col("conversation_id"),
        col("importance")
    ) \
    .withColumn("processing_timestamp", current_timestamp()) \
    .withColumn("processing_date", current_date())
    
    # Extract entities
    silver_df = silver_df \
        .withColumn("mentioned_order_numbers", extract_order_numbers_udf(col("body_text"))) \
        .withColumn("mentioned_tracking_numbers", extract_tracking_numbers_udf(col("body_text"))) \
        .withColumn("extracted_phone_numbers", extract_phone_numbers_udf(col("body_text")))
    
    # Calculate sentiment
    silver_df = silver_df \
        .withColumn("sentiment_score", calculate_sentiment_score_udf(col("body_text"))) \
        .withColumn("sentiment_label", get_sentiment_label_udf(col("sentiment_score")))
    
    # Validation
    silver_df = silver_df \
        .withColumn("is_valid_email", col("sender_email").rlike("^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$")) \
        .withColumn("is_auto_reply", 
            when(lower(col("subject")).contains("auto") | 
                 lower(col("subject")).contains("out of office"), True)
            .otherwise(False)) \
        .withColumn("language_detected", lit("en"))
    
    # Calculate processing duration
    silver_df = silver_df \
        .withColumn("processing_duration_ms", 
            (unix_timestamp(col("processing_timestamp")) - unix_timestamp(col("ingestion_timestamp"))) * 1000)
    
    # Note: Customer matching would be done via Shopify API in production
    # For batch processing, we'll add customer fields as null and update separately
    silver_df = silver_df \
        .withColumn("customer_id", lit(None).cast(StringType())) \
        .withColumn("customer_email", col("sender_email")) \
        .withColumn("customer_name", col("sender_name")) \
        .withColumn("customer_phone", lit(None).cast(StringType())) \
        .withColumn("is_known_customer", lit(False)) \
        .withColumn("customer_lifetime_value", lit(None).cast(DecimalType(10, 2))) \
        .withColumn("customer_order_count", lit(None).cast(IntegerType()))
    
    # Write to silver table
    silver_df.write \
        .format("delta") \
        .mode("append") \
        .partitionBy("processing_date") \
        .saveAsTable("silver_emails")
    
    print(f"Successfully processed {silver_df.count()} records to silver layer")

# =============================================================================
# SILVER TO GOLD PROCESSING (WITH AI)
# =============================================================================

def classify_email_openai(subject, body):
    """
    Call Azure OpenAI to classify email
    This is simplified - in production, you'd batch these calls
    """
    try:
        prompt = f"""Classify this customer service email into ONE category:
- order_tracking
- returns
- product_info
- delivery
- payment
- complaints

Also determine priority (urgent/high/medium/low) and sentiment.

Subject: {subject}
Body: {body[:500]}

Return JSON with: category, confidence, priority, priority_score (1-10), 
sentiment_label, sentiment_score (-1 to 1), requires_human_review (boolean)
"""
        
        headers = {
            "api-key": openai_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [
                {"role": "system", "content": "You are an email classifier. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 500,
            "response_format": {"type": "json_object"}
        }
        
        response = requests.post(
            f"{openai_endpoint}/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-02-15-preview",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            classification = json.loads(result['choices'][0]['message']['content'])
            
            # Add token usage and cost
            tokens = result['usage']['total_tokens']
            cost = (result['usage']['prompt_tokens'] * 0.15 + result['usage']['completion_tokens'] * 0.60) / 1_000_000
            
            classification['openai_tokens_used'] = tokens
            classification['openai_cost_usd'] = cost
            
            return classification
    except Exception as e:
        print(f"Error classifying email: {e}")
        return None

def process_silver_to_gold():
    """
    Process silver emails to gold layer with AI classification
    """
    print("Starting Silver to Gold processing...")
    
    # Read new silver records
    silver_df = spark.read.format("delta") \
        .table("silver_emails") \
        .filter(col("processing_timestamp") > lit(datetime.now() - timedelta(hours=1)))
    
    # Check if already in gold
    try:
        gold_df = spark.read.format("delta").table("gold_classified_emails")
        processed_ids = gold_df.select("email_id").distinct()
        silver_df = silver_df.join(processed_ids, "email_id", "left_anti")
    except:
        print("Gold table doesn't exist yet")
    
    if silver_df.count() == 0:
        print("No new silver records to process")
        return
    
    print(f"Processing {silver_df.count()} silver records...")
    
    # For production, you'd batch classify via Azure Function or API
    # Here we'll add placeholder classification data
    
    gold_df = silver_df.select(
        expr("uuid()").alias("ticket_id"),
        col("email_id"),
        col("customer_id"),
        col("received_timestamp"),
        current_timestamp().alias("classified_timestamp"),
        current_date().alias("classified_date"),
        col("customer_name"),
        col("sender_email").alias("customer_email"),
        col("subject"),
        col("body_preview"),
        # These would come from OpenAI in production
        lit("order_tracking").alias("category"),
        lit(0.85).alias("category_confidence"),
        lit("tracking_inquiry").alias("subcategory"),
        lit("medium").alias("priority"),
        lit(5).alias("priority_score"),
        col("sentiment_label"),
        col("sentiment_score"),
        lit("curious").alias("emotion_detected"),
        lit("normal").alias("urgency_level"),
        col("mentioned_order_numbers").alias("order_numbers"),
        col("mentioned_tracking_numbers").alias("tracking_numbers"),
        array().cast(ArrayType(StringType())).alias("product_ids"),
        lit("Thank you for contacting us...").alias("suggested_response"),
        lit("order_tracking_template").alias("response_template_used"),
        lit(False).alias("auto_response_sent"),
        lit(False).alias("requires_human_review"),
        lit("new").alias("status"),
        lit(30).alias("sla_target_minutes"),
        (col("received_timestamp") + expr("INTERVAL 30 MINUTES")).alias("sla_deadline_timestamp"),
        lit(100).alias("openai_tokens_used"),
        lit(0.0001).alias("openai_cost_usd")
    )
    
    # Write to gold table
    gold_df.write \
        .format("delta") \
        .mode("append") \
        .partitionBy("classified_date", "category") \
        .saveAsTable("gold_classified_emails")
    
    print(f"Successfully processed {gold_df.count()} records to gold layer")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("EMAIL PROCESSING PIPELINE")
    print("=" * 80)
    
    # Process bronze to silver
    process_bronze_to_silver()
    
    print("\n" + "=" * 80)
    
    # Process silver to gold
    process_silver_to_gold()
    
    print("\n" + "=" * 80)
    print("Pipeline completed successfully")
    print("=" * 80)
