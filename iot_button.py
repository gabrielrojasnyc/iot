import os
import logging  #for proper function logging
import boto3
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)
personal_email = os.environ['email_address']
topic_name = 'aws-iot-button-sns-topic-python'
client_sns = boto3.client('sns')
client_dynamo = boto3.client('dynamodb')
resource_dynamo = boto3.resource('dynamodb')
client_ec2 = boto3.client('ec2')
list_instances = []



def create_sns_topic():
    # This function is idempotent no need to manually check if topic already exits 
    response = client_sns.create_topic(Name=topic_name)
    return response

# This funtion is called to create_sns_subscription check
# if the subscription is on Pending confirmaion or accepted
def find_existing_subscription(topic_arn_iot):
    response = client_sns.list_subscriptions_by_topic(
        TopicArn= topic_arn_iot
    )
    return response

# Create SNS topic to email specified on the envrron
def create_sns_subscription(topic_arn_iot):
    state_subscription = find_existing_subscription(topic_arn_iot) # Function to check if subscriptopn exists
    
    # If handles if subscription already exits or not
    if not state_subscription['Subscriptions']:
        response = client_sns.subscribe(
            TopicArn= topic_arn_iot,
            Protocol= 'email',
            Endpoint = personal_email
            )
        return response

    else:
        result_subscription = state_subscription['Subscriptions'][0]['SubscriptionArn']
        try:
            if result_subscription == 'PendingConfirmation':
                response= client_sns.subscribe(
                    TopicArn=topic_arn_iot,
                    Protocol='email',
                    Endpoint=personal_email
                )
                return response
            else:
                return response
        except Exception as err:
            logger.error('Program could not set proper subscription {}'.format(err))

#Send email with informatio about the IoT button
def email_subscription(topic_arn_iot, event, item_table_count, delete_instances):
    item_table_count = 2000 - item_table_count
    try:
        client_sns.publish(
            TopicArn=topic_arn_iot,
            Message="""{} -- processed by Python 3.6 Lambda
                    Battery voltage: {}
                    There are {} clicks left.
                    The following instances were deleted {}""".format(event['serialNumber'], event['batteryVoltage'], item_table_count, delete_instances),
            Subject="Hello from your IoT Button {}: {}".format(event['serialNumber'], event['clickType'])
        )
        logger.info('Message sent')
    except Exception as err:
        logger.error('Could not send email please topic {}'.format(err))

#Creates dynamo table
def create_dynamo_table(event):
    iot_button_count = event['serialNumber']
    #Checks if table exist if not creates table
    response_query = client_dynamo.list_tables()
    if iot_button_count not in response_query['TableNames']:
        response = client_dynamo.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'count',
                    'AttributeType': 'S'

                }
            ],
            TableName=iot_button_count,
            KeySchema=[
                {
                    'AttributeName': 'count',
                    'KeyType': 'HASH'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        logger.info("table created {}".format(response))

    else:
        logger.info("table is already created {}".format(iot_button_count))

def create_item_dynamo(event):
    iot_button_count = event['serialNumber']
    unix_time = str(time.time())
    client_dynamo.put_item(
        TableName= iot_button_count,
        Item= {
            'count': {
                'S': unix_time
            }
        }
    )
    response = resource_dynamo.Table(iot_button_count)
    return response.scan()['ScannedCount']

def delete_ec2_intances():
    response_ec2 = client_ec2.describe_instances()
    for reservation in response_ec2["Reservations"]:
        for instance in reservation['Instances']:
            list_instances.append(instance['InstanceId'])
    
    logger.info('intances to be deleted {}'.format(list_instances))
    response = client_ec2.terminate_instances(
        InstanceIds=list_instances
    )
    return list_instances

# Min point of entry to the function
def lambda_handler(event, context):
    logger.info('Starting Function')
    logger.info('The following payload was received')

    # print infomation about the payload being passed
    print('serial number {}'.format(event['serialNumber']))
    print('batteryVoltage {}'.format(event['batteryVoltage']))
    print('clickType {}'.format(event['clickType']))
    print('email to be used {}'.format(personal_email))
    
    #Calls function to create topic
    topic_arn_iot = create_sns_topic()
    logger.info('Topic ARN is {}'.format(topic_arn_iot['TopicArn']))

    #Calls function to create subscription
    subscription = create_sns_subscription(topic_arn_iot['TopicArn'])
        
    #Calls function to create dynamo_table
    create_dynamo_table(event)

    #Add events to dynamo table to keep track of click
    item_table_count = create_item_dynamo(event)

    #Delete any EC2 instances
    delete_instances = delete_ec2_intances()

    #Calls function to email data
    email_subscription(topic_arn_iot['TopicArn'], event, item_table_count, delete_instances)
