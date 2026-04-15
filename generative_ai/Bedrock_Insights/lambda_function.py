import json
import os
import boto3
import base64
import argparse


def lambda_handler(event, context):

    # this can be run either as cmd line py program or a Lambda based on the execution environment
    execEnv = str(os.getenv('AWS_EXECUTION_ENV'))
    if execEnv.startswith("AWS_Lambda"):
        model_image_id = os.getenv('model_image_id')
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("-m", "--model_image_id", help="The model_id to use for Image real time inference")
        args = parser.parse_args()
        model_image_id = args.model_image_id

    if model_image_id is None:
        print("Invalid model_image_id")
        return -1
    else:
        print(" Image model id: ", model_image_id)

    # Check if this is a Bedrock Agent request
    is_bedrock_agent = 'messageVersion' in event and 'actionGroup' in event
    
    if is_bedrock_agent:
        # Extract from OpenAPI schema request body properties
        request_body = event['requestBody']['content']['application/json']['properties']

        print(request_body)

        params = {}
        for param in request_body:
            name = param.get('name')
            value = param.get('value')
            params[name] = value

        bucket_name = params['bucket_name']
        image_key = params['image_key']

        print(f"Bucket Name: {bucket_name}, Image Key: {image_key}")

    else:
        # Extract from direct Lambda event
        bucket_name = event['bucket_name']
        image_key = event['image_key']
    
    s3 = boto3.client('s3')
    bedrock = boto3.client('bedrock-runtime')
    
    # Get the target image from S3
    response = s3.get_object(Bucket=bucket_name, Key=image_key)
    image_data = response['Body'].read()

    # Load few-shot example images from S3
    fewshot_prefix = 'iq-constellation-fewshot-data/'
    
    # Get interference example
    interference_response = s3.get_object(
        Bucket=bucket_name, 
        Key=f'{fewshot_prefix}interference-13.jpeg'
    )
    interference_image = interference_response['Body'].read()
    
    # Get phase noise example
    phase_noise_response = s3.get_object(
        Bucket=bucket_name, 
        Key=f'{fewshot_prefix}phase_noise-0.jpeg'
    )
    phase_noise_image = phase_noise_response['Body'].read()

    # System prompt
    system_prompt = (
        "You are an expert RF Analyst specializing in IQ constellation modulation diagrams. "
        "Your task is to analyze constellation diagrams and identify:\n"
        "1. The modulation type (e.g., QPSK, 16-QAM, 64-QAM, etc.)\n"
        "2. Any noise or impairments present\n"
        "3. Classification of noise/imbalance as phase noise or interference\n"
        "4. Typical causes of the identified issues\n\n"
        "5. Imparement severity if present (Mild/moderate/severe)\n"
        "6. Quick recommendation (acceptable/needs attendtion/critical)\n"
        "Do not respond in markup, respond in plain text"
        "I will show you some examples first, then ask you to analyze a new image."
    )

    # Use converse API with few-shot examples
    response = bedrock.converse(
        modelId=model_image_id,
        system=[{'text': system_prompt}],
        messages=[
            # Few-shot Example 1: Interference
            {
                'role': 'user',
                'content': [
                    {
                        'image': {
                            'format': 'jpeg',
                            'source': {'bytes': interference_image}
                        }
                    },
                    {
                        'text': 'Analyze this IQ constellation diagram.'
                    }
                ]
            },
            {
                'role': 'assistant',
                'content': [{
                    'text': (
                        """
                        1. Modulation type: 8PSK (8 constellation points arranged in a circle at 45-degree intervals)

                        2. Noise/impairments present: Yes, severe impairment with significant signal degradation detected

                        3. Type of noise/imbalance: Interference - constellation points show extensive random scattering in all directions from ideal positions. Each symbol cluster exhibits chaotic spreading with points scattered
                        far beyond normal boundaries. The interference appears additive and broadband, affecting all constellation points with similar random dispersion patterns.

                        4. Typical causes:
                            • Co-channel interference from adjacent frequency users
                            • Broadband noise from switching power supplies or digital circuits
                            • Electromagnetic interference from nearby transmitters
                            • Thermal noise floor elevation due to receiver front-end issues
                            • Intermodulation products from nonlinear amplifiers
                            • External RF interference from industrial equipment or unintentional radiators
                            • Inadequate filtering allowing out-of-band signals to corrupt the desired signal

                        5. Impairment severity: Severe - constellation structure heavily degraded with extensive point scattering. Signal integrity compromised with high likelihood of increased bit errors and potential link
                        instability.

                        6. Quick recommendation: Critical - immediate investigation required to identify and eliminate interference source. Check for nearby transmitters, verify filtering, examine power supply noise, and consider
                        frequency coordination. Monitor spectrum around operating frequency to identify specific interference signatures.
                        """
                    )
                }]
            },
            # Few-shot Example 2: Phase Noise
            {
                'role': 'user',
                'content': [
                    {
                        'image': {
                            'format': 'jpeg',
                            'source': {'bytes': phase_noise_image}
                        }
                    },
                    {
                        'text': 'Analyze this IQ constellation diagram.'
                    }
                ]
            },
            {
                'role': 'assistant',
                'content': [{
                    'text': (
            """
                1. Modulation type: 8PSK (8 constellation points arranged in a circle at 45-degree intervals)

                2. Noise/impairments present: Yes, significant phase-related impairment detected affecting all constellation points uniformly

                3. Type of noise/imbalance: Phase noise - constellation points exhibit characteristic rotational smearing with angular spreading around ideal positions. Each symbol shows curved trailing patterns indicating
                time-varying phase jitter. The impairment affects all constellation points equally, confirming oscillator-based rather than channel-based degradation.

                4. Typical causes:
                    • Local oscillator phase jitter and frequency instability
                    • PLL loop bandwidth optimization issues or inadequate filtering
                    • Thermal noise in VCO or reference oscillator circuits
                    • Crystal oscillator aging, temperature coefficients, or mechanical vibration
                    • Phase detector nonlinearity or charge pump ripple
                    • Power supply noise coupling into oscillator circuits

                5. Impairment severity: Moderate - constellation points maintain separation but show noticeable phase uncertainty. BER performance likely degraded from ideal, approaching system design margins.

                6. Quick recommendation: Needs attention - phase noise at this level suggests oscillator subsystem requires calibration or component replacement. Monitor temperature stability and check PLL loop parameters.
                Consider frequency reference upgrade if persistent across multiple units.
                """
                    )
                }]
            },
            # Actual query with the target image
            {
                'role': 'user',
                'content': [
                    {
                        'image': {
                            'format': 'jpeg',
                            'source': {'bytes': image_data}
                        }
                    },
                    {
                        'text': (
                            'Now analyze this IQ constellation diagram. '
                        )
                    }
                ]
            }
        ]
    )
    
    result = response['output']['message']['content'][0]['text']
    
    # Return appropriate response format
    if is_bedrock_agent:
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event['actionGroup'],
                'apiPath': event['apiPath'],
                'httpMethod': event['httpMethod'],
                'httpStatusCode': 200,
                'responseBody': {
                    'application/json': {
                        'body': result
                    }
                }
            }
        }
    else:
        return result


def main():
    # Test direct Lambda path
    lambda_event = {
        'bucket_name': 'iq-constellation-images',
        'image_key': 'compression-0.jpeg'
    }
    print("Lambda result:", lambda_handler(lambda_event, {}))
    print("\n")
    
    # Test Bedrock Agent path
    agent_event = {
        'messageVersion': '1.0',
        'actionGroup': 'test-action-group',
        'apiPath': '/analyze-image',
        'httpMethod': 'POST',
        'requestBody': {
            'content': {
                'application/json': {
                    "properties": [
                        {
                            "name": "bucket_name",
                            "type": "string",
                            "value": "iq-constellation-images"
                        },
                        {
                            "name": "image_key",
                            "type": "string",
                            "value": "compression-0.jpeg"
                        }
                    ]
                }
            }
        }
    }
    print("Agent result:", lambda_handler(agent_event, {}))


if __name__ == "__main__":
    main()
