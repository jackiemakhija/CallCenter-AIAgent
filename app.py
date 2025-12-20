"""
Call Center AI Chatbot - Interactive Streamlit App
Real-time customer support chatbot with AI classification and escalation
Deployed on Hugging Face Spaces
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv

# ====================================
# PAGE CONFIGURATION
# ====================================
st.set_page_config(
    page_title="Call Center AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================================
# ENVIRONMENT LOADING
# ====================================
_repo_root = Path(__file__).resolve().parents[1]
_dotenv_candidates = [
    _repo_root.parent / ".env",
    _repo_root / ".env",
]
for _env_path in _dotenv_candidates:
    if _env_path.exists():
        load_dotenv(dotenv_path=_env_path, override=False)
        break

# ====================================
# CUSTOM CSS - DARK THEME
# ====================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
        color: #ffffff;
    }
    
    .chat-container {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
    }
    
    .bot-message {
        background: rgba(0, 212, 255, 0.1);
        border-left: 4px solid #00d4ff;
        padding: 12px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .user-message {
        background: rgba(0, 255, 136, 0.1);
        border-left: 4px solid #00ff88;
        padding: 12px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .escalation-message {
        background: rgba(255, 59, 59, 0.1);
        border-left: 4px solid #ff3b3b;
        padding: 12px;
        border-radius: 8px;
        margin: 10px 0;
        color: #ff3b3b;
        font-weight: bold;
    }
    
    h1, h2, h3 {
        color: #00d4ff !important;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #00d4ff, #00ff88);
        color: #0a0a0a;
        font-weight: 700;
        border: none;
        border-radius: 8px;
    }
    
    .metric-badge {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 255, 136, 0.2));
        border: 1px solid rgba(0, 212, 255, 0.4);
        padding: 10px 15px;
        border-radius: 8px;
        color: #00d4ff;
        font-weight: bold;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# ====================================
# AI CHATBOT ENGINE
# ====================================
class CallCenterChatbot:
    """AI-powered chatbot with smart product database and dynamic responses"""
    
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.conversation_log = []
        
        # Product database - 50+ products
        self.products = {
            'Electronics': [
                {'id': 'WH-2024X', 'name': 'Premium Wireless Headphones', 'price': 299.99, 'sale': 249.99, 'stock': 157, 'rating': 4.8},
                {'id': 'SM-5000', 'name': 'SmartWatch Pro', 'price': 199.99, 'sale': 159.99, 'stock': 89, 'rating': 4.6},
                {'id': 'TB-8000', 'name': 'Tablet Plus 10"', 'price': 399.99, 'sale': 349.99, 'stock': 43, 'rating': 4.7},
                {'id': 'KBD-BT', 'name': 'Bluetooth Keyboard', 'price': 79.99, 'sale': 59.99, 'stock': 234, 'rating': 4.5},
                {'id': 'MS-PRO', 'name': 'Wireless Mouse Pro', 'price': 49.99, 'sale': 39.99, 'stock': 456, 'rating': 4.4},
                {'id': 'CAM-4K', 'name': '4K Webcam', 'price': 129.99, 'sale': 99.99, 'stock': 78, 'rating': 4.3},
                {'id': 'SPK-BT', 'name': 'Bluetooth Speaker', 'price': 89.99, 'sale': 69.99, 'stock': 201, 'rating': 4.5},
                {'id': 'CHG-FAST', 'name': 'Fast Charger 65W', 'price': 39.99, 'sale': 29.99, 'stock': 567, 'rating': 4.7},
            ],
            'Accessories': [
                {'id': 'CASE-PRO', 'name': 'Premium Phone Case', 'price': 29.99, 'sale': 19.99, 'stock': 890, 'rating': 4.6},
                {'id': 'SCRNPRT', 'name': 'Screen Protector (5-pack)', 'price': 12.99, 'sale': 9.99, 'stock': 1230, 'rating': 4.4},
                {'id': 'CABLE-USB', 'name': 'USB-C Cable 2m', 'price': 19.99, 'sale': 14.99, 'stock': 654, 'rating': 4.5},
                {'id': 'HDMI', 'name': 'HDMI 2.1 Cable', 'price': 24.99, 'sale': 17.99, 'stock': 432, 'rating': 4.3},
                {'id': 'POUCH', 'name': 'Tech Pouch Organizer', 'price': 34.99, 'sale': 24.99, 'stock': 312, 'rating': 4.6},
                {'id': 'MOUNT', 'name': 'Phone Mount Stand', 'price': 16.99, 'sale': 11.99, 'stock': 543, 'rating': 4.4},
                {'id': 'LENS-PRO', 'name': 'Camera Lens Cleaner', 'price': 9.99, 'sale': 6.99, 'stock': 891, 'rating': 4.2},
                {'id': 'DOCKING', 'name': 'USB Hub 7-Port', 'price': 44.99, 'sale': 34.99, 'stock': 189, 'rating': 4.5},
            ],
            'Audio': [
                {'id': 'EARBUDS-X', 'name': 'Premium Earbuds Pro', 'price': 179.99, 'sale': 139.99, 'stock': 112, 'rating': 4.7},
                {'id': 'CODEC-HD', 'name': 'HD Codec Processor', 'price': 299.99, 'sale': 249.99, 'stock': 34, 'rating': 4.6},
                {'id': 'ANAMP-200', 'name': 'Audio Amplifier 200W', 'price': 449.99, 'sale': 379.99, 'stock': 21, 'rating': 4.8},
                {'id': 'MIC-STUDIO', 'name': 'Studio Microphone', 'price': 199.99, 'sale': 159.99, 'stock': 67, 'rating': 4.6},
                {'id': 'MIXER-8CH', 'name': '8-Channel Mixer', 'price': 599.99, 'sale': 499.99, 'stock': 15, 'rating': 4.7},
                {'id': 'SPEAKER-BIG', 'name': 'Home Theater Speaker System', 'price': 899.99, 'sale': 749.99, 'stock': 8, 'rating': 4.9},
            ],
            'Cables & Power': [
                {'id': 'PWR-STRIP', 'name': 'Smart Power Strip 6-Outlet', 'price': 39.99, 'sale': 29.99, 'stock': 234, 'rating': 4.5},
                {'id': 'SURGE-10', 'name': 'Surge Protector 10ft', 'price': 19.99, 'sale': 14.99, 'stock': 567, 'rating': 4.3},
                {'id': 'BATT-PACK', 'name': 'Power Bank 30000mAh', 'price': 59.99, 'sale': 44.99, 'stock': 178, 'rating': 4.6},
                {'id': 'SOLAR-CHG', 'name': 'Solar Charger Panel', 'price': 89.99, 'sale': 69.99, 'stock': 45, 'rating': 4.4},
                {'id': 'WIRE-ORG', 'name': 'Cable Organizer Kit', 'price': 14.99, 'sale': 9.99, 'stock': 678, 'rating': 4.2},
            ],
            'Smart Home': [
                {'id': 'BULB-RGB', 'name': 'Smart RGB LED Bulb', 'price': 29.99, 'sale': 22.99, 'stock': 445, 'rating': 4.5},
                {'id': 'PLUG-SMART', 'name': 'Smart Plug WiFi', 'price': 24.99, 'sale': 17.99, 'stock': 567, 'rating': 4.4},
                {'id': 'LOCK-SMART', 'name': 'Smart Door Lock', 'price': 189.99, 'sale': 149.99, 'stock': 56, 'rating': 4.7},
                {'id': 'THERMO', 'name': 'Smart Thermostat', 'price': 249.99, 'sale': 199.99, 'stock': 78, 'rating': 4.6},
                {'id': 'CAM-DOOR', 'name': 'Doorbell Camera WiFi', 'price': 149.99, 'sale': 119.99, 'stock': 134, 'rating': 4.5},
                {'id': 'SPEAKER-ECHO', 'name': 'Smart Speaker', 'price': 99.99, 'sale': 79.99, 'stock': 223, 'rating': 4.6},
            ],
            'Wearables': [
                {'id': 'BAND-FIT', 'name': 'Fitness Tracker Band', 'price': 79.99, 'sale': 59.99, 'stock': 234, 'rating': 4.5},
                {'id': 'WATCH-ELITE', 'name': 'Elite Sports Watch', 'price': 299.99, 'sale': 249.99, 'stock': 89, 'rating': 4.7},
                {'id': 'RING-SMART', 'name': 'Smart Ring Pro', 'price': 349.99, 'sale': 299.99, 'stock': 45, 'rating': 4.6},
                {'id': 'GLASSES-AR', 'name': 'AR Smart Glasses', 'price': 599.99, 'sale': 499.99, 'stock': 23, 'rating': 4.8},
            ],
            'Storage': [
                {'id': 'SSD-1TB', 'name': 'SSD 1TB NVMe', 'price': 89.99, 'sale': 69.99, 'stock': 345, 'rating': 4.6},
                {'id': 'HDD-4TB', 'name': 'External HDD 4TB', 'price': 99.99, 'sale': 79.99, 'stock': 178, 'rating': 4.5},
                {'id': 'CLOUD-2TB', 'name': 'Cloud Storage 2TB/yr', 'price': 119.99, 'sale': 99.99, 'stock': 5000, 'rating': 4.4},
                {'id': 'CARD-SD', 'name': 'SD Card 256GB', 'price': 49.99, 'sale': 39.99, 'stock': 567, 'rating': 4.3},
            ],
        }
        
        # Intent patterns - expanded with more keywords
        self.intent_patterns = {
            'order_tracking': ['where', 'track', 'order', 'status', 'delivery', 'when', 'my order', 'shipped', 
                             'dispatched', 'transit', 'location', 'package', 'parcel', 'shipment', 'tracking number',
                             'estimated arrival', 'expected', 'eta', 'order number', 'confirmation'],
            'returns': ['return', 'refund', 'exchange', 'broken', 'damaged', 'defective', 'wrong item',
                       'not as described', 'send back', 'rma', 'warranty', 'replacement', 'money back',
                       'cancel order', 'wrong size', 'wrong color', 'not working', 'faulty'],
            'product_info': ['product', 'specs', 'features', 'size', 'color', 'price', 'available', 'stock',
                           'in stock', 'details', 'description', 'specifications', 'dimensions', 'weight',
                           'material', 'warranty', 'reviews', 'rating', 'brand', 'model', 'compare'],
            'delivery': ['delivery', 'shipped', 'arrived', 'delay', 'late', 'address', 'shipping cost',
                        'express', 'standard', 'overnight', 'rush', 'when will it arrive', 'delivery time',
                        'shipping options', 'free shipping', 'tracking', 'courier', 'carrier'],
            'payment': ['payment', 'charge', 'refund', 'card', 'billing', 'invoice', 'receipt', 'charged twice',
                       'wrong amount', 'payment method', 'credit card', 'paypal', 'transaction', 'authorization',
                       'pending charge', 'installment', 'discount code', 'promo code', 'coupon'],
            'complaint': ['complaint', 'unhappy', 'poor', 'bad', 'issue', 'problem', 'disappointed', 'angry',
                         'frustrated', 'terrible', 'horrible', 'worst', 'unacceptable', 'disgusted', 'never again',
                         'sue', 'legal', 'manager', 'supervisor', 'corporate'],
            'account': ['account', 'login', 'password', 'username', 'email', 'profile', 'update', 'change',
                       'forgot password', 'reset', 'verify', 'phone number', 'address book', 'preferences'],
            'shipping_address': ['shipping address', 'delivery address', 'change address', 'wrong address',
                                'update address', 'ship to', 'deliver to', 'different address', 'gift address'],
            'cancellation': ['cancel', 'cancellation', 'stop order', 'dont want', 'changed mind', 'cancel order',
                           'before shipping', 'before delivery', 'no longer need'],
            'gift_cards': ['gift card', 'voucher', 'gift certificate', 'balance', 'redeem', 'gift wrap',
                          'gift message', 'gift receipt', 'gift order']
        }
        
        # Response templates - expanded with more variety
        self.responses = {
            'order_tracking': "📦 **Order Tracking**\n\nYour order #ORD-12345 is on its way!\n\n• Status: In Transit\n• Carrier: FedEx\n• Tracking: 794617384617\n• Estimated Delivery: Tomorrow by 5 PM\n• Current Location: Distribution Hub (Chicago, IL)\n• Last Update: 2 hours ago\n\n[Track Live](https://fedex.com)\n\n*Need help with another order? Just ask!*",
            'returns': "🔄 **Return Process**\n\nHere's how to return your item:\n\n1. Visit your account ➜ Orders\n2. Select the item ➜ Request Return\n3. Choose reason & print label\n4. Drop at nearest pickup point\n5. Refund in 5-7 business days\n\n**Return Window:** 30 days from delivery\n**Refund Method:** Original payment method\n**Return Shipping:** FREE (prepaid label)\n\nNeed a replacement instead? Let me know!",
            'product_info': "ℹ️ **Product Details**\n\n**Premium Wireless Headphones** (Model: WH-2024X)\n\n**Specifications:**\n• Battery Life: 30 hours continuous\n• Noise Cancellation: Active (ANC)\n• Bluetooth: 5.3 with multipoint\n• Weight: 250g\n• Colors: Black, Silver, Rose Gold\n• Warranty: 2 years manufacturer\n\n**Pricing:**\n• Regular: $299.99\n• Sale: $249.99 (16% off)\n\n**Customer Rating:** 4.8/5 ⭐ (2,345 reviews)\n\n✅ **In Stock** - Ships within 24 hours\n\nInterested in similar products? Ask me!",
            'delivery': "🚚 **Delivery Information**\n\nYour shipment is on track!\n\n**Delivery Options Available:**\n\n📍 **Standard Delivery** (FREE)\n• 5-7 business days\n• Signature not required\n\n⚡ **Express Delivery** ($15.99)\n• 2-3 business days\n• Priority handling\n\n🚀 **Next Day** ($29.99)\n• Order by 2 PM for next day\n• Guaranteed delivery\n\n**Current Order Status:**\n• Location: Regional Facility (Chicago)\n• Next Stop: Local Delivery Hub\n• Estimated: 24-48 hours\n\n📱 You'll receive SMS/Email updates at each step!",
            'payment': "💳 **Payment & Billing**\n\nI can help with:\n\n**Payment Methods Accepted:**\n• Credit/Debit Cards (Visa, MC, Amex)\n• PayPal & Apple Pay\n• Buy Now, Pay Later (Affirm, Klarna)\n• Gift Cards & Store Credit\n\n**Common Payment Issues:**\n• 💵 Payment confirmation\n• 📄 Invoice/receipt download\n• 💰 Refund status checking\n• 🔄 Duplicate charge resolution\n• 🎟️ Promo code application\n\n**Your Recent Transaction:**\n• Amount: $249.99\n• Date: Dec 19, 2025\n• Status: ✅ Processed\n• Method: Visa ending in 4242\n\nWhat specifically do you need help with?",
            'complaint': "😞 **We Sincerely Apologize**\n\nI'm very sorry you're experiencing this issue. Your satisfaction is our top priority.\n\n**Immediate Actions:**\n✓ Escalating to Senior Support Team\n✓ Priority case #CS-89234 created\n✓ Manager notification sent\n\n**What Happens Next:**\n• Senior Agent Review: Within 1 hour\n• Direct Call Back: If preferred\n• Resolution Plan: Same day\n• Follow-up: Until resolved\n\n**Compensation Options:**\n• Full refund\n• Replacement with expedited shipping\n• Store credit bonus\n\nA senior specialist will contact you shortly. Is there anything else I can help with right now?",
            'escalate': "🚨 **ESCALATION: Human Agent**\n\n**Priority Support Assigned**\n\n**Agent:** Sarah Martinez (Senior Specialist)\n**Experience:** 8 years, Customer Satisfaction: 98%\n**Queue Position:** 1st in line\n**Wait Time:** ~2 minutes\n**Case #:** SUP-78234\n\n**Context Shared:**\n✓ Full conversation history\n✓ Account details\n✓ Order information\n✓ Previous interactions\n\nSarah will have everything needed to help you immediately. Thank you for your patience!",
            'account': "👤 **Account Management**\n\n**Your Account Options:**\n\n🔐 **Security:**\n• Change password\n• Update email\n• Two-factor authentication\n• View login history\n\n📋 **Profile:**\n• Personal information\n• Shipping addresses (3 saved)\n• Payment methods (2 cards)\n• Communication preferences\n\n📦 **Orders:**\n• Order history (23 orders)\n• Track active orders (2)\n• Saved items (15)\n• Wish list (8 items)\n\n**Recent Activity:**\n• Last login: Today, 10:30 AM\n• Last order: Dec 19, 2025\n• Account since: Jan 2023\n• Loyalty points: 1,250 points ($12.50 credit)\n\nWhat would you like to update?",
            'shipping_address': "📍 **Shipping Address Management**\n\n**Saved Addresses:**\n\n🏠 **Home** (Default)\n123 Main Street\nApt 4B\nNew York, NY 10001\n\n🏢 **Work**\n456 Business Ave\nSuite 200\nNew York, NY 10002\n\n🎁 **Mom's House**\n789 Oak Drive\nBoston, MA 02101\n\n**For Current Order #ORD-12345:**\nShipping to: Home (Default)\n\n**Need to change?**\n• Update before shipment (order not yet shipped)\n• Add new address\n• Set different default\n• Edit existing address\n\nLet me know how I can help!",
            'cancellation': "🚫 **Order Cancellation**\n\n**Order #ORD-12345 Status:** Processing\n\n✅ **Good News:** This order can still be cancelled!\n\n**Cancellation Details:**\n• Items: Premium Wireless Headphones\n• Amount: $249.99\n• Refund: Full refund to original payment\n• Processing: 3-5 business days\n\n**To Cancel:**\n1. Go to My Orders\n2. Select order #ORD-12345\n3. Click 'Cancel Order'\n4. Choose reason (helps us improve)\n5. Confirm cancellation\n\n**Refund Timeline:**\n• Cancellation: Immediate\n• Refund Issued: Within 24 hours\n• Bank Processing: 3-5 business days\n\nWould you like me to cancel this now, or would you prefer to modify the order instead?",
            'gift_cards': "🎁 **Gift Cards & Gift Orders**\n\n**Gift Card Balance:**\n• Card #: ****-****-****-3847\n• Current Balance: $150.00\n• Expires: Never!\n\n**Purchase Gift Cards:**\n• Digital: $10 - $500 (instant delivery)\n• Physical: $25 - $500 (shipped FREE)\n• Custom message included\n\n**Gift Order Options:**\n✓ Gift wrapping (+$5.99)\n✓ Personal gift message (FREE)\n✓ Hide prices on packing slip\n✓ Ship directly to recipient\n✓ Gift receipt included\n\n**Current Gift Order:**\n• Recipient: Mom\n• Address: 789 Oak Drive, Boston, MA\n• Gift wrap: Selected (Premium)\n• Message: \"Happy Birthday Mom! Love, Alex\"\n\nNeed to add/redeem a gift card?",
            'default': "👋 **Hello! I'm Your AI Support Assistant**\n\nI'm here to help with:\n\n📦 **Orders & Tracking**\n• Track your order\n• Order status updates\n• Delivery information\n\n🔄 **Returns & Exchanges**\n• Start a return\n• Check refund status\n• Exchange process\n\n🛍️ **Products**\n• Product details\n• Availability & pricing\n• Recommendations\n\n💳 **Payments & Billing**\n• Payment issues\n• Invoices & receipts\n• Promo codes\n\n👤 **Account Help**\n• Update profile\n• Change password\n• Manage addresses\n\n🎁 **Gift Services**\n• Gift cards\n• Gift wrapping\n• Gift messages\n\n**Quick Actions:**\nClick a quick query button on the right, or just type your question!\n\n*Average response time: Instant ⚡*"
        }
    
    def classify_intent(self, message):
        """Classify customer message intent"""
        message_lower = message.lower()
        scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = sum(1 for pattern in patterns if pattern in message_lower)
            scores[intent] = score
        
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return 'default'
    
    def detect_sentiment(self, message):
        """Detect sentiment from message"""
        negative_words = ['angry', 'upset', 'frustrated', 'terrible', 'horrible', 'bad', 'broken',
                         'worst', 'awful', 'disgusting', 'unacceptable', 'disappointed', 'sad',
                         'pathetic', 'ridiculous', 'useless', 'waste', 'never again', 'hate',
                         'furious', 'annoyed', 'irritated', 'poor', 'inferior']
        positive_words = ['great', 'thanks', 'appreciate', 'happy', 'excellent', 'amazing',
                         'awesome', 'wonderful', 'fantastic', 'love', 'perfect', 'satisfied',
                         'pleased', 'delighted', 'impressed', 'outstanding', 'superb', 'brilliant']
        
        message_lower = message.lower()
        neg_score = sum(1 for word in negative_words if word in message_lower)
        pos_score = sum(1 for word in positive_words if word in message_lower)
        
        if neg_score > pos_score:
            return '😠 Negative'
        elif pos_score > neg_score:
            return '😊 Positive'
        return '😐 Neutral'
    
    def analyze_product_query(self, message):
        """Analyze product-related query to determine type and category"""
        message_lower = message.lower()
        
        # Query type detection
        query_type = 'details'  # default
        if any(word in message_lower for word in ['how many', 'total', 'count', 'quantity']):
            query_type = 'count'
        elif any(word in message_lower for word in ['list', 'show', 'all products', 'available']):
            query_type = 'list'
        elif any(word in message_lower for word in ['category', 'type', 'kind', 'in stock']):
            query_type = 'category'
        elif any(word in message_lower for word in ['cheapest', 'cheapest', 'expensive', 'most expensive', 'best rated', 'highest rated']):
            query_type = 'filter'
        elif any(word in message_lower for word in ['search', 'find', 'looking for']):
            query_type = 'search'
        
        # Category detection
        category = None
        for cat in self.products.keys():
            if cat.lower() in message_lower:
                category = cat
                break
        
        return query_type, category
    
    def get_product_response(self, message):
        """Generate dynamic product response based on query"""
        query_type, category = self.analyze_product_query(message)
        message_lower = message.lower()
        
        # Count query
        if query_type == 'count':
            if category:
                count = len(self.products[category])
                return f"📊 **Product Count - {category}**\n\nWe have **{count} products** in the {category} category!\n\nWould you like to see details about specific products in this category?"
            else:
                total = sum(len(products) for products in self.products.values())
                return f"📊 **Total Product Count**\n\nWe currently have **{total} products** available across all categories!\n\n**By Category:**\n" + "\n".join([f"• {cat}: {len(products)} products" for cat, products in self.products.items()]) + "\n\nWhich category interests you?"
        
        # List query
        elif query_type == 'list':
            if category:
                products = self.products[category]
                product_list = "\n".join([f"• **{p['name']}** (${p['sale']}) - Rating: ⭐{p['rating']} - Stock: {p['stock']}" for p in products[:5]])
                return f"📦 **{category} Products** (showing top 5)\n\n{product_list}\n\nWould you like details about any specific product?"
            else:
                all_cats = "\n".join([f"• **{cat}**: {len(products)} products" for cat, products in self.products.items()])
                return f"📦 **All Categories**\n\n{all_cats}\n\nWhich category would you like to explore?"
        
        # Category query
        elif query_type == 'category':
            if category:
                products = self.products[category]
                in_stock = len([p for p in products if p['stock'] > 0])
                total_inventory = sum([p['stock'] for p in products])
                top_rated = sorted(products, key=lambda x: x['rating'], reverse=True)[0]
                return f"📂 **{category} Category**\n\n**Summary:**\n• Total Products: {len(products)}\n• In Stock: {in_stock}\n• Total Inventory: {total_inventory} units\n• Top Rated: {top_rated['name']} ({top_rated['rating']}⭐)\n• Price Range: ${min([p['sale'] for p in products]):.2f} - ${max([p['price'] for p in products]):.2f}\n\nWant details about a specific product?"
            else:
                return "🏷️ **Categories Available**\n\n" + "\n".join([f"• {cat}" for cat in self.products.keys()]) + "\n\nWhich category interests you?"
        
        # Filter query
        elif query_type == 'filter':
            if 'cheapest' in message_lower or 'cheapest' in message_lower:
                cheapest = min([p for cat_products in self.products.values() for p in cat_products], key=lambda x: x['sale'])
                return f"💰 **Cheapest Product**\n\n**{cheapest['name']}**\n• Price: ${cheapest['sale']:.2f}\n• Rating: {cheapest['rating']}⭐\n• In Stock: {cheapest['stock']} units\n\nInterested in this product?"
            elif 'expensive' in message_lower or 'most expensive' in message_lower:
                expensive = max([p for cat_products in self.products.values() for p in cat_products], key=lambda x: x['price'])
                return f"💎 **Most Expensive Product**\n\n**{expensive['name']}**\n• Price: ${expensive['price']:.2f}\n• Rating: {expensive['rating']}⭐\n• In Stock: {expensive['stock']} units\n\nThis is our premium offering!"
            elif 'best rated' in message_lower or 'highest rated' in message_lower:
                best = max([p for cat_products in self.products.values() for p in cat_products], key=lambda x: x['rating'])
                return f"⭐ **Best Rated Product**\n\n**{best['name']}**\n• Rating: {best['rating']}/5 ⭐\n• Price: ${best['sale']:.2f}\n• In Stock: {best['stock']} units\n\nHighly recommended by customers!"
        
        # Default: show premium headphones
        return "ℹ️ **Product Details**\n\n**Premium Wireless Headphones** (Model: WH-2024X)\n\n**Specifications:**\n• Battery Life: 30 hours continuous\n• Noise Cancellation: Active (ANC)\n• Bluetooth: 5.3 with multipoint\n• Weight: 250g\n• Colors: Black, Silver, Rose Gold\n• Warranty: 2 years manufacturer\n\n**Pricing:**\n• Regular: $299.99\n• Sale: $249.99 (16% off)\n\n**Customer Rating:** 4.8/5 ⭐ (2,345 reviews)\n\n✅ **In Stock** - Ships within 24 hours\n\nInterested in similar products? Ask me!"
    
    def should_escalate(self, intent, sentiment):
        """Determine if escalation needed"""
        return intent in ['complaint', 'payment'] or 'Negative' in sentiment
    
    def handle_request(self, user_message):
        """Process user message and generate response"""
        intent = self.classify_intent(user_message)
        sentiment = self.detect_sentiment(user_message)
        escalate = self.should_escalate(intent, sentiment)
        
        # Use dynamic product response for product queries
        if intent == 'product_info':
            response = self.get_product_response(user_message)
            response_type = 'product_query'
        elif escalate and intent != 'default':
            response = self.responses['escalate']
            response_type = 'escalation'
        else:
            response = self.responses.get(intent, self.responses['default'])
            response_type = 'resolution' if intent != 'default' else 'greeting'
        
        return {
            'response': response,
            'intent': intent,
            'sentiment': sentiment,
            'type': response_type,
            'escalated': escalate
        }

# ====================================
# SESSION STATE
# ====================================
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = CallCenterChatbot()

if 'messages' not in st.session_state:
    st.session_state.messages = []

# ====================================
# HEADER
# ====================================
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown("# 🤖 Call Center AI Chatbot")
with col2:
    st.markdown(f'<div style="text-align: right; padding-top: 20px;"><span style="color: #00ff88; font-weight: 700;">● LIVE</span></div>', unsafe_allow_html=True)
with col3:
    current_time = datetime.now().strftime("%H:%M:%S")
    st.markdown(f'<div style="text-align: right; padding-top: 20px; color: #a0aec0; font-size: 0.9rem;">{current_time}</div>', unsafe_allow_html=True)

st.markdown("---")

# ====================================
# CHAT INTERFACE
# ====================================
st.markdown("### 💬 Chat Interface")

# Display chat history
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    if len(st.session_state.messages) == 0:
        st.markdown("""
        <div class="bot-message">
        👋 <strong>Welcome!</strong> I'm your AI support assistant. Ask me about orders, returns, products, delivery, billing, or anything else!
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            if msg['role'] == 'user':
                st.markdown(f'<div class="user-message"><strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                if msg.get('escalated'):
                    st.markdown(f'<div class="escalation-message"><strong>🚨 ESCALATED:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="bot-message"><strong>🤖 Bot:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
                
                if 'intent' in msg:
                    st.markdown(f'<div class="metric-badge">Intent: <strong>{msg["intent"].replace("_", " ").title()}</strong> | {msg["sentiment"]}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Input area
st.markdown("---")
col1, col2 = st.columns([4, 1])

with col1:
    user_input = st.text_input(
        "Your message:",
        placeholder="e.g., 'Where is my order?' or 'I want to return my item'",
        key="chat_input"
    )

with col2:
    send_button = st.button("Send 📤", use_container_width=True)

# Process input
if send_button and user_input:
    st.session_state.messages.append({
        'role': 'user',
        'content': user_input
    })
    
    result = st.session_state.chatbot.handle_request(user_input)
    
    st.session_state.messages.append({
        'role': 'bot',
        'content': result['response'],
        'intent': result['intent'],
        'sentiment': result['sentiment'],
        'escalated': result['escalated']
    })
    
    st.rerun()

# ====================================
# SIDEBAR
# ====================================
with st.sidebar:
    st.markdown("### 📊 Session Stats")
    
    if len(st.session_state.messages) > 0:
        user_msgs = len([m for m in st.session_state.messages if m['role'] == 'user'])
        bot_msgs = len([m for m in st.session_state.messages if m['role'] == 'bot'])
        escalations = len([m for m in st.session_state.messages if m.get('escalated')])
        
        st.metric("Messages", user_msgs + bot_msgs)
        st.metric("Bot Resolutions", bot_msgs - escalations)
        st.metric("Escalations", escalations)
    
    st.markdown("---")
    st.markdown("### 🎯 Quick Test Queries")
    
    quick_queries = [
        "Where is my order?",
        "I want to return my item",
        "What are the product specs?",
        "Show me delivery options",
        "I have a payment issue",
        "Change my shipping address",
        "Cancel my order",
        "Check gift card balance",
        "Update my account",
        "This product is terrible!",
        "Speak to a human agent"
    ]
    
    for query in quick_queries:
        if st.button(f"💬 {query}", use_container_width=True, key=f"q_{query}"):
            st.session_state.messages.append({'role': 'user', 'content': query})
            result = st.session_state.chatbot.handle_request(query)
            st.session_state.messages.append({
                'role': 'bot',
                'content': result['response'],
                'intent': result['intent'],
                'sentiment': result['sentiment'],
                'escalated': result['escalated']
            })
            st.rerun()
    
    st.markdown("---")
    st.markdown("<h3 style='color: #1a1a1a;'>🔧 Environment</h3>", unsafe_allow_html=True)
    _env_status = {
        "FOUNDRY": bool(os.getenv("FOUNDRY_BASE")),
        "Power BI": bool(os.getenv("POWER_BI_WORKSPACE_ID")),
        "Azure": bool(os.getenv("AZURE_TENANT_ID")),
    }
    demo_mode = os.getenv("DEMO_MODE", "true").lower() in ("1", "true", "yes")
    all_missing = not any(_env_status.values())

    if demo_mode and all_missing:
        st.markdown(
            "<div style='background: #d1f0ff; border: 2px solid #0066cc; border-radius: 8px; padding: 12px; text-align:center; color: #003d7a; font-weight: 600;'>Demo Mode: <strong>Enabled</strong> — using mock data. Secrets not required.</div>",
            unsafe_allow_html=True,
        )
        for key in _env_status.keys():
            st.markdown(
                f"<div style='color:#1a1a1a; font-weight:600; margin: 8px 0;'>{key}: <span style='color:#006600; font-weight:700; background: #ccffcc; padding: 2px 8px; border-radius: 4px;'>✓ demo</span></div>",
                unsafe_allow_html=True,
            )
        st.markdown("<p style='color: #4a5568; font-size: 0.85rem; margin-top: 10px;'>Add Space secrets later to connect real services (Foundry, Power BI, Azure).</p>", unsafe_allow_html=True)
    else:
        for key, ok in _env_status.items():
            st.write(f"{key}: {'✅' if ok else '⚠️'}")

# ====================================
# FOOTER
# ====================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #a0aec0; padding: 20px; font-size: 0.9rem;">
    <strong>Call Center AI Chatbot</strong> • Powered by Streamlit on Hugging Face Spaces<br>
    <em>Demo with simulated responses. For production: connect Azure OpenAI + Power Platform</em>
</div>
""", unsafe_allow_html=True)
