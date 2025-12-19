"""
Shopify Integration Module
Syncs customer data, orders, and provides real-time order information
"""
import shopify
import requests
from typing import Dict, List, Optional
import structlog
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import settings

logger = structlog.get_logger()


class ShopifyClient:
    """Shopify API client for customer and order management"""
    
    def __init__(self):
        """Initialize Shopify API client"""
        self.api_key = settings.SHOPIFY_API_KEY
        self.api_secret = settings.SHOPIFY_API_SECRET
        self.store_url = settings.SHOPIFY_STORE_URL
        self.access_token = settings.SHOPIFY_ACCESS_TOKEN
        
        # Initialize Shopify session
        shopify.Session.setup(api_key=self.api_key, secret=self.api_secret)
        self.session = shopify.Session(
            self.store_url,
            "2024-01",  # API version
            self.access_token
        )
        shopify.ShopifyResource.activate_session(self.session)
        
        logger.info("Shopify client initialized", store=self.store_url)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def get_customer_by_email(self, email: str) -> Optional[Dict]:
        """
        Get customer information by email
        
        Args:
            email: Customer email address
            
        Returns:
            Customer data or None if not found
        """
        try:
            customers = shopify.Customer.search(query=f"email:{email}")
            
            if not customers:
                logger.info("Customer not found", email=email)
                return None
            
            customer = customers[0]
            
            # Transform to our format
            customer_data = {
                "customer_id": f"shopify_{customer.id}",
                "shopify_id": customer.id,
                "email": customer.email,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "full_name": f"{customer.first_name} {customer.last_name}".strip(),
                "phone": customer.phone,
                "total_orders": customer.orders_count,
                "total_spent": float(customer.total_spent) if customer.total_spent else 0.0,
                "average_order_value": float(customer.total_spent) / customer.orders_count if customer.orders_count > 0 else 0.0,
                "created_at": customer.created_at,
                "updated_at": customer.updated_at,
                "accepts_marketing": customer.accepts_marketing,
                "email_verified": customer.verified_email,
                "tags": customer.tags.split(", ") if customer.tags else [],
                "status": customer.state,
                "default_address": self._format_address(customer.default_address) if customer.default_address else None
            }
            
            # Determine customer tier
            customer_data["customer_tier"] = self._determine_customer_tier(
                customer_data["total_spent"],
                customer_data["total_orders"]
            )
            
            logger.info("Customer retrieved",
                       email=email,
                       customer_id=customer_data["customer_id"],
                       tier=customer_data["customer_tier"],
                       total_spent=customer_data["total_spent"])
            
            return customer_data
            
        except Exception as e:
            logger.error("Failed to retrieve customer", email=email, error=str(e))
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def get_order(self, order_number: str) -> Optional[Dict]:
        """
        Get order information by order number
        
        Args:
            order_number: Order number (e.g., "12345")
            
        Returns:
            Order data or None if not found
        """
        try:
            orders = shopify.Order.find(name=f"#{order_number}")
            
            if not orders:
                logger.info("Order not found", order_number=order_number)
                return None
            
            order = orders[0]
            
            order_data = {
                "order_id": order.id,
                "order_number": order_number,
                "order_name": order.name,
                "created_at": order.created_at,
                "updated_at": order.updated_at,
                "status": order.financial_status,
                "fulfillment_status": order.fulfillment_status,
                "total_price": float(order.total_price),
                "currency": order.currency,
                "customer_email": order.email,
                "customer_id": f"shopify_{order.customer.id}" if order.customer else None,
                "line_items": [
                    {
                        "product_id": item.product_id,
                        "variant_id": item.variant_id,
                        "title": item.title,
                        "quantity": item.quantity,
                        "price": float(item.price)
                    }
                    for item in order.line_items
                ],
                "shipping_address": self._format_address(order.shipping_address) if order.shipping_address else None,
                "tracking_numbers": [],
                "tracking_urls": []
            }
            
            # Get fulfillment/tracking info
            if order.fulfillments:
                for fulfillment in order.fulfillments:
                    if fulfillment.tracking_number:
                        order_data["tracking_numbers"].append(fulfillment.tracking_number)
                    if fulfillment.tracking_url:
                        order_data["tracking_urls"].append(fulfillment.tracking_url)
            
            logger.info("Order retrieved",
                       order_number=order_number,
                       status=order_data["status"],
                       fulfillment_status=order_data["fulfillment_status"],
                       total=order_data["total_price"])
            
            return order_data
            
        except Exception as e:
            logger.error("Failed to retrieve order", order_number=order_number, error=str(e))
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def get_customer_orders(self, customer_email: str, limit: int = 10) -> List[Dict]:
        """
        Get recent orders for customer
        
        Args:
            customer_email: Customer email
            limit: Maximum number of orders to return
            
        Returns:
            List of order data
        """
        try:
            customer = self.get_customer_by_email(customer_email)
            
            if not customer:
                return []
            
            # Get customer's orders
            orders = shopify.Order.find(customer_id=customer["shopify_id"], limit=limit)
            
            order_list = []
            for order in orders:
                order_list.append({
                    "order_number": order.name.replace("#", ""),
                    "created_at": order.created_at,
                    "status": order.financial_status,
                    "fulfillment_status": order.fulfillment_status,
                    "total_price": float(order.total_price),
                    "currency": order.currency
                })
            
            logger.info("Customer orders retrieved",
                       email=customer_email,
                       order_count=len(order_list))
            
            return order_list
            
        except Exception as e:
            logger.error("Failed to retrieve customer orders", email=customer_email, error=str(e))
            return []
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def sync_customers_bulk(self, since_date: Optional[datetime] = None) -> List[Dict]:
        """
        Bulk sync customers from Shopify
        
        Args:
            since_date: Only sync customers updated after this date
            
        Returns:
            List of customer data
        """
        if since_date is None:
            since_date = datetime.now() - timedelta(days=30)
        
        try:
            customers = shopify.Customer.find(
                updated_at_min=since_date.isoformat(),
                limit=250
            )
            
            customer_list = []
            for customer in customers:
                customer_data = {
                    "customer_id": f"shopify_{customer.id}",
                    "shopify_id": customer.id,
                    "email": customer.email,
                    "first_name": customer.first_name,
                    "last_name": customer.last_name,
                    "phone": customer.phone,
                    "total_orders": customer.orders_count,
                    "total_spent": float(customer.total_spent) if customer.total_spent else 0.0,
                    "created_at": customer.created_at,
                    "updated_at": customer.updated_at,
                    "tags": customer.tags.split(", ") if customer.tags else []
                }
                customer_list.append(customer_data)
            
            logger.info("Customers synced",
                       count=len(customer_list),
                       since_date=since_date)
            
            return customer_list
            
        except Exception as e:
            logger.error("Failed to sync customers", error=str(e))
            raise
    
    def _format_address(self, address) -> Dict:
        """Format Shopify address to our format"""
        if not address:
            return None
        
        return {
            "address1": address.address1,
            "address2": address.address2,
            "city": address.city,
            "province": address.province,
            "country": address.country,
            "zip": address.zip
        }
    
    def _determine_customer_tier(self, total_spent: float, total_orders: int) -> str:
        """Determine customer tier based on spending and order history"""
        if total_spent >= 5000 or total_orders >= 50:
            return "VIP"
        elif total_spent >= 1000 or total_orders >= 10:
            return "Regular"
        elif total_orders > 0:
            return "New"
        else:
            return "Prospect"


# Global client instance
_shopify_client: Optional[ShopifyClient] = None


def get_shopify_client() -> ShopifyClient:
    """Get or create global Shopify client instance"""
    global _shopify_client
    if _shopify_client is None:
        _shopify_client = ShopifyClient()
    return _shopify_client
