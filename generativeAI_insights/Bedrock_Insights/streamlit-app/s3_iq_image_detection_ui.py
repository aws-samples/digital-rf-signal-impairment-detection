import streamlit as st
import boto3
from PIL import Image
import io
import logging
import os
import uuid

# Troubleshooting Tip: If you encounter a GetObject error, update the S3 bucket name
# on line 114 to match your actual bucket (e.g., "satcom-iq-constellation-demo")

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Get config from environment variables
agent_id = os.environ.get("BEDROCK_AGENT_ID")
agent_alias_id = os.environ.get("BEDROCK_AGENT_ALIAS_ID", "TSTALIASID")  # TSTALIASID is the default test alias ID
ui_title = os.environ.get("BEDROCK_AGENT_TEST_UI_TITLE", "Agents for Amazon Bedrock Test UI")


def init_session_state():
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []


# allow the user to select an IQ image from an S3 bucket
# display the image and then pass the image to a multimodal LLM
# to interpret the contents of the image
def interpret_IQ_image(bucket, prefix=""):

    # Configure S3 client
    s3 = boto3.client('s3')

    st.title("S3 IQ Image Viewer and Noise Detector")
    
    # Info banner for bucket configuration
    st.info("💡 Update the S3 bucket name to match your bucket")

    # Input fields
    bucket_name = st.text_input("S3 Bucket Name", value=bucket)

    # S3 File Explorer
    if bucket_name:
        try:
            # List objects in bucket with optional prefix
            list_params = {'Bucket': bucket_name}
            if prefix:
                list_params['Prefix'] = prefix
            response = s3.list_objects_v2(**list_params)

            if 'Contents' in response:
                # Filter for image files
                image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')
                image_objects = [obj for obj in response['Contents']
                                if obj['Key'].lower().endswith(image_extensions)]
                
                # Sort by LastModified timestamp (newest first) and get latest 15
                image_objects.sort(key=lambda x: x['LastModified'], reverse=True)
                image_files = [obj['Key'] for obj in image_objects[:15]]

                if image_files:
                    selected_file = st.selectbox("Select an image file:", image_files)

                    if st.button("Load Selected Image"):
                        # Download and display selected image
                        response = s3.get_object(Bucket=bucket_name, Key=selected_file)
                        image_data = response['Body'].read()
                        image = Image.open(io.BytesIO(image_data))
                        st.image(image, caption=f"Image from s3://{bucket_name}/{selected_file}", width=200)
                        
                        # Invoke Bedrock agent
                        if agent_id:
                            bedrock_runtime = boto3.client('bedrock-agent-runtime')
                            try:
                                agent_response = bedrock_runtime.invoke_agent(
                                    agentId=agent_id,
                                    agentAliasId=agent_alias_id,
                                    sessionId=st.session_state.session_id,
                                    inputText=f"Analyze image from bucket: {bucket_name}, file: {selected_file}"
                                )
                                
                                # Display agent response
                                st.subheader("Agent Analysis...")
                                for event in agent_response['completion']:
                                    if 'chunk' in event:
                                        chunk = event['chunk']
                                        if 'bytes' in chunk:
                                            st.write(chunk['bytes'].decode('utf-8'))
                            except Exception as e:
                                st.error(f"Error invoking agent: {str(e)}")
                        else:
                            st.warning("BEDROCK_AGENT_ID not configured")
                else:
                    st.warning("No image files found in this bucket.")
            else:
                st.warning("No objects found in this bucket.")

        except Exception as e:
            st.error(f"Error accessing bucket: {str(e)}")



# allow local Python execution testing
if __name__ == '__main__':

    # General page configuration and initialization
    st.set_page_config(page_title=ui_title, layout="wide")
    st.title(ui_title)

    if len(st.session_state.items()) == 0:
        init_session_state()

    # Sidebar button to reset session state
    with st.sidebar:
        if st.button("Reset Session"):
            init_session_state()

    interpret_IQ_image("satcom-iq-constellation-demo-4231", "iq-constellation-plots-qpsk/")