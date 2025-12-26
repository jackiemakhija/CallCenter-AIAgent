"""
Interactive Chatbot Demo - Power Virtual Agents Simulation
Shows how the chatbot handles customer queries with real-time responses
"""

import json
from datetime import datetime

class ChatbotDemo:
    """Simulates Power Virtual Agents chatbot interactions"""
    
    def __init__(self):
        self.conversation_history = []
        self.customer_context = {
            "customer_id": "CUST-001",
            "name": "Sarah Johnson",
            "email": "sarah.j@example.com",
            "loyalty_tier": "gold",
            "recent_orders": [
                {"order_id": "ORD-12345", "status": "shipped", "date": "2025-12-10", "tracking": "FX9876543210"},
                {"order_id": "ORD-12340", "status": "delivered", "date": "2025-11-28", "amount": 149.99}
            ]
        }
    
    def welcome_message(self):
        return """
╔════════════════════════════════════════════════════════════════╗
║           🤖 RETAIL SUPPORT BOT - LIVE DEMO                   ║
║           Powered by Power Virtual Agents + Azure OpenAI      ║
╚════════════════════════════════════════════════════════════════╝

Bot: Hi! I'm your virtual assistant. How can I help you today?

Quick options:
  1. 📦 Track my order
  2. 🔄 Return an item
  3. 📍 Delivery questions
  4. 💳 Payment issues
  5. 📞 Speak to a human agent

Type your question or choose a number...
"""
    
    def classify_intent(self, message):
        """Simulates Azure OpenAI intent classification"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["track", "where", "order", "shipment", "delivery status"]):
            return {"intent": "order_tracking", "confidence": 0.95, "sentiment": "neutral"}
        elif any(word in message_lower for word in ["return", "refund", "send back"]):
            return {"intent": "returns", "confidence": 0.92, "sentiment": "neutral"}
        elif any(word in message_lower for word in ["product", "in stock", "price", "shipping cost"]):
            return {"intent": "product_info", "confidence": 0.88, "sentiment": "neutral"}
        elif any(word in message_lower for word in ["delivery", "arrive", "when", "package"]):
            return {"intent": "delivery_question", "confidence": 0.90, "sentiment": "neutral"}
        elif any(word in message_lower for word in ["charge", "payment", "refund", "money", "twice"]):
            return {"intent": "payment_issue", "confidence": 0.97, "sentiment": "negative"}
        elif any(word in message_lower for word in ["human", "agent", "person", "speak", "talk"]):
            return {"intent": "escalate_to_human", "confidence": 1.0, "sentiment": "neutral"}
        else:
            return {"intent": "general_inquiry", "confidence": 0.60, "sentiment": "neutral"}
    
    def handle_order_tracking(self):
        """Demo: Order tracking flow"""
        order = self.customer_context["recent_orders"][0]
        
        return f"""
Bot: Let me check your order status...

📦 Order #{order['order_id']}
   Status: {order['status'].upper()}
   Tracking: {order['tracking']}
   Expected: Today by 5:00 PM
   
🚚 Current Location: Local delivery hub - Memphis, TN
📍 Out for delivery

Track it here: https://fedex.com/track/{order['tracking']}

Is there anything else you'd like to know about this order?
"""
    
    def handle_returns(self):
        """Demo: Returns processing flow"""
        return """
Bot: I can help you with that! Here's how to return an item:

📋 STEP 1: Initiate Return
   • Log in to your account: retailcompany.com/orders
   • Click "Return" next to the order
   • Select items and reason

📦 STEP 2: Ship It Back
   • We'll email you a prepaid FedEx label
   • Pack the item securely
   • Drop at any FedEx location

✅ STEP 3: Get Your Refund
   • Once received, full refund in 5-7 business days
   • Refund goes to original payment method

Which order would you like to return?
  • Order #ORD-12345 (Blue Hoodie, shipped Dec 10)
  • Order #ORD-12340 (Gray T-Shirt, delivered Nov 28)
"""
    
    def handle_payment_issue(self):
        """Demo: Payment escalation (critical)"""
        return """
Bot: I understand this is frustrating. Payment issues are important to us.

⚠️  I'm connecting you with our Payments Specialist right away.

🔄 Transferring chat to Sarah (Payments Team Lead)...

[ESCALATION DATA CAPTURED]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Priority: CRITICAL
Customer: Sarah Johnson (Gold member)
Issue: Payment concern
Confidence: 97%
Sentiment: NEGATIVE
Conversation history: [Available to agent]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Agent Sarah: Hi! I see you have a payment concern. I've pulled up your account 
            and I'm here to help resolve this immediately. Can you tell me 
            more about what happened?
"""
    
    def handle_escalation(self):
        """Demo: Direct escalation to human agent"""
        return """
Bot: Of course! Let me connect you with a live agent.

