import json
import boto3

translate_client = boto3.client('translate')

def lambda_handler(event, context):
    """Lambda function for Bedrock agent OpenAPI action group"""

    # Check if this is a Bedrock Agent request
    is_bedrock_agent = 'messageVersion' in event and 'actionGroup' in event
    print(f"Is Bedrock Agent: {is_bedrock_agent}")

    if not is_bedrock_agent:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid request format. Expected Bedrock Agent event.'})
        }

    # Extract properties from Bedrock agent event
    properties = event['requestBody']['content']['application/json']['properties']
    
    print(properties)
    
    # Convert properties array to dict
    param_dict = {prop['name']: prop['value'] for prop in properties}
    
    target_language = param_dict.get('target_language')
    source_text = param_dict.get('source_text')
    
    print(f"Target language: {target_language}")
    
    if not target_language or not source_text:
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event.get('actionGroup', 'TranslateActionGroup'),
                'apiPath': event.get('apiPath', '/translate'),
                'httpMethod': event.get('httpMethod', 'POST'),
                'httpStatusCode': 400,
                'responseBody': {
                    'application/json': {
                        'body': json.dumps({'error': 'Missing required parameters: target_language, source_text'})
                    }
                }
            }
        }
    
    # Translate text
    response = translate_client.translate_text(
        Text=source_text,
        SourceLanguageCode='auto',
        TargetLanguageCode=target_language
    )
    
    return {
        'messageVersion': '1.0',
        'response': {
            'actionGroup': event.get('actionGroup', 'TranslateActionGroup'),
            'apiPath': event.get('apiPath', '/translate'),
            'httpMethod': event.get('httpMethod', 'POST'),
            'httpStatusCode': 200,
            'responseBody': {
                'application/json': {
                    'body': json.dumps({
                        'translated_text': response['TranslatedText']
                    })
                }
            }
        }
    }

def main():
    """Test function"""
    test_event = {
        'messageVersion': '1.0',
        'actionGroup': 'TranslateActionGroup',
        'apiPath': '/translate',
        'httpMethod': 'POST',
        'requestBody': {
            'content': {
                'application/json': {
                    'properties': [
                        {
                            'name': 'target_language',
                            'type': 'string',
                            'value': 'fr'
                        },
                        {
                            'name': 'source_text',
                            'type': 'string',
                            'value': 'Hello, how are you today?'
                        }
                    ]
                }
            }
        }
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
