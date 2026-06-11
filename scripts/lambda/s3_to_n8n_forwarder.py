import json
import urllib.request

N8N_WEBHOOK_URL = "https://vigilant-yodel-97wxgw49r5p62p649-5678.app.github.dev/webhook/cad-pipeline"

def lambda_handler(event, context):
    data = json.dumps(event).encode("utf-8")
    req = urllib.request.Request(
        N8N_WEBHOOK_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as response:
        print("n8n response:", response.status)
    return {"statusCode": 200}
