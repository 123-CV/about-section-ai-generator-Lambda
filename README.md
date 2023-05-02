# Lambda Function README

This Lambda function takes in a text input and uses the OpenAI API to generate a short "about" section for a CV cover letter. 

## Usage

The Lambda function can be triggered via an AWS API Gateway endpoint or through other AWS services that support Lambda function invocations.

When triggered, the function expects an input event in the following format:

{
"text": "input text"
}


The `text` field should contain the information about a user that will be used as input for the OpenAI API.

The function returns a JSON response with a 200 status code and a body containing the generated "about" section in string format. 

## Dependencies

This Lambda function requires the following dependencies:

- Python 3.9
- The `openai` package
- An OpenAI API key

## Environment Variables

This Lambda function requires the following environment variable to be set:

- `openai`: Your OpenAI API key

## Function Logic

Upon receiving an input event, the function first sets up logging and retrieves the `text` input. It then calls the `generate_about_section` function, which uses the OpenAI API to generate a short "about" section based on the input text. 

The generated "about" section is returned to the calling function as a string in the JSON response body.
