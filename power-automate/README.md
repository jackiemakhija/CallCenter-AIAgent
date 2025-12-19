# Power Automate Flow Templates

This directory contains JSON definitions for Power Automate flows. Import these into your Power Automate environment.

## Flow 1: Email Ingestion and Bronze Layer

**Trigger:** When a new email arrives (Outlook connector)

**Actions:**
1. Parse email metadata
2. Extract attachments (if any)
3. Insert into Fabric Lakehouse bronze_emails table
4. Trigger Bronze→Silver pipeline

```json
{
  "name": "Email-Ingestion-Bronze",
  "trigger": {
    "type": "When a new email arrives (V3)",
    "connector": "Office 365 Outlook",
    "parameters": {
      "folderPath": "Inbox/Support",
      "importance": "Any",
      "includeAttachments": true
    }
  },
  "actions": [
    {
      "name": "Parse_Email",
      "type": "Compose",
      "inputs": {
        "email_id": "@{triggerOutputs()?['body/id']}",
        "received_timestamp": "@{triggerOutputs()?['body/receivedDateTime']}",
        "sender_email": "@{triggerOutputs()?['body/from/emailAddress/address']}",
        "sender_name": "@{triggerOutputs()?['body/from/emailAddress/name']}",
        "subject": "@{triggerOutputs()?['body/subject']}",
        "body_text": "@{triggerOutputs()?['body/bodyPreview']}",
        "body_html": "@{triggerOutputs()?['body/body/content']}",
        "has_attachments": "@{triggerOutputs()?['body/hasAttachments']}",
        "conversation_id": "@{triggerOutputs()?['body/conversationId']}",
        "importance": "@{triggerOutputs()?['body/importance']}"
      }
    },
    {
      "name": "Insert_Bronze_Lakehouse",
      "type": "HTTP",
      "inputs": {
        "method": "POST",
        "uri": "https://api.fabric.microsoft.com/v1/workspaces/@{variables('WorkspaceId')}/lakehouses/@{variables('LakehouseId')}/tables/bronze_emails/rows",
        "headers": {
          "Content-Type": "application/json",
          "Authorization": "Bearer @{body('Get_Fabric_Token')?['access_token']}"
        },
        "body": {
          "email_id": "@{outputs('Parse_Email')?['email_id']}",
          "ingestion_timestamp": "@{utcNow()}",
          "received_timestamp": "@{outputs('Parse_Email')?['received_timestamp']}",
          "sender_email": "@{outputs('Parse_Email')?['sender_email']}",
          "sender_name": "@{outputs('Parse_Email')?['sender_name']}",
          "subject": "@{outputs('Parse_Email')?['subject']}",
          "body_text": "@{outputs('Parse_Email')?['body_text']}",
          "body_html": "@{outputs('Parse_Email')?['body_html']}",
          "has_attachments": "@{outputs('Parse_Email')?['has_attachments']}",
          "conversation_id": "@{outputs('Parse_Email')?['conversation_id']}",
          "importance": "@{outputs('Parse_Email')?['importance']}",
          "raw_json": "@{string(triggerOutputs()?['body'])}",
          "ingestion_date": "@{formatDateTime(utcNow(), 'yyyy-MM-dd')}"
        }
      }
    },
    {
      "name": "Trigger_Silver_Pipeline",
      "type": "HTTP",
      "inputs": {
        "method": "POST",
        "uri": "https://api.fabric.microsoft.com/v1/workspaces/@{variables('WorkspaceId')}/items/@{variables('NotebookId')}/jobs/instances?jobType=RunNotebook",
        "headers": {
          "Authorization": "Bearer @{body('Get_Fabric_Token')?['access_token']}"
        },
        "body": {
          "executionData": {
            "parameters": {
              "email_id": "@{outputs('Parse_Email')?['email_id']}"
            }
          }
        }
      }
    }
  ]
}
```

## Flow 2: Email Classification and Response

**Trigger:** Fabric Lakehouse - when new row added to silver_emails

**Actions:**
1. Get customer info from Shopify
2. Call Azure OpenAI for classification
3. Generate automated response
4. Insert into gold_classified_emails
5. Send auto-response (if applicable)

