import json
import logging
import os
import boto3
import openai

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Set up OpenAI API credentials
openai_api_key = os.environ.get('openai')

lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    logging.info("In handler method")
    try:
        # Get the text from the incoming event
        body = event.get('body', {})
        if not body:
            raise ValueError('No body provided in the event')
        
        # Check if required fields are present in the body
        required_fields = ['messageId', 'chatId', 'userId', 'replyId', 'isCommand', 'type', 'state']
        missing_fields = [field for field in required_fields if field not in body]
        if missing_fields:
            raise ValueError(f'Missing required fields in body: {missing_fields}')
        
        logger.info("Calling get_user_data function")
        response = get_user_data(body)
        logger.info(f"Response from aggregator function: {response}")
        
        return {
            "statusCode": 200,
            "body": {
                "messageId": body.get('messageId'),
                "chatId": body.get('chatId'),
                "userId": body.get('userId'),
                "message": response,
                "replyId": body.get('replyId'),
                "isCommand": body.get('isCommand'),
                "type": body.get('type'),
                "state": body.get('state')
            }
        }
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return {
            "statusCode": 500,
            "body": {"error": str(e)}
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
    
    payload_body = json.loads(response_payload.get('body', {}))
    
    # Check if required fields are present in the response
    required_fields = ['user', 'lang', 'edu', 'exp', 'skill']
    missing_fields = [field for field in required_fields if field not in payload_body]
    if missing_fields:
        raise ValueError(f'Missing required fields in aggregator function response: {missing_fields}')
    
    logger.info("pulling user data from response payload")
    user = payload_body['user']
    logger.info(f"User: \n{user}")
    
    name = user.get('userName')
    
    # language
    language = payload_body['lang'][0] if payload_body['lang'] else ''
    
    # school
    education = payload_body['edu'][0] if payload_body['edu'] else {}
    school = education.get('schoolName')
    graduation_year = education.get('graduationYear')
    achievements = education.get('achievementList', [])
    
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
