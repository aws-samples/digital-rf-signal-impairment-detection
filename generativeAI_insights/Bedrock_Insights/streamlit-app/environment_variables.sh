#!/bin/bash

# iq image detection agent
export BEDROCK_AGENT_ID="<YOUR-AGENT-ID>" # Update with your Agent ID
export BEDROCK_AGENT_ALIAS_ID="<YOUR-AGENT-ALIAS-ID>" # Update with your Agent Alias ID


export AWS_DEFAULT_REGION="us-west-2"

# The favicon, such as `:bar_chart:`. The default Streamlit icon will be used if it is not set.
#export BEDROCK_AGENT_TEST_UI_ICON="satcom-ant-img-512.jpg"

# The page title. The default `Agents for Amazon Bedrock Test UI` will used if it is not set.
export BEDROCK_AGENT_TEST_UI_TITLE="Satcom agents Bedrock UI"

# The log level. One of: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.
# The default `INFO` will be used if it is not set.
# For more advanced logging configuration, use `logging.yaml` instead.
# 
# LOG_LEVEL=
