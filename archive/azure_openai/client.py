"""
Azure OpenAI Integration Module
Handles email classification, response generation, and semantic search
"""
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from typing import List, Dict, Optional, Tuple
import json
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import settings, CATEGORY_MAPPING, RESPONSE_TEMPLATES

logger = structlog.get_logger()


class OpenAIClient:
    """Azure OpenAI client with retry logic and cost tracking"""
    
    def __init__(self):
        """Initialize Azure OpenAI client"""
        self.client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
        )
        self.deployment = settings.AZURE_OPENAI_DEPLOYMENT_NAME
        self.embedding_deployment = settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
        
        logger.info("Azure OpenAI client initialized", 
                   deployment=self.deployment,
                   endpoint=settings.AZURE_OPENAI_ENDPOINT)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def classify_email(self, subject: str, body: str, 
                      customer_history: Optional[Dict] = None) -> Dict:
        """
        Classify email into category with confidence score
        
        Args:
            subject: Email subject line
            body: Email body text
            customer_history: Optional customer context
            
        Returns:
            Classification result with category, confidence, priority, sentiment
        """
        # Build context-aware prompt
        history_context = ""
        if customer_history:
            history_context = f"""
Customer Context:
- Total Orders: {customer_history.get('total_orders', 0)}
- Lifetime Value: ${customer_history.get('total_spent', 0):.2f}
- Customer Tier: {customer_history.get('customer_tier', 'Regular')}
- Recent Tickets: {customer_history.get('recent_ticket_count', 0)}
"""
        
        prompt = f"""You are an AI assistant classifying customer service emails for a retail company.

{history_context}

Email Subject: {subject}

Email Body:
{body}

Classify this email into ONE of these categories:
- order_tracking: Customer asking about order status or shipping
- returns: Customer wants to return/exchange product or request refund
- product_info: Questions about product details, availability, specifications
- delivery: Issues with delivery, missing packages, delivery delays
- payment: Payment problems, billing questions, refund status
- complaints: Customer complaints, negative feedback, quality issues

Also determine:
1. Priority (urgent/high/medium/low) based on customer tier, sentiment, and issue type
2. Sentiment (positive/neutral/negative) with score from -1.0 to 1.0
3. Whether this requires human review (complex issues, high-value customers, complaints)
4. Extract any mentioned order numbers, tracking numbers, product names

Return your response as JSON with this exact structure:
{{
    "category": "category_name",
    "confidence": 0.95,
    "subcategory": "specific_issue",
    "priority": "high",
    "priority_score": 8,
    "sentiment_label": "negative",
    "sentiment_score": -0.6,
    "emotion": "frustrated",
    "urgency_level": "high",
    "requires_human_review": true,
    "reason": "Brief explanation of classification",
    "extracted_entities": {{
        "order_numbers": ["12345"],
        "tracking_numbers": [],
        "product_names": ["Product X"]
    }}
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are an expert email classifier for customer service. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Calculate cost
            cost = self._calculate_cost(
                response.usage.prompt_tokens,
                response.usage.completion_tokens
            )
            
            # Add metadata
            result['tokens_used'] = response.usage.total_tokens
            result['cost_usd'] = cost
            result['model'] = self.deployment
            
            logger.info("Email classified", 
                       category=result['category'],
                       confidence=result['confidence'],
                       priority=result['priority'],
                       tokens=response.usage.total_tokens,
                       cost_usd=cost)
            
            return result
            
        except Exception as e:
            logger.error("Email classification failed", error=str(e))
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate_response(self, classification: Dict, email_content: Dict,
                         customer_info: Dict, context: Optional[Dict] = None) -> Dict:
        """
        Generate automated response for email
        
        Args:
            classification: Classification result from classify_email
            email_content: Original email subject and body
            customer_info: Customer information
            context: Additional context (order info, tracking, etc.)
            
        Returns:
            Generated response with confidence and metadata
        """
        category = classification['category']
        
        # Get template
        template = RESPONSE_TEMPLATES.get(category, "")
        
        # Build context
        context_str = ""
        if context:
            if 'order_info' in context:
                order = context['order_info']
                context_str += f"\nOrder #{order.get('order_number')}: {order.get('status')}"
            if 'tracking_info' in context:
                tracking = context['tracking_info']
                context_str += f"\nTracking: {tracking.get('tracking_number')} - {tracking.get('status')}"
        
        prompt = f"""You are a helpful customer service agent for a retail company.

Customer: {customer_info.get('full_name', 'Valued Customer')}
Email: {customer_info.get('email')}
Tier: {customer_info.get('customer_tier', 'Regular')}
Lifetime Value: ${customer_info.get('total_spent', 0):.2f}

