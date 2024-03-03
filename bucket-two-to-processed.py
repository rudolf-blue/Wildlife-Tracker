#lambda function to find animals and extract metadata from json response, and append to .txt file
import json
import boto3

def lambda_handler(event, context):
    
    s3_client = boto3.client('s3')
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    response = s3_client.get_object(Bucket=bucket, Key=key)
    json_data = json.loads(response['Body'].read().decode('utf-8'))

    strings_to_check = ["Animal", "Squirrel", "Bird", "Skunk", "Lizard", "Cat"]

    temp_string = ""

    for check_string in strings_to_check:
        if any(label['Name'] == check_string for label in json_data['labels']):
            temp_string = f"{check_string}\t"

    if len(temp_string) > 0:
        lat = json_data['metadata']['lat']
        lon = json_data['metadata']['lon']

        data_to_append = f"{temp_string}{lat}\t{lon}\n"

        processed_bucket = "processing-processed"
        text_file_key = "wildLocations.txt"

        try:
            existing_data = s3_client.get_object(Bucket=processed_bucket, Key=text_file_key)['Body'].read().decode('utf-8')
            data_to_append = existing_data + data_to_append
        except s3_client.exceptions.NoSuchKey:
            pass

        s3_client.put_object(Bucket=processed_bucket, Key=text_file_key, Body=data_to_append.encode('utf-8'))

        return {
            'statusCode': 200,
            'body': json.dumps('Data processed successfully!')
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps('No matching strings found. Exiting.')
        }
