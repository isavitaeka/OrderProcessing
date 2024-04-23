import json
from datetime import datetime
import uuid
import os
import boto3
import logging
logger = logging.getLogger()
logger.setLevel("INFO")

#set env variables
#DATETIME = os.environ['GET_DATETIME']
#UUID = os.environ['GET_UUID']
#QUEUE_URL = os.environ['QUEUE_URL']
#orderId = str(uuid.uuid4())
SOURCE_EMAIL_ADDRESS = 'savita@savitasingh18.shop'
ORDER_QUEUE = 'https://sqs.eu-north-1.amazonaws.com/706824313294/SubmitOrder' 
ORDER_TABLE = 'OrderDB'



def lambda_handler(event, context):
    
    logger.info(event)
    # Queue Resource
    sqs = boto3.resource('sqs')
    # Dynamo DB Resouce 
    client = boto3.resource('dynamodb')
    
    # SNS & SQS Resource
    clientSNS = boto3.client('sns',region_name='eu-north-1')
    logger.info ("Initialise SNS Queue")
    
    queue = sqs.Queue(ORDER_QUEUE)
    logger.info ("Initialise SQS Queue")

    ses_client = boto3.client('ses', region_name='us-east-1')



    try:
        #for message in queue.receive_messages():
        #    data = message.body
        #    data = json.loads(data)
        #    logger.info("Event: ", event);
            
        #    print(data)
            
        #    print ("Event: %s" % json.dumps(data))

        #    message.delete()
            
            # Generating Order id
            orderId = str(uuid.uuid4())
            id = orderId
        
            logger.info("Order Id generated : " + orderId)
            
            # Extract Order data from the POST event
            productId = event['id']
            name = event['name']
            deviceType = event['deviceType']
            brand = event['brand']
            model = event['model']
            screenSize = event['screenSize']
            email = event['email']
            customerName = event['customerName']
            image = event['image']
            logger.info ("Data extracted from Order request")
    
    
            #Upload Order in the Order Database
            table = client.Table(ORDER_TABLE)
            response = table.put_item(
    	       Item={
    	        'id': orderId,
    	        'productId': productId,
                'name': name,
                'deviceType' : deviceType,
                'brand' : brand,
                'model' : model,
                'screenSize' : screenSize,
                'email' : email, 
                'customerName' : customerName,
                'status' : 'OrderAcknowledged',
                'image' : image

            }
            )
            
            logger.info("Order Submitted by");
            logger.info(customerName);



            # Push Order int the Queue for further processing
            message = {
    	        'id': orderId,
    	        'productId': productId,
                'name': name,
                'deviceType' : deviceType,
                'brand' : brand,
                'model' : model,
                'screenSize' : screenSize,
                'email' : email, 
                'customerName' : customerName,
                'status' : 'OrderAcknowledged'
                }

            messageBody = json.dumps(message)
            logger.info(messageBody)
            response = queue.send_message(MessageBody=messageBody)
            logger.info("Queue Response")
            logger.info(response)
            
            logMsg = "Order Submitted by " + customerName + " [" + email + "], [" + orderId +  "]"
            logger.info(logMsg)
            
            
            # Send Notification to the User to User
            emailMessage = "Dear " + customerName + "\n\n\Thank you for placing the Order. \n\nYou will get back to you Shortly on the Order.  Thank You\nsavitasingh.shop"
            subject = "Order : " + orderId
            
                
            logger.info ("Sending email");    
            response = ses_client.send_email(
            Destination={
                'ToAddresses': [email]
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': 'UTF-8',
                        'Data': emailMessage,
                    }
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': subject,
                },
            },
            Source=SOURCE_EMAIL_ADDRESS
            )
            
            logger.info (response);
            
            logMsg = "Email sent to the customer " + customerName
            logger.info(logMsg)
            
    

            return {
                "statusCode" : 200,
                "status" : "OrderAcknowledged",
                "result" : "OrderAck",
                "id" : id
                
            }

    except Exception as e:
        
        logger.error("ERROR while acknowledging ")
        logger.info(e)
        
        
        #return json.dumps(data)
        return {
            "statusCode" : 500,
            "status" : "System ERROR"
            
        }
        print(e)