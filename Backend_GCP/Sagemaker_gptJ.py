import boto3

sm_client = boto3.client('sagemaker')

# List all endpoints
endpoints = sm_client.list_endpoints()

for ep in endpoints['Endpoints']:
    print(f"Name: {ep['EndpointName']}, Status: {ep['EndpointStatus']}")