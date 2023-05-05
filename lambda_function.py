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
    
    return {
        "statusCode": 200,
        "body": {
            "messageId": event['body']['messageId'],
            "chatId": event['body']['chatId'],
            "userId": event['body']['userId'],
            "message": response,
            "replyId": event['body']['replyId'],
            "isCommand": event['body']['isCommand'],
            "type": event['body']['type'],
            "state": event['body']['state']
  }

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
    
    payload_body = json.loads(response_payload['body'])
    
    logger.info("pulling user data from response payload")
    user = payload_body['user']
    logger.info(f"User: \n{user}")
    
    name = user['userName']
    
    # language
    language = payload_body['lang'][0]
    
    # school
    education = payload_body['edu'][0]
    school = education['schoolName']
    graduation_year = education['graduationYear']
    achievements = education['achievementList']
    
    # experience
    experience = payload_body['exp'][0]
    last_company = experience['companyName']
    role =  experience['role']
    start_date = experience['dateStart']
    end_date = experience['dateEnd']
    
    # skills
    skills = payload_body['skill']
    
    list_skills = ''
    for skill in skills:
        list_skills += skill["skillName"] + ", "
        
    # Remove the last comma and space
    list_skills = list_skills[:-2]
    
    logging.info("Calling generate_about_section")
    about_section = generate_about_section(name, language, school, graduation_year, achievements, last_company, role, start_date, end_date, list_skills)
    
    return about_section

def generate_about_section(name, language, school, graduation_year, achievements, last_company, role, start_date, end_date, list_skills):
    logging.info("In generate_about_section")
    # set openai api key
    openai.api_key = openai_api_key
    
    prompt = f"Given the information about a user below, please generate a short (300 words maximum) 'about' section for a CV cover letter. Name: {name}, language: {language}, school: {school}, graduation year: {graduation_year}, achievements in school: {achievements}, last company worked for: {last_company}, role in that company: {role}, start date in the role: {start_date}, end date in the role: {end_date} and a list of my skills: {list_skills}"
    response = openai.Completion.create(
        engine="text-davinci-003", 
        prompt=prompt,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.65,
    )
    about = response.choices[0].text.strip()
    logging.info(f"About section:\n {about}")

    return about