Original Email Subject: {email_content['subject']}
Original Email: {email_content['body'][:500]}

Category: {category}
Sentiment: {classification.get('sentiment_label', 'Neutral')}

{context_str}

Generate a professional, empathetic, and helpful response that:
1. Addresses the customer's specific concern
2. Uses the customer's name
3. Provides clear next steps or resolution
4. Maintains a friendly, professional tone
5. Is concise (2-3 paragraphs maximum)
6. For VIP customers, adds extra appreciation

Template to follow:
{template}

Return JSON with:
{{
    "response_text": "Full response email text",
    "confidence": 0.9,
    "requires_review": false,
    "suggested_actions": ["action1", "action2"],
    "estimated_resolution_time": "24 hours"
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are an expert customer service agent. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Calculate cost
            cost = self._calculate_cost(
                response.usage.prompt_tokens,
                response.usage.completion_tokens
            )
            
            # Add metadata
            result['tokens_used'] = response.usage.total_tokens
            result['cost_usd'] = cost
            result['model'] = self.deployment
            
            logger.info("Response generated",
                       category=category,
                       confidence=result.get('confidence'),
                       tokens=response.usage.total_tokens,
                       cost_usd=cost)
            
            return result
            
        except Exception as e:
            logger.error("Response generation failed", error=str(e))
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for semantic search
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector (1536 dimensions)
        """
        try:
            response = self.client.embeddings.create(
                model=self.embedding_deployment,
                input=text
            )
            
            embedding = response.data[0].embedding
            
            logger.debug("Embedding generated",
                        dimensions=len(embedding),
                        tokens=response.usage.total_tokens)
            
            return embedding
            
        except Exception as e:
            logger.error("Embedding generation failed", error=str(e))
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def semantic_search_kb(self, query: str, category: Optional[str] = None,
                          top_k: int = 3) -> List[Dict]:
        """
        Search knowledge base using semantic similarity
        
        Args:
            query: Search query
            category: Optional category filter
            top_k: Number of results to return
            
        Returns:
            List of relevant KB articles with similarity scores
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query)
        
        # In production, this would query Fabric with vector similarity
        # For now, return placeholder
        # TODO: Implement vector similarity search in Fabric or Azure AI Search
        
        logger.info("KB search executed",
                   query_length=len(query),
                   category=category,
                   top_k=top_k)
        
        return []
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on token usage"""
        input_cost = input_tokens * settings.COST_INPUT_TOKEN
        output_cost = output_tokens * settings.COST_OUTPUT_TOKEN
        total_cost = input_cost + output_cost
        return round(total_cost, 6)
    
    def estimate_monthly_cost(self, daily_emails: int, daily_chats: int,
                            avg_tokens_per_request: int = 1000) -> Dict:
        """
        Estimate monthly OpenAI costs
        
        Args:
            daily_emails: Expected daily email volume
            daily_chats: Expected daily chat volume
            avg_tokens_per_request: Average tokens per API call
            
        Returns:
            Cost breakdown and projections
        """
        # Email processing: 2 API calls (classify + generate)
        email_tokens_per_day = daily_emails * avg_tokens_per_request * 2
        email_cost_per_day = (
            email_tokens_per_day * 0.5 * settings.COST_INPUT_TOKEN +
            email_tokens_per_day * 0.5 * settings.COST_OUTPUT_TOKEN
        )
        
        # Chat processing: 3-5 exchanges per chat
        chat_tokens_per_day = daily_chats * avg_tokens_per_request * 4
        chat_cost_per_day = (
            chat_tokens_per_day * 0.5 * settings.COST_INPUT_TOKEN +
            chat_tokens_per_day * 0.5 * settings.COST_OUTPUT_TOKEN
        )
        
        total_cost_per_day = email_cost_per_day + chat_cost_per_day
        monthly_cost = total_cost_per_day * 30
        
        return {
            "email_cost_daily": round(email_cost_per_day, 2),
            "chat_cost_daily": round(chat_cost_per_day, 2),
            "total_cost_daily": round(total_cost_per_day, 2),
            "estimated_monthly_cost": round(monthly_cost, 2),
            "budget_monthly": settings.MONTHLY_BUDGET_OPENAI,
            "budget_utilization_pct": round((monthly_cost / settings.MONTHLY_BUDGET_OPENAI) * 100, 2),
            "daily_email_volume": daily_emails,
            "daily_chat_volume": daily_chats
        }


# Global client instance
_openai_client: Optional[OpenAIClient] = None


def get_openai_client() -> OpenAIClient:
    """Get or create global OpenAI client instance"""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient()
    return _openai_client
