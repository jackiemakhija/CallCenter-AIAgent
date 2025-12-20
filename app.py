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
        
        # Intent patterns
        self.intent_patterns = {
            'order_tracking': ['where', 'track', 'order', 'status', 'delivery', 'when', 'my order'],
            'returns': ['return', 'refund', 'exchange', 'broken', 'damaged', 'defective'],
            'product_info': ['product', 'specs', 'features', 'size', 'color', 'price', 'available'],
            'delivery': ['delivery', 'shipped', 'arrived', 'delay', 'late', 'address'],
            'payment': ['payment', 'charge', 'refund', 'card', 'billing', 'invoice'],
            'complaint': ['complaint', 'unhappy', 'poor', 'bad', 'issue', 'problem']
        }
        
        # Response templates
        self.responses = {
            'order_tracking': "📦 **Order Tracking**\n\nYour order #ORD-12345 is on its way!\n\n• Status: In Transit\n• Carrier: FedEx\n• Tracking: 794617384617\n• Estimated Delivery: Tomorrow by 5 PM\n\n[Track Live](https://fedex.com)",
            'returns': "🔄 **Return Process**\n\nHere's how to return your item:\n\n1. Visit your account ➜ Orders\n2. Select the item ➜ Request Return\n3. Choose reason & print label\n4. Drop at nearest pickup point\n5. Refund in 5-7 business days",
            'product_info': "ℹ️ **Product Details**\n\n**Premium Wireless Headphones**\n• Battery: 30 hours\n• Noise Cancellation: Active\n• Price: $299.99\n• Rating: 4.8/5 ⭐\n\nIn stock - Ready to ship!",
            'delivery': "🚚 **Delivery Information**\n\nYour shipment is on track!\n\n• Current Location: Distribution Center (Chicago)\n• Next Stop: Local Delivery Hub\n• Estimated: 24-48 hours\n\nYou'll receive SMS/Email updates.",
            'payment': "💳 **Payment & Billing**\n\nI can help with:\n• Payment confirmation\n• Invoice details\n• Refund status\n\nWhat specifically do you need?",
            'complaint': "😞 **We Apologize**\n\nI'm escalating to our senior team immediately. They will:\n\n✓ Review your issue\n✓ Contact within 1 hour\n✓ Provide solution",
            'escalate': "🚨 **ESCALATION: Human Agent**\n\n**Agent Assigned:** Sarah (Senior Specialist)\n**Queue Position:** 1st\n**Wait Time:** ~2 minutes\n\nThey will have full context of your issue!",
            'default': "👋 **Hello! How can I help?**\n\nI can assist with:\n• 📦 Order tracking\n• 🔄 Returns & refunds\n• ℹ️ Product info\n• 🚚 Delivery status\n• 💳 Billing\n\nWhat do you need?"
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
        negative_words = ['angry', 'upset', 'frustrated', 'terrible', 'horrible', 'bad', 'broken']
        positive_words = ['great', 'thanks', 'appreciate', 'happy', 'excellent']
        
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
        "Product specs?",
        "I have a payment issue",
        "I'm very unhappy!",
        "Speak to a human"
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
    st.markdown("### 🔧 Environment")
    _env_status = {
        "FOUNDRY": bool(os.getenv("FOUNDRY_BASE")),
        "Power BI": bool(os.getenv("POWER_BI_WORKSPACE_ID")),
        "Azure": bool(os.getenv("AZURE_TENANT_ID")),
    }
    demo_mode = os.getenv("DEMO_MODE", "true").lower() in ("1", "true", "yes")
    all_missing = not any(_env_status.values())

    if demo_mode and all_missing:
        st.markdown(
            "<div class='metric-badge' style='text-align:center;'>Demo Mode: <strong>Enabled</strong> — using mock data. Secrets not required.</div>",
            unsafe_allow_html=True,
        )
        for key in _env_status.keys():
            st.markdown(
                f"<div style='color:#f8fafc; font-weight:600;'>{key}: <span style='color:#8ef0b4; font-weight:700;'>demo</span></div>",
                unsafe_allow_html=True,
            )
        st.caption("Add Space secrets later to connect real services (Foundry, Power BI, Azure).")
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
