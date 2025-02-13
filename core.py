import boto3
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)
import json

# Constants
BASE_URL = "https://fragment.dev/docs"
S3_DATA_BUCKET = "fragment-docs-data"
S3_OUTPUT_FOLDER = "scraped_docs"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 0

def fetch_data_from_s3(url: str):
    """
    This method fetches the markdown data for the URL from S3.

    :param str url: The URL of the page
    :return: The markdown data
    :rtype: str
    """
    # Fetch the markdown data from S3
    print(f"Fetching markdown data for {url}")
    s3 = boto3.client('s3')
    try:
        filename = url.replace(f"{BASE_URL}/", "").replace("/", "-") + ".md"
        response = s3.get_object(Bucket=S3_DATA_BUCKET, Key=f"{S3_OUTPUT_FOLDER}/{filename}")
        print(f"Markdown data fetched successfully for {url}")
        print(response)
        return response['Body'].read().decode('utf-8')
    except Exception as e:
        print(f"An error occurred while fetching markdown data: {e}")
        return None

def get_markdown_data(url: str):
    """
    This method first synchronously invokes the ledaa_web_scrapper Lambda function to scrape the URL and store the data in S3.
    Then, it fetches the markdown data for the URL from S3.

    :param str url: The URL of the page
    :return: The markdown data
    :rtype: str
    """
    # Invoke the ledaa_web_scrapper Lambda function
    lambda_client = boto3.client('lambda')
    try:
        lambda_invoke_status_response = lambda_client.invoke(
            FunctionName='ledaa_web_scrapper_lambda',
            InvocationType='RequestResponse',
            Payload='{"url": "' + url + '"}'
        )
        # check invocation status
        if lambda_invoke_status_response['StatusCode'] != 200:
            print(f"Error: Failed to invoke LEDAA Web Scraper Lambda for {url}")
            # Log the error
            print(lambda_invoke_status_response)
            return None
    except Exception as e:
        print(f"An error occurred while invoking LEDAA Web Scraper Lambda: {e}")
        return None
    print(f"LEDAA Web Scraper Lambda invocation completed for {url}")
    # Fetch the markdown data from S3
    return fetch_data_from_s3(url=url)
    
def preprocess_data(url: str, markdown_data: str) -> list[str]:
    """
    This method preprocesses the markdown data by splitting the markdown text into document chunks.
    Also, adds the URL as metadata to each document chunk.

    :param str markdown_data: The markdown data
    :return: The document chunks
    :rtype: list
    """
    print(f"Preprocessing data")
    # Initialize the text splitter
    text_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.MARKDOWN, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    # Load the document
    docs = text_splitter.create_documents([markdown_data], metadatas=[{"url": url}])
    # Extract the document chunks
    return [doc.page_content for doc in docs]
    
def main(url: str):
    # Validate URL
    if not url:
        return {
            'statusCode': 400,
            'body': 'URL is required'
        }
    # Get markdown data for the URL from S3
    markdown_data = get_markdown_data(url=url)
    if not markdown_data:
        return {
            'statusCode': 500,
            'body': 'Failed to fetch markdown data'
        }
    print(f"Markdown data fetched successfully for {url}")
    # Pre-process data: text splitting and document chunking
    data_chunks = preprocess_data(url=url, markdown_data=markdown_data)
    if not data_chunks:
        return {
            'statusCode': 500,
            'body': 'Failed to preprocess data'
        }
    print(f"Data preprocessed successfully for {url}")
    # Return data chunks as json
    return {    
        'statusCode': 200,
        'body': json.dumps(data_chunks)
    }

# Lambda handler method (will be invoked by AWS Lambda)
def lambda_handler(event, context):
    print("LEDAA Load Data Lambda invoked")
    # Validate URL 
    if "url" not in event:
        return {
            'statusCode': 400,
            'body': 'URL is required'
        }
    # Invoke the main method
    return main(url=event["url"])
