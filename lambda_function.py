import json
import openai
import logging
import os

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Set up OpenAI API credentials
openai_api_key = os.environ['openai']

def lambda_handler(event, context):
    logging.info("In handler method")
    text = event['text']
    logging.info(f"Text: {text}")
    logging.info("Calling generate_about_section")
    about_text = generate_about_section(text)
    logging.info(f"Response: {about_text}")
    return {
        'statusCode': 200,
        'body': json.dumps('about_text')
    }

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