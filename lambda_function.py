import json

with open('products.txt', 'r') as f:
    data = json.load(f)
print(data)

def lambda_handler(event, context):
    print("I am being called")
    # TODO implement
    return {
        "isBase64Encoded": "false",
        'statusCode': 200,
        "headers": {
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': '*',
        'Cache-Control': 'public, max-age=14300',
        'Content-Type': 'application/json'


        },
 #       'body': json.dumps('Again This is the next change I am going GetProductList Lambda....!')
        'body' : json.dumps(data)
    }
