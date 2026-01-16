# IQ Constellation Analysis with Amazon Bedrock

This project uses Amazon Bedrock Agents with multimodal LLMs to analyze IQ constellation diagrams and identify RF signal impairments like phase noise and interference.

## Architecture Overview

The solution consists of:

- **Amazon Bedrock Agent**: Orchestrates the analysis workflow
- **AWS Lambda (Image Analysis)**: Performs image analysis using Claude Sonnet 4.5 with few-shot prompting
- **AWS Lambda (Translation) (optional)**: Translates analysis results to target languages using Amazon Translate
- **Amazon Bedrock Knowledge Base**: Provides reference documentation for RF impairment analysis
- **Amazon S3**: Stores constellation images, few-shot examples, and knowledge base documents
- **Streamlit UI**: Interactive web interface for image selection, analysis, and multilingual output

## Prerequisites

- AWS Account with access to Amazon Bedrock
- AWS CLI configured with appropriate credentials
- Python 3.9+ (for Streamlit app)
- Access to Claude Sonnet 4.5 model in your AWS region

**Note**: Some of the assets may not be available in all regions. This stack was tested in **us-east-1** and **us-west-2**.

## Translation Support (Optional)

This solution includes optional multilingual support that allows analysis results to be translated into multiple languages using Amazon Translate. When enabled:

- A dedicated **Translation Lambda function** is deployed alongside the image analysis Lambda
- The Bedrock Agent gains a **Translation Action Group** that can translate responses on demand
- The **Streamlit UI** includes a language selector dropdown for instant translation
- Supports 75+ languages including Spanish, French, German, Japanese, Chinese, and more

Translation is **disabled by default** to minimize costs. Enable it during deployment by setting the `EnableTranslation` parameter to `yes`
in the `bedrock-constellation-analysis-translate.yaml` file.

## Deployment Steps

### Step 1: Prepare S3 Bucket and Lambda Code

**Important**: Complete this step before deploying the CloudFormation stack.

1. **Set bucket name** (reference your existing DIFI Processor Results bucket):

```bash
DIFI_RESULTS_BUCKET=your-difi-processor-results-bucket-name
```

2. **Create Lambda deployment packages**:

```bash
# Zip the image analysis Lambda function
zip iq-constellation-inference-demo-fxn.zip lambda_function.py

# Zip the translation Lambda function (if using translation feature)
zip bedrock_translate_lambda.zip bedrock_translate_lambda.py
```

3. **Upload Lambda code to S3**:

```bash
# Upload image analysis Lambda
aws s3 cp iq-constellation-inference-demo-fxn.zip s3://${DIFI_RESULTS_BUCKET}/lambda/iq-constellation-inference-demo-fxn.zip

# Upload translation Lambda (if using translation feature)
aws s3 cp bedrock_translate_lambda.zip s3://${DIFI_RESULTS_BUCKET}/lambda/bedrock_translate_lambda.zip
```

4. **Upload few-shot training examples**:

```bash
aws s3 cp iq-constellation-fewshot-data/ s3://${DIFI_RESULTS_BUCKET}/iq-constellation-fewshot-data/ --recursive
```

5. **Upload knowledge base documents**:

```bash
aws s3 cp iq-constellation-kb-data/ s3://${DIFI_RESULTS_BUCKET}/iq-constellation-kb-data/ --recursive
```

6. **Upload test constellation images**:

```bash
aws s3 cp iq-constellation-plots-qpsk/ s3://${DIFI_RESULTS_BUCKET}/iq-constellation-plots-qpsk/ --recursive
aws s3 cp iq-constellation-plots-8psk/ s3://${DIFI_RESULTS_BUCKET}/iq-constellation-plots-8psk/ --recursive
```

7. **Verify uploads**:

```bash
aws s3 ls s3://${DIFI_RESULTS_BUCKET}/ --recursive
```

### Step 2: Deploy CloudFormation Stack