🔄 Searching for available agent...
✓ Found: Mike (Customer Support)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HANDOFF TO HUMAN AGENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Customer: Sarah Johnson (sarah.j@example.com)
Loyalty: Gold Member
Previous orders: 2 in last 30 days
Chat history: [Full conversation passed to agent]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Agent Mike: Hi Sarah! Thanks for your patience. How can I help you today?
"""
    
    def chat(self, user_message):
        """Main chat handler"""
        print(f"\nYou: {user_message}")
        print("\n[Processing...]")
        
        # Classify intent
        classification = self.classify_intent(user_message)
        print(f"[Intent: {classification['intent']}, Confidence: {classification['confidence']}, Sentiment: {classification['sentiment']}]")
        
        # Log to conversation history
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "classification": classification
        })
        
        # Generate response based on intent
        if classification["intent"] == "order_tracking":
            response = self.handle_order_tracking()
        elif classification["intent"] == "returns":
            response = self.handle_returns()
        elif classification["intent"] == "payment_issue":
            response = self.handle_payment_issue()
        elif classification["intent"] == "escalate_to_human":
            response = self.handle_escalation()
        elif classification["confidence"] < 0.7:
            response = """
Bot: I'm not quite sure I understood that correctly. Let me connect you 
     with a human agent who can better assist you.
     
🔄 Transferring to agent...
"""
        else:
            response = """
Bot: I'd be happy to help! Could you provide more details about what you're 
     looking for? Or I can connect you with a live agent if that's easier.
"""
        
        print(response)
        
        # Log bot response
        self.conversation_history[-1]["bot_response"] = response
        
        # Log to Fabric (simulated)
        self.log_interaction(classification)
        
        return response
    
    def log_interaction(self, classification):
        """Simulates logging to Fabric Lakehouse"""
        fabric_log = {
            "chat_id": f"CHAT-{len(self.conversation_history)}",
            "customer_id": self.customer_context["customer_id"],
            "intent": classification["intent"],
            "confidence": classification["confidence"],
            "sentiment": classification["sentiment"],
            "timestamp": datetime.now().isoformat(),
            "escalated": classification["intent"] in ["payment_issue", "escalate_to_human"] or classification["confidence"] < 0.7
        }
        print(f"\n[✓ Logged to Fabric: silver_chat_messages table]")
        print(f"[Chat ID: {fabric_log['chat_id']}, Escalated: {fabric_log['escalated']}]")
    
    def run_demo(self):
        """Run interactive demo"""
        print(self.welcome_message())
        
        # Predefined demo scenarios
        scenarios = [
            ("Where is my order?", "order_tracking"),
            ("I want to return my blue hoodie", "returns"),
            ("I was charged twice!", "payment_issue"),
            ("Can I speak to a human?", "escalate_to_human")
        ]
        
        print("\n" + "="*70)
        print("DEMO MODE: Running 4 pre-programmed scenarios")
        print("="*70)
        
        for i, (message, expected_intent) in enumerate(scenarios, 1):
            print(f"\n{'─'*70}")
            print(f"SCENARIO {i}: {expected_intent.upper().replace('_', ' ')}")
            print("─"*70)
            
            self.chat(message)
            
            input("\n[Press Enter to continue to next scenario...]")
        
        # Summary
        print("\n" + "="*70)
        print("DEMO SUMMARY")
        print("="*70)
        print(f"\nTotal interactions: {len(self.conversation_history)}")
        print(f"Customer: {self.customer_context['name']} ({self.customer_context['loyalty_tier'].upper()} member)")
        
        escalations = sum(1 for conv in self.conversation_history 
                         if conv['classification']['intent'] in ['payment_issue', 'escalate_to_human'] 
                         or conv['classification']['confidence'] < 0.7)
        
        print(f"Escalated to human: {escalations}/{len(self.conversation_history)}")
        print(f"Bot-resolved: {len(self.conversation_history) - escalations}/{len(self.conversation_history)}")
        
        print("\n" + "="*70)
        print("HOW THIS WORKS IN PRODUCTION")
        print("="*70)
        print("""
1. Customer visits website → Chat widget opens (Power Virtual Agents)
2. User types message → Sent to Power Automate flow
3. Power Automate calls Azure OpenAI → Classifies intent + sentiment
4. Based on intent:
   • Order tracking → Query Fabric DW → Return status + tracking
   • Returns → Generate return label → Email to customer
   • Payment issue → ESCALATE immediately to payments team
   • Low confidence → ESCALATE to human agent
5. Response sent back to chatbot → Customer sees answer in <2 seconds
6. All interactions logged to Fabric Lakehouse → Analytics dashboard updates
7. If escalated → Human agent gets full context + conversation history

Key Features:
✓ <2 second response time
✓ 24/7 availability
✓ Handles 800+ chats/day automatically
✓ Smart escalation (only 20-25% need humans)
✓ Full conversation history for agents
✓ Real-time analytics & monitoring
✓ Continuous learning from interactions
""")

if __name__ == "__main__":
    print("\n")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║    INTERACTIVE CHATBOT DEMO - POWER VIRTUAL AGENTS            ║")
    print("║    Retail Call Center AI Solution                             ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    demo = ChatbotDemo()
    demo.run_demo()
    
    print("\n\n📁 Want to see the actual configuration?")
    print("   Check: power-virtual-agents/chatbot_configuration.md")
    print("\n🚀 Ready to deploy?")
    print("   Follow: documentation/COMPLETE_RUNBOOK.md (Phase 3: PVA setup)")
