import boto3
import logging

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

#Using the AWS boto3 library, create a client used to access the data stored on the S3 Bucket
s3_client = boto3.client('s3')

# Function to extract file information from an S3 event
def get_file_info(event):
    LOGGER.info('get_file_info: starting')
    # Retrieve the first record from the S3 event payload
    first_record = event['Records'][0]
    # Extract the bucket name where the file is stored
    bucket_name = first_record['s3']['bucket']['name']
    # Extract the key (file name) of the uploaded file
    file_name = first_record['s3']['object']['key']

    LOGGER.info(f'get_file_info: file={file_name}, bucket_name={bucket_name}')
    # Return the bucket name and file key
    return bucket_name, file_name

# Function to load the content of a file from an S3 bucket
def load_file(bucket_name, s3_key):
    LOGGER.info(f'load_file: loading s3_key={s3_key} from bucket_name={bucket_name}')
    # Use the S3 client to retrieve the file object from the specified bucket and key
    response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
    # Read the file's content from the response and decode it into a UTF-8 string
    body_text = response['Body'].read().decode('utf-8')

    LOGGER.info(f'load_file: done: s3_key   ={s3_key} result_chars={len(body_text)}')
    # Return the decoded content of the file
    return body_text