**Why?** CloudFormation automates the creation of IAM roles, Lambda functions, Bedrock Agent, and their interconnections as infrastructure-as-code. This ensures consistent, repeatable deployments and eliminates manual configuration errors that could occur when creating these resources individually through the console.

**Template Options:**
- `bedrock-constellation-analysis.yaml` - Base template without translation support
- `bedrock-constellation-analysis-translate.yaml` - Template with optional translation support

1. Deploy the CloudFormation template:

**Without Translation (default):**
```bash
aws cloudformation create-stack \
  --stack-name iq-constellation-analysis \
  --template-body file://bedrock-constellation-analysis.yaml \
  --parameters ParameterKey=S3BucketName,ParameterValue=${DIFI_RESULTS_BUCKET} \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

**With Language Translation Enabled:**
```bash
aws cloudformation create-stack \
  --stack-name iq-constellation-analysis \
  --template-body file://bedrock-constellation-analysis-translate.yaml \
  --parameters \
    ParameterKey=S3BucketName,ParameterValue=${DIFI_RESULTS_BUCKET} \
    ParameterKey=EnableTranslation,ParameterValue=yes \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

2. Get the stack outputs:

```bash
aws cloudformation describe-stacks \
  --stack-name iq-constellation-analysis \
  --query 'Stacks[0].Outputs' \
  --region us-east-1
```

Note the following output values:

- `AgentId`
- `AgentAliasId`
- `S3BucketName`
- `LambdaFunctionArn`

### Step 3: Create Knowledge Base

**Why?** Bedrock Knowledge Bases require a vector database to store document embeddings for semantic search. Amazon OpenSearch Serverless provides this vector store, but its collections and indices cannot be dynamically created through CloudFormation. The Knowledge Base creation process requires manual configuration of the vector store, embedding model selection, and data source synchronization, which must be done through the console or API.

The Knowledge Base must be created manually as it requires specific configuration:

1. **Navigate to Amazon Bedrock Console**

   - Go to **Knowledge bases** in the left navigation
   - Click **Create knowledge base with vector store**

2. **Knowledge Base Details**

   - Name: `iq-constellation-kb`
   - Description: `Knowledge base for IQ constellation diagram analysis and RF impairment identification`
   - IAM Role: Create a new service role (or use existing)
   - Click **Next**

3. **Configure Data Source and Parsing/Chunking Strategy**

   - Data source name: `iq-constellation-docs`
   - S3 URI: `s3://${DIFI_RESULTS_BUCKET}/iq-constellation-kb-data/`
   - Select **Bedrock Data Automation (BDA) as parser**
     - BDA as a parser is ideal for documents rich in images and tables
   - Select **Default chunking**
   - Click **Next**

4. **Create Embeddings**

   - Select Embedding model: `Titan Text Embeddings V2` (or your preferred model)
   - Select **Quick create new vector store**
   - Select **Amazon OpenSearch Serverless** as vector store
   - Click **Next**

5. **Review and Create**

   - Review settings
   - Click **Create knowledge base**

6. **Sync Data Source**

   - After creation, click **Sync** to ingest the documents
     - **Note:** Every time you upload new documents to your data source, you will have to re-sync
   - Wait for sync to complete (this may take several minutes)

7. **Note the Knowledge Base ID**
   - You'll need this for the next step
   - Format: `XXXXXXXXXX` (10 characters)

### Step 4: Add Knowledge Base to Agent

1. **Navigate to Bedrock Agents**

   - Go to **Agents** in Amazon Bedrock Console
   - Find your agent (name starts with `iq-constellation-`)

2. **Edit Agent**

   - Click on the agent name
   - Scroll to **Knowledge bases** section
   - Click **Add** or **Associate knowledge base**

3. **Configure Knowledge Base Association**

   - Select your knowledge base: `iq-constellation-kb`
   - Instructions for knowledge base:
     ```
     Use this knowledge base as the primary source of reference for answers in determining which type of impairment is present.
     ```
   - Click **Add**

