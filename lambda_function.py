import json
import openai
import logging
import os
import boto3

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Set up OpenAI API credentials
openai_api_key = os.environ['openai']

lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    logging.info("In handler method")
    #  Get the text from the incoming event
    logger.info("Populating user data variables")
    
    body = event['body']
    
    logger.info(f"Calling get_user_data function with body: {body}")
    response = get_user_data(body)
    logger.info(f"Response from aggregator function: {response}")
    
    text = "dummy-text"
    
    logging.info(f"Text: {text}")
    logging.info("Calling generate_about_section")
    about_text = generate_about_section(text)
    logging.info(f"Response from get_user_data method:\n {about_text}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('about_text')
    }

def get_user_data(body):
    logger.info("In get_user_data function")
    # invoke data aggregator function with message: /sendcv
    logger.info("Changing body message to sendcv")
    
    body['message'] = "/sendcv"
    
    logger.info(f"Body is now: {body}")
    function_name = 'dev-DataAggregatorFunction'
    
    logger.info(f"Sending invoke command to {function_name}")
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',
        LogType='None',
        Payload=json.dumps(body, separators=(',', ':'))
    )
    response_payload = json.loads(response['Payload'].read().decode("utf-8"))
    logger.info(f"Response payload from aggregator function: \n{response_payload}")
    return response_payload

def generate_about_section(text):
    logging.info("In generate_about_section")
    # set openai api key
    openai.api_key = openai_api_key
    
    prompt = f"Given the information about a user below, please generate a short (100 words maximum) 'about' section for a CV cover letter: {text}"
    response = openai.Completion.create(
        engine="text-davinci-003", 
        prompt=prompt,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.6,
    )
    about = response.choices[0].text.strip()
    logging.info(f"About section:\n {about}")

    return about
