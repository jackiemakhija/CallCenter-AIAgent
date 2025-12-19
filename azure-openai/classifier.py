import os
import json
from openai import AzureOpenAI
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class RetailClassifier:
    """
    Azure OpenAI-based classifier for retail customer inquiries.
    Handles: Intent classification, entity extraction, sentiment analysis.
    """
    
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
    
    def classify_email(self, email_body: str, subject: str) -> Dict:
        """
        Classify email into retail intent categories.
        
        Returns:
            {
                "intent": "order_tracking|returns|product_info|delivery|payment|complaint",
                "confidence": 0.0-1.0,
                "sentiment": "positive|neutral|negative",
                "priority": "low|normal|high|critical",
                "extracted_entities": {"customer_id": "...", "order_id": "..."},
                "requires_human_review": bool
            }
        """
        
        prompt = f"""You are a retail customer service intent classifier.
        
Classify the following email into ONE of these categories:
1. order_tracking - Customer asking about order status, tracking number, delivery date
2. returns - Customer wants to return item or asking about return process
3. product_info - Customer asking about product details, availability, pricing
4. delivery - Customer reporting delivery issues, wrong address, damaged package
5. payment - Customer reporting billing issues, duplicate charges, refund status
6. complaint - Customer expressing dissatisfaction, complaints, negative feedback

Email Subject: {subject}
Email Body: {email_body}

Also extract:
- sentiment: positive, neutral, or negative
- priority: low (standard), normal (important), high (urgent), critical (payment/complaint)
- order_id if present (format: ORD-XXXXX or similar)
- customer_email if present

Response format (JSON):
{{
    "intent": "string",
    "confidence": 0.0-1.0,
    "sentiment": "string",
    "priority": "string",
    "order_id": "string or null",
    "extracted_entities": {{"customer_email": "...", "order_id": "..."}},
    "reasoning": "brief explanation"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            # Determine if human review needed
            result["requires_human_review"] = (
                result.get("confidence", 1.0) < 0.7 or 
                result.get("sentiment") == "negative" or
                result.get("priority") == "critical"
            )
            
            return result
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response: {e}")
            return {"intent": "unknown", "confidence": 0.0, "requires_human_review": True}
        except Exception as e:
            logger.error(f"Azure OpenAI error: {e}")
            raise
    
    def classify_chat(self, message: str) -> Dict:
        """
        Classify chat message and extract entities.
        More concise than email classification.
        """
        
        prompt = f"""Extract intent and entities from this customer message:

Message: "{message}"

Intents: order_tracking, returns, product_info, delivery, payment, complaint, general_inquiry

Extract any mentioned:
- order_id
- product_name
- issue_description

Response (JSON):
{{
    "intent": "string",
    "confidence": 0.0-1.0,
    "entities": {{"order_id": null, "product_name": null}},
    "followup_question": "question to clarify intent if needed"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        
        except Exception as e:
            logger.error(f"Chat classification error: {e}")
            return {"intent": "general_inquiry", "confidence": 0.5}


class ResponseGenerator:
    """
    Generate contextual, accurate responses using enriched data.
    """
    
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
    
    def generate_email_response(
        self,
        intent: str,
        customer_name: str,
        order_data: Optional[Dict] = None,
        tracking_data: Optional[Dict] = None,
        payment_data: Optional[Dict] = None
    ) -> Dict:
        """
        Generate professional email response based on intent and enriched data.
        """
        
        # Build context
        context = f"Customer: {customer_name}\n"
        if order_data:
            context += f"Order: {order_data.get('order_id')} - Status: {order_data.get('status')}\n"
        if tracking_data:
            context += f"Tracking: {tracking_data.get('current_location')} - ETA: {tracking_data.get('estimated_delivery')}\n"
        if payment_data:
            context += f"Payment: {payment_data.get('status')} - Amount: ${payment_data.get('amount')}\n"
        
        prompt = f"""You are a professional retail customer service representative.

Context:
{context}

Generate a professional, empathetic, and accurate response for intent: {intent}

Requirements:
- Keep it concise (2-3 sentences)
- Be friendly and professional
- Include specific details (order numbers, tracking info, etc.)
- If escalation needed, explain why
- Always end with offer to help further

Response:
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300
            )
            
            response_text = response.choices[0].message.content
            
            return {
                "response_body": response_text,
                "success": True
            }
        
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return {
                "response_body": "Thank you for your inquiry. Our team will review your message and respond shortly.",
                "success": False
            }
    
    def generate_chat_response(
        self,
        intent: str,
        user_message: str,
        order_data: Optional[Dict] = None
    ) -> str:
        """
        Generate friendly, conversational chat response.
        """
        
        data_context = ""
        if order_data:
            data_context = f"\nOrder Status: {order_data.get('status')}\nCurrent Location: {order_data.get('current_location')}"
        
        prompt = f"""Generate a friendly, conversational response to this customer message.
Keep it SHORT (1-2 sentences).

Customer: {user_message}
Intent: {intent}{data_context}

Response (conversational, friendly):
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=150
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Chat response generation error: {e}")
            return "Thanks for reaching out! How can I help?"


# Example usage
if __name__ == "__main__":
    # Initialize
    classifier = RetailClassifier()
    generator = ResponseGenerator()
    
    # Test 1: Email classification
    test_email_subject = "Where is my order?"
    test_email_body = "Hi, I placed an order yesterday (ORD-12345) and haven't received it yet. Can you tell me when it will arrive? Thanks!"
    
    print("=== EMAIL CLASSIFICATION ===")
    result = classifier.classify_email(test_email_body, test_email_subject)
    print(json.dumps(result, indent=2))
    
    # Test 2: Chat classification
    print("\n=== CHAT CLASSIFICATION ===")
    test_chat = "Track order #ORD-67890"
    result = classifier.classify_chat(test_chat)
    print(json.dumps(result, indent=2))
    
    # Test 3: Response generation
    print("\n=== RESPONSE GENERATION ===")
    order_data = {
        "order_id": "ORD-12345",
        "status": "shipped",
        "current_location": "Memphis, TN",
        "estimated_delivery": "2025-12-20"
    }
    response = generator.generate_email_response(
        intent="order_tracking",
        customer_name="John Doe",
        order_data=order_data
    )
    print(response["response_body"])