4. **Prepare Agent**
   - After adding the knowledge base, click **Save and exit** at the top
   - Click **Prepare** on the chat window to the right
   - Wait for preparation to complete

### Step 5: Add Bedrock Access Policy to Agent Role

The agent needs permission to access the Knowledge Base. Add an inline policy:

1. **Find the Agent Role**

   - In the CloudFormation outputs or Bedrock Agent console, note the agent role name
   - Format: `bedrock-agent-<stack-name>`

2. **Add Inline Policy via IAM Console**

   - Go to IAM Console → Roles
   - Search for `bedrock-agent-<stack-name>`
   - Click on the role
   - Go to **Permissions** tab
   - Click **Add permissions** → **Create inline policy**

3. **Policy JSON**

   - Switch to JSON editor and paste:

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "BedrockKnowledgeBaseAccess",
         "Effect": "Allow",
         "Action": ["bedrock:Retrieve", "bedrock:RetrieveAndGenerate"],
         "Resource": "arn:aws:bedrock:us-east-1:YOUR_ACCOUNT_ID:knowledge-base/YOUR_KB_ID"
       }
     ]
   }
   ```

   - Replace `YOUR_ACCOUNT_ID` and `YOUR_KB_ID` with your values

4. **Name and Create**
   - Policy name: `Bedrock-KB-Access-Policy`
   - Click **Create policy**

Alternatively, add via CLI:

```bash
# Set your values
AGENT_ROLE_NAME="bedrock-agent-iq-constellation-analysis"
KB_ID="YOUR_KB_ID"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="us-east-1"

# Create policy document
cat > kb-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BedrockKnowledgeBaseAccess",
      "Effect": "Allow",
      "Action": [
        "bedrock:Retrieve",
        "bedrock:RetrieveAndGenerate"
      ],
      "Resource": "arn:aws:bedrock:${REGION}:${ACCOUNT_ID}:knowledge-base/${KB_ID}"
    }
  ]
}
EOF

# Add inline policy
aws iam put-role-policy \
  --role-name ${AGENT_ROLE_NAME} \
  --policy-name Bedrock-Access-Policy \
  --policy-document file://kb-policy.json
```

### Step 6: Test the Agent

Test the agent in the Bedrock Console:

1. Go to your agent in the Bedrock Console
2. Click **Test** in the top right
3. Try a test query:

   ```
   Analyze the image at bucket: ${DIFI_RESULTS_BUCKET}, file: iq-constellation-plots-qpsk/phase_noise-0.jpeg
   ```

4. The agent should:
   - Invoke the Lambda function
   - Analyze the image using Claude Sonnet with few-shot examples
   - Reference the knowledge base for additional context
   - Return a detailed analysis of the RF impairment

### Step 7: Deploy Streamlit UI (Optional)

Run the interactive web interface locally:

1. **Install Dependencies**

```bash
cd streamlit-app
pip install -r requirements.txt
```

2. **Set Environment Variables**

```bash
# Use the values from CloudFormation outputs
export BEDROCK_AGENT_ID="YOUR_AGENT_ID"
export BEDROCK_AGENT_ALIAS_ID="YOUR_ALIAS_ID"
export BEDROCK_AGENT_TEST_UI_TITLE="IQ Constellation Analysis"
```

Or source the environment file:

```bash
# Edit environment_variables.sh with your values
source environment_variables.sh
```

3. **Update S3 Bucket Name and Prefix**

Edit `s3_iq_image_detection_ui.py` or `s3_iq_image_detection_ui_translate.py` and update the line near the end of the script with your bucket name and S3 prefix for test images:

```python
interpret_IQ_image("<YOUR-BUCKET-NAME>", "results/test-file/")
```

- Replace the first parameter with your actual bucket name (e.g., `pcap-test-results`)
- The second parameter is the S3 prefix/folder containing your test images (e.g., `iq-constellation-plots-qpsk/` or `iq-constellation-plots-8psk/`)

4. **Run Streamlit**

```bash
streamlit run s3_iq_image_detection_ui.py
```

or, with language translation
```bash
streamlit run s3_iq_image_detection_ui_translate.py
```

5. **Use the UI**
   - Open browser to `http://localhost:8501`
   - Select images from the S3 bucket
   - Click "Load Selected Image" to analyze
   - View the agent's analysis results
   - **Optional**: Select a target language from the dropdown to translate results