```json
{
  "name": "Email-Classification-Gold",
  "trigger": {
    "type": "When an item is created or modified",
    "connector": "Fabric Lakehouse",
    "parameters": {
      "tableName": "silver_emails"
    }
  },
  "actions": [
    {
      "name": "Get_Customer_Shopify",
      "type": "HTTP",
      "inputs": {
        "method": "GET",
        "uri": "https://@{variables('ShopifyStore')}/admin/api/2024-01/customers/search.json?query=email:@{triggerOutputs()?['sender_email']}",
        "headers": {
          "X-Shopify-Access-Token": "@{variables('ShopifyAccessToken')}"
        }
      }
    },
    {
      "name": "Classify_Email_OpenAI",
      "type": "HTTP",
      "inputs": {
        "method": "POST",
        "uri": "@{variables('AzureOpenAIEndpoint')}/openai/deployments/@{variables('DeploymentName')}/chat/completions?api-version=2024-02-15-preview",
        "headers": {
          "api-key": "@{variables('AzureOpenAIKey')}",
          "Content-Type": "application/json"
        },
        "body": {
          "messages": [
            {
              "role": "system",
              "content": "You are an email classifier for retail customer service."
            },
            {
              "role": "user",
              "content": "Classify this email: Subject: @{triggerOutputs()?['subject']} Body: @{triggerOutputs()?['body_text']}"
            }
          ],
          "temperature": 0.3,
          "max_tokens": 500,
          "response_format": { "type": "json_object" }
        }
      }
    },
    {
      "name": "Parse_Classification",
      "type": "Parse JSON",
      "inputs": {
        "content": "@{body('Classify_Email_OpenAI')?['choices'][0]['message']['content']}",
        "schema": {
          "type": "object",
          "properties": {
            "category": { "type": "string" },
            "confidence": { "type": "number" },
            "priority": { "type": "string" },
            "sentiment_label": { "type": "string" }
          }
        }
      }
    },
    {
      "name": "Condition_Auto_Respond",
      "type": "If",
      "expression": {
        "and": [
          {
            "greater": [
              "@body('Parse_Classification')?['confidence']",
              0.85
            ]
          },
          {
            "equals": [
              "@body('Parse_Classification')?['requires_human_review']",
              false
            ]
          }
        ]
      },
      "actions": {
        "Generate_Response_OpenAI": {
          "type": "HTTP",
          "inputs": {
            "method": "POST",
            "uri": "@{variables('AzureOpenAIEndpoint')}/openai/deployments/@{variables('DeploymentName')}/chat/completions?api-version=2024-02-15-preview",
            "body": {
              "messages": [
                {
                  "role": "system",
                  "content": "Generate helpful customer service response"
                },
                {
                  "role": "user",
                  "content": "Customer: @{triggerOutputs()?['sender_name']} Category: @{body('Parse_Classification')?['category']} Email: @{triggerOutputs()?['body_text']}"
                }
              ]
            }
          }
        },
        "Send_Response_Email": {
          "type": "Send an email (V2)",
          "connector": "Office 365 Outlook",
          "inputs": {
            "to": "@{triggerOutputs()?['sender_email']}",
            "subject": "Re: @{triggerOutputs()?['subject']}",
            "body": "@{body('Generate_Response_OpenAI')?['choices'][0]['message']['content']}"
          }
        }
      }
    }
  ]
}
```

## Flow 3: Chatbot to Fabric Integration

**Trigger:** Power Virtual Agents - conversation ended

**Actions:**
1. Parse conversation data
2. Insert conversation into chat_conversations table
3. Insert messages into chat_messages table
4. Update customer record

```json
{
  "name": "Chatbot-To-Fabric",
  "trigger": {
    "type": "When Power Virtual Agents conversation ends",
    "connector": "Power Virtual Agents"
  },
  "actions": [
    {
      "name": "Parse_Conversation",
      "type": "Compose",
      "inputs": {
        "conversation_id": "@{triggerOutputs()?['ConversationId']}",
        "started_timestamp": "@{triggerOutputs()?['StartTime']}",
        "ended_timestamp": "@{utcNow()}",
        "customer_email": "@{triggerOutputs()?['UserEmail']}",
        "channel": "web",
        "total_messages": "@{length(triggerOutputs()?['Messages'])}"
      }
    },
    {
      "name": "Insert_Conversation_Lakehouse",
      "type": "HTTP",
      "inputs": {
        "method": "POST",
        "uri": "https://api.fabric.microsoft.com/v1/workspaces/@{variables('WorkspaceId')}/lakehouses/@{variables('LakehouseId')}/tables/chat_conversations/rows",
        "body": "@{outputs('Parse_Conversation')}"
      }
    },
    {
      "name": "For_Each_Message",
      "type": "Foreach",
      "foreach": "@triggerOutputs()?['Messages']",
      "actions": {
        "Insert_Message": {
          "type": "HTTP",
          "inputs": {
            "method": "POST",
            "uri": "https://api.fabric.microsoft.com/v1/workspaces/@{variables('WorkspaceId')}/lakehouses/@{variables('LakehouseId')}/tables/chat_messages/rows",
            "body": {
              "message_id": "@{items('For_Each_Message')?['MessageId']}",
              "conversation_id": "@{outputs('Parse_Conversation')?['conversation_id']}",
              "timestamp": "@{items('For_Each_Message')?['Timestamp']}",
              "sender_type": "@{items('For_Each_Message')?['SenderType']}",
              "message_text": "@{items('For_Each_Message')?['Text']}"
            }
          }
        }
      }
    }
  ]
}
```

## Setup Instructions

1. **Import Flows:**
   - Go to Power Automate (https://make.powerautomate.com)
   - Click "My flows" → "Import" → "Import Package (Legacy)"
   - Upload the flow JSON files
   - Configure connections for:
     - Office 365 Outlook
     - Microsoft Fabric
     - HTTP with Azure AD
     - Power Virtual Agents

2. **Configure Variables:**
   Each flow requires these variables:
   - `WorkspaceId`: Your Fabric workspace ID
   - `LakehouseId`: Your Fabric lakehouse ID
   - `AzureOpenAIEndpoint`: Your Azure OpenAI endpoint
   - `AzureOpenAIKey`: Your Azure OpenAI API key
   - `DeploymentName`: Your GPT-4o-mini deployment
   - `ShopifyStore`: Your Shopify store URL
   - `ShopifyAccessToken`: Your Shopify access token

3. **Test Flows:**
   - Start with Flow 1 (Email Ingestion)
   - Send a test email to the support inbox
   - Monitor flow runs in Power Automate
   - Check data in Fabric Lakehouse

4. **Enable Flows:**
   - Turn on all flows
   - Monitor for errors
   - Set up error alerts
