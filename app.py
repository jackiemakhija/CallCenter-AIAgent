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
    """Simple AI-powered chatbot that classifies intents and responds"""
    
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.conversation_log = []
        
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
    
    def should_escalate(self, intent, sentiment):
        """Determine if escalation needed"""
        return intent in ['complaint', 'payment'] or 'Negative' in sentiment
    
    def handle_request(self, user_message):
        """Process user message and generate response"""
        intent = self.classify_intent(user_message)
        sentiment = self.detect_sentiment(user_message)
        escalate = self.should_escalate(intent, sentiment)
        
        if escalate and intent != 'default':
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
