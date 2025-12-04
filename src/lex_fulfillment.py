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
    
    # 1. Basic Info
    tracking_id = order.get('trackingId', 'N/A')
    order_date = order.get('orderDate', 'N/A')
    
    # 2. Customer Details
    cust = order.get('customer', {})
    c_name = cust.get('name', 'Valued Customer')
    c_email = cust.get('email', 'N/A')
    c_phone = cust.get('phone', 'N/A')
    
    # 3. Delivery Details
    dlv = order.get('delivery', {})
    status = dlv.get('status', 'Unknown')
    carrier = dlv.get('carrier', 'Unknown')
    est_date = dlv.get('estimatedDate', 'Unknown')
    
    # 4. Item Details (Loop through list)
    items_list = ""
    items = order.get('orderDetails', {}).get('items', [])
    for item in items:
        i_name = item.get('name', 'Item')
        i_qty = item.get('quantity', '1')
        i_vendor = item.get('vendor', 'Generic')
        items_list += f"- {i_qty}x {i_name} (sold by {i_vendor})\n"

    # Construct the verbose message required by assessment
    msg = (
        f"Here are the details for Order {tracking_id}:\n"
        f"**Status:** {status}\n"
        f"**Carrier:** {carrier} (Est: {est_date})\n"
        f"**Ordered On:** {order_date}\n\n"
        f"**Items:**\n{items_list}\n"
        f"**Customer:** {c_name} | {c_email} | {c_phone}"
    )
    return msg

def lambda_handler(event, context):
    logger.info(json.dumps(event))
    
    intent_name = event['sessionState']['intent']['name']

    # === WELCOME ===
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

    # === GET ORDER STATUS ===
    if intent_name == 'GetOrderStatus':
        try:
            slots = event['sessionState']['intent']['slots']
            tracking_id = slots['TrackingID']['value']['originalValue']
            tracking_id = tracking_id.upper().strip() # Added strip() for safety
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
                {"contentType": "PlainText", "content": message_content},
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

    # === END CONVERSATION ===
    if intent_name == 'EndConversationIntent':
        return {
            "sessionState": {
                "dialogAction": {"type": "Close"},
                "intent": {"name": intent_name, "state": "Fulfilled"}
            },
            "messages": [{"contentType": "PlainText", "content": "Thank you for using SwiftLine. Have a great day!"}]
        }

    # === FALLBACK ===
    return {
        "sessionState": {"dialogAction": {"type": "Delegate"}},
        "messages": [{"contentType": "PlainText", "content": "I'm not sure how to help with that."}]
    }