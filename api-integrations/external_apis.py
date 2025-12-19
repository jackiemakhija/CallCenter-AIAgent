import requests
import logging
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class ShopifyAPI:
    """Shopify API integration for order and product data."""
    
    def __init__(self, store_url: str, access_token: str):
        self.store_url = store_url
        self.access_token = access_token
        self.base_url = f"https://{store_url}/admin/api/2024-01"
        self.headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }
    
    def get_order(self, order_id: str) -> Dict:
        """Fetch order details by ID."""
        url = f"{self.base_url}/orders/{order_id}.json"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()["order"]
    
    def search_orders_by_email(self, email: str) -> List[Dict]:
        """Search orders by customer email."""
        url = f"{self.base_url}/orders.json"
        params = {"query": f"email:{email}", "limit": 10}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()["orders"]
    
    def get_product(self, product_id: str) -> Dict:
        """Fetch product details."""
        url = f"{self.base_url}/products/{product_id}.json"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()["product"]
    
    def create_return(self, order_id: str, line_items: List[Dict]) -> Dict:
        """Initiate a return for order items."""
        url = f"{self.base_url}/orders/{order_id}/returns.json"
        payload = {
            "return": {
                "line_items": line_items,
                "return_reason": "CUSTOMER_REQUEST"
            }
        }
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()["return"]


class FedExUPSAPI:
    """Unified tracking API for FedEx and UPS."""
    
    def __init__(self, fedex_api_key: str, ups_api_key: str):
        self.fedex_api_key = fedex_api_key
        self.ups_api_key = ups_api_key
    
    def track_fedex(self, tracking_number: str) -> Dict:
        """Track FedEx shipment."""
        url = "https://apis.fedex.com/track/v1/tracknumbers"
        headers = {
            "Authorization": f"Bearer {self._get_fedex_token()}",
            "Content-Type": "application/json"
        }
        payload = {
            "trackingInfo": [{"trackingNumber": tracking_number}],
            "includeDetailedScans": True
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        # Extract relevant fields
        tracking = response.json()["output"]["completeTrackResults"][0]["trackResults"][0]
        return {
            "tracking_number": tracking_number,
            "status": tracking.get("latestStatusDetail", {}).get("code"),
            "current_location": tracking.get("latestStatusDetail", {}).get("location"),
            "estimated_delivery": tracking.get("estimatedDeliveryTimestamp"),
            "events": tracking.get("scanEvents", [])
        }
    
    def track_ups(self, tracking_number: str) -> Dict:
        """Track UPS shipment."""
        url = f"https://onlinetools.ups.com/track/v1/details/{tracking_number}"
        headers = {
            "Authorization": f"Bearer {self.ups_api_key}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        shipment = response.json()["shipments"][0]
        return {
            "tracking_number": tracking_number,
            "status": shipment.get("status"),
            "current_location": shipment.get("currentLocation"),
            "estimated_delivery": shipment.get("estimatedDeliveryDate"),
            "events": shipment.get("statusHistory", [])
        }
    
    def _get_fedex_token(self) -> str:
        """Get FedEx OAuth token (cached)."""
        # In production, implement token caching
        url = "https://apis.fedex.com/oauth/authorize"
        response = requests.post(url, data={
            "grant_type": "client_credentials",
            "client_id": self.fedex_api_key.split(":")[0],
            "client_secret": self.fedex_api_key.split(":")[1]
        })
        return response.json()["access_token"]


class StripeAPI:
    """Stripe API integration for payment data."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def get_charge(self, charge_id: str) -> Dict:
        """Fetch charge details."""
        import stripe
        stripe.api_key = self.api_key
        charge = stripe.Charge.retrieve(charge_id)
        return {
            "charge_id": charge.id,
            "amount": charge.amount / 100,  # Convert cents to dollars
            "status": charge.status,
            "customer_id": charge.customer,
            "refunded": charge.refunded,
            "refund_amount": charge.amount_refunded / 100 if charge.amount_refunded else 0,
            "created": datetime.fromtimestamp(charge.created)
        }
    
    def get_customer_charges(self, customer_id: str, limit: int = 10) -> List[Dict]:
        """Get all charges for a customer."""
        import stripe
        stripe.api_key = self.api_key
        charges = stripe.Charge.list(customer=customer_id, limit=limit)
        return [
            {
                "charge_id": c.id,
                "amount": c.amount / 100,
                "status": c.status,
                "created": datetime.fromtimestamp(c.created)
            }
            for c in charges.data
        ]
    
    def create_refund(self, charge_id: str, amount: Optional[float] = None, reason: str = None) -> Dict:
        """Create a refund for a charge."""
        import stripe
        stripe.api_key = self.api_key
        refund_kwargs = {"charge": charge_id}
        if amount:
            refund_kwargs["amount"] = int(amount * 100)  # Convert to cents
        if reason:
            refund_kwargs["reason"] = reason
        
        refund = stripe.Refund.create(**refund_kwargs)
        return {
            "refund_id": refund.id,
            "charge_id": refund.charge,
            "amount": refund.amount / 100,
            "status": refund.status,
            "created": datetime.fromtimestamp(refund.created)
        }


# Example usage
if __name__ == "__main__":
    # Initialize APIs
    shopify = ShopifyAPI(
        store_url="mystore.myshopify.com",
        access_token="YOUR_SHOPIFY_API_TOKEN"
    )
    
    tracking = FedExUPSAPI(
        fedex_api_key="YOUR_FEDEX_KEY",
        ups_api_key="YOUR_UPS_KEY"
    )
    
    stripe = StripeAPI(api_key="YOUR_STRIPE_KEY")
    
    # Test: Get order details
    try:
        order = shopify.get_order("ORD-12345")
        print(f"Order: {order['order_number']} - Status: {order['fulfillment_status']}")
    except Exception as e:
        logger.error(f"Shopify error: {e}")
    
    # Test: Track shipment
    try:
        tracking_info = tracking.track_fedex("7942657890")
        print(f"Tracking: {tracking_info['status']} at {tracking_info['current_location']}")
    except Exception as e:
        logger.error(f"Tracking error: {e}")
    
    # Test: Get charge
    try:
        charge = stripe.get_charge("ch_1234567890")
        print(f"Charge: ${charge['amount']} - {charge['status']}")
    except Exception as e:
        logger.error(f"Stripe error: {e}")
