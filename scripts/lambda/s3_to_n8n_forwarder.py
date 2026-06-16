import json
import logging
import os
import urllib.request
import urllib.error

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Forward S3 events to n8n webhook"""
    
    # Get webhook URL from environment variable
    webhook_url = os.environ.get("N8N_WEBHOOK_URL")
    if not webhook_url:
        logger.error("N8N_WEBHOOK_URL environment variable not set")
        return {"statusCode": 500, "body": json.dumps({"error": "Configuration error"})}
    
    if not event:
        logger.error("Event is empty")
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid event"})}
    
    try:
        data = json.dumps(event).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as response:
            logger.info(f"n8n response: {response.status}")
            return {"statusCode": 200, "body": json.dumps({"message": "Success"})}
    
    except urllib.error.URLError as e:
        logger.error(f"Failed to reach webhook: {e}")
        return {"statusCode": 502, "body": json.dumps({"error": "Webhook unreachable"})}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": "Internal server error"})}
