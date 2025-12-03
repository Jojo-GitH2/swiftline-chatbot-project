import json
import boto3
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('ORDERS_TABLE')
table = dynamodb.Table(TABLE_NAME)

def get_order_details(tracking_id):
    try:
        response = table.get_item(Key={'trackingId': tracking_id})
        return response.get('Item')
    except Exception as e:
        logger.error(f"Error fetching order: {str(e)}")
        return None

def format_response(order):
    if not order:
        return "I couldn't find an order with that tracking ID. Please check the number and try again."
    
    status = order.get('delivery', {}).get('status', 'Unknown')
    carrier = order.get('delivery', {}).get('carrier', 'Unknown')
    est_date = order.get('delivery', {}).get('estimatedDate', 'Unknown')
    customer = order.get('customer', {}).get('name', 'Valued Customer')
    
    msg = (f"Hello {customer}. Order {order['trackingId']} is currently **{status}** via {carrier}. "
           f"It is estimated to arrive by {est_date}.")
    return msg

def lambda_handler(event, context):
    logger.info(json.dumps(event))
    
    intent_name = event['sessionState']['intent']['name']

    # === 1. WELCOME / MAIN MENU ===
    if intent_name == 'WelcomeIntent':
        return {
            "sessionState": {
                "dialogAction": {"type": "Close"},
                "intent": {"name": intent_name, "state": "Fulfilled"}
            },
            "messages": [
                {
                    "contentType": "ImageResponseCard",
                    "imageResponseCard": {
                        "title": "SwiftLine Support",
                        "subtitle": "What would you like to do?",
                        "buttons": [
                            {
                                "text": "Track my Order",
                                "value": "Track my order"
                            }
                        ]
                    }
                }
            ]
        }

    # === 2. GET ORDER STATUS (With Closing Loop) ===
    if intent_name == 'GetOrderStatus':
        try:
            slots = event['sessionState']['intent']['slots']
            tracking_id = slots['TrackingID']['value']['originalValue']
            tracking_id = tracking_id.upper()
        except (KeyError, TypeError):
            return {
                "sessionState": {"dialogAction": {"type": "Close"}},
                "messages": [{"contentType": "PlainText", "content": "I encountered an error reading the tracking number."}]
            }
        
        order_data = get_order_details(tracking_id)
        message_content = format_response(order_data)
        
        return {
            "sessionState": {
                "dialogAction": {"type": "Close"},
                "intent": {"name": intent_name, "state": "Fulfilled"}
            },
            "messages": [
                # Message 1: The Result
                {"contentType": "PlainText", "content": message_content},
                # Message 2: The Loop Question
                {
                    "contentType": "ImageResponseCard",
                    "imageResponseCard": {
                        "title": "Is there anything else?",
                        "subtitle": "Would you like to do something else?",
                        "buttons": [
                            {
                                "text": "Yes",
                                "value": "Main Menu" 
                            },
                            {
                                "text": "No",
                                "value": "No thanks"
                            }
                        ]
                    }
                }
            ]
        }

    # === 3. END CONVERSATION (New) ===
    if intent_name == 'EndConversationIntent':
        return {
            "sessionState": {
                "dialogAction": {"type": "Close"},
                "intent": {"name": intent_name, "state": "Fulfilled"}
            },
            "messages": [{"contentType": "PlainText", "content": "Thank you for using SwiftLine. Have a great day!"}]
        }

    # === 4. FALLBACK ===
    return {
        "sessionState": {"dialogAction": {"type": "Delegate"}},
        "messages": [{"contentType": "PlainText", "content": "I'm not sure how to help with that."}]
    }