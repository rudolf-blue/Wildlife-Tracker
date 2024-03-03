#lambda function to pass bucket contents to rekognition on new bucket object trigger
import boto3
import json


def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    rekognition_client = boto3.client('rekognition')

    for record in event['Records']:
        bucket = 'aws-squirrels'
        key = record['s3']['object']['key']

        try:
            response = s3_client.head_object(Bucket=bucket, Key=key)
            metadata = response.get('Metadata', {})
            Lat_Value = metadata.get('x-amz-meta-lat')
            Lon_Value = metadata.get('x-amz-meta-lon')

            if key.lower().endswith(('.jpg', '.jpeg', '.png')):
                response = rekognition_client.detect_labels(
                    Image={
                        'S3Object': {
                            'Bucket': bucket,
                            'Name': key
                        }
                    }
                )

                labels = response['Labels']

                data_to_save = {
                    'filename': key,
                    'labels': labels,
                    'metadata': metadata
                }

                json_data = json.dumps(data_to_save)
                s3_client.put_object(
                    Body=json_data.encode('utf-8'),
                    Bucket='processing-squirrel-results',
                    Key=key + '.json'
                )

            else:
                print(f"{key}))

        except Exception as e:
            print(f"{key}")

    return {
        'statusCode': 200,
        'body': json.dumps('Processing complete!')
    }