## How It Works

### 🧠 Few-Shot Learning

Few-shot prompting is a technique where the model is provided with a small number of example inputs and outputs to guide its behavior on new, similar tasks. The Lambda function demonstrates this by showing the LLM two annotated example images before asking it to analyze a new constellation diagram. This helps the model understand the expected analysis format and the characteristics that distinguish different types of RF impairments.

The Lambda function uses two example images as a guide:

- **Interference example**: Shows random scattering pattern
- **Phase noise example**: Shows rotational smearing pattern

**For more information**: [Few-Shot Prompting Guide](https://www.promptingguide.ai/techniques/fewshot)

### 📚 Knowledge Base (RAG)

The knowledge base uses Retrieval Augmented Generation (RAG) to enhance the agent's responses with domain-specific technical documentation. Documents are converted into vector embeddings and stored in Amazon OpenSearch Serverless. When the agent needs information, it retrieves relevant passages from these documents to ground its responses in factual, technical content rather than relying solely on the model's training data.

The knowledge base contains technical documentation about:

- IQ constellation diagrams
- RF impairments and their characteristics
- Phase noise vs interference identification
- Troubleshooting guidance

**For more information**: [What is RAG?](https://aws.amazon.com/what-is/retrieval-augmented-generation/)

### 🤖 Agent Orchestration

The Bedrock Agent acts as an intelligent orchestrator that reasons about user requests and coordinates multiple tools to accomplish tasks. It has access to both the Lambda function (for image analysis) and the Knowledge Base (for technical documentation). The agent determines when to invoke each tool, interprets their outputs, and synthesizes a comprehensive response. This agentic workflow allows the system to handle complex, multi-step analysis tasks autonomously.

**For more information**: [What are AI Agents?](https://huggingface.co/learn/agents-course/en/unit1/what-are-agents)

### Analysis Output

The agent provides:

1. Modulation type (QPSK, 8PSK, 16-QAM, etc.)
2. Impairment detection (yes/no)
3. Impairment classification (phase noise or interference)
4. Typical causes
5. Severity assessment (mild/moderate/severe)
6. Recommendation (acceptable/needs attention/critical)

## Troubleshooting

### Lambda Function Errors

- Verify the handler is set to `lambda_function.lambda_handler`
- Check CloudWatch Logs for the Lambda function
- Ensure the Lambda role has S3 and Bedrock permissions

### Knowledge Base Not Working

- Verify the knowledge base is synced
- Check that the agent role has the `Bedrock-Access-Policy`
- Ensure the knowledge base instruction is added to the agent

### Agent Not Responding

- Verify the agent is "Prepared" after any changes
- Check that the Lambda permission allows Bedrock to invoke it
- Test the Lambda function directly first

### S3 Access Issues

- Verify bucket names match in all configurations
- Check that files are uploaded to correct prefixes
- Ensure IAM roles have S3 GetObject permissions

## Cleanup

To remove all resources:

```bash
# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name iq-constellation-analysis --region us-east-1

# Manually delete Knowledge Base (not in stack)
# Go to Bedrock Console → Knowledge bases → Delete

# Empty and delete S3 bucket if needed (if you want to remove it)
aws s3 rm s3://${DIFI_RESULTS_BUCKET} --recursive
aws s3 rb s3://${DIFI_RESULTS_BUCKET}
```

## License

[License information to be added]
