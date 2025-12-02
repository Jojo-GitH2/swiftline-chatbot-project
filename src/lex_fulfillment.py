import json
import os
import boto3
from botocore.exceptions import ClientError

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('ORDERS_TABLE')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    # 1. Parse the Intent
    interpretations = event.get('sessionState', {}).get('intent', {})
    intent_name = interpretations.get('name')

    if intent_name == 'GetOrderStatus':
        return check_order_status(event)

    return close_dialog("Sorry, I didn't understand that request.")

def check_order_status(event):
    # 2. Extract the Slot (Tracking ID)
    slots = event.get('sessionState', {}).get('intent', {}).get('slots', {})
    tracking_id_slot = slots.get('TrackingID')

    if not tracking_id_slot or not tracking_id_slot.get('value'):
        return elicit_slot('TrackingID', "Please provide your tracking number (e.g., SWL-2024-AIR-001234).")

    tracking_id = tracking_id_slot['value']['interpretedValue']

    # 3. Query DynamoDB
    try:
        response = table.get_item(Key={'trackingId': tracking_id})
    except ClientError as e:
        print(e.response['Error']['Message'])
        return close_dialog("I'm having trouble accessing the database right now.")

    if 'Item' not in response:
        return close_dialog(f"I couldn't find an order with ID {tracking_id}. Please check the number and try again.")

    # 4. Format the Response
    item = response['Item']
    message = (
        f"Order Found!\n"
        f"Status: {item['delivery']['status']}\n"
        f"Estimated Delivery: {item['delivery']['estimatedDate']}\n"
        f"Customer: {item['customer']['name']}\n"
        f"Items: {item['orderDetails']['items'][0]['name']} (x{item['orderDetails']['items'][0]['quantity']})"
    )

    return close_dialog(message)

# Helper: Close the conversation
def close_dialog(message):
    return {
        "sessionState": {
            "dialogAction": {
                "type": "Close"
            },
            "intent": {
                "name": "GetOrderStatus",
                "state": "Fulfilled"
            }
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": message
            }
        ]
    }

# Helper: Ask for a specific slot
def elicit_slot(slot_to_elicit, message):
    return {
        "sessionState": {
            "dialogAction": {
                "type": "ElicitSlot",
                "slotToElicit": slot_to_elicit
            },
            "intent": {
                "name": "GetOrderStatus",
                "state": "InProgress"
            }
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": message
            }
        ]
    }