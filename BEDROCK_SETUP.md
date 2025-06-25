# AWS Bedrock Integration with Open WebUI

This guide explains how to connect your Open WebUI instance to AWS Bedrock LLM models using the Bedrock Access Gateway.

## Prerequisites

1. **AWS Account with Bedrock Access**
   - Active AWS account
   - AWS Access Key ID and Secret Access Key
   - IAM permissions to use Bedrock models
   - Enabled models in AWS Bedrock (see [AWS Bedrock Model Access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html))

2. **Docker and Docker Compose installed**

## Setup Instructions

### Step 1: Set Up AWS Credentials

Create a `.env.bedrock` file in the project root with your AWS credentials:

```bash
# AWS Credentials for Bedrock Access
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
# Optional: Only needed if using temporary credentials
AWS_SESSION_TOKEN=

# AWS Region where your Bedrock models are available
AWS_REGION=us-east-1

# WebUI Secret Key (generate a random string)
WEBUI_SECRET_KEY=your_random_secret_key_here
```

**Security Note:** Never commit this file to version control. Add `.env.bedrock` to your `.gitignore`.

### Step 2: Enable Bedrock Models

Before using models, ensure they're enabled in your AWS account:

1. Go to AWS Console → Amazon Bedrock
2. Navigate to "Model access" in the left sidebar
3. Request access to the models you want to use (e.g., Claude, Llama, etc.)
4. Wait for approval (usually instant for most models)

### Step 3: Run the Services

```bash
# Load environment variables and start the services
docker-compose --env-file .env.bedrock -f docker-compose.bedrock.yaml up -d
```

### Step 4: Access Open WebUI

1. Open your browser and go to `http://localhost:3000`
2. Create an account (first user becomes admin)
3. The Bedrock models should appear automatically in the model selector

### Step 5: Alternative - Add Bedrock via UI

If you prefer to configure Bedrock through the UI instead of docker-compose:

1. Start only Open WebUI:
   ```bash
   docker run -d -p 3000:8080 --name open-webui open-webui
   ```

2. Start Bedrock Gateway separately:
   ```bash
   docker run -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
     -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
     -e AWS_REGION=us-east-1 \
     -d -p 8000:80 \
     --name bedrock-gateway \
     bedrock-gateway
   ```

3. In Open WebUI:
   - Go to Admin Panel → Settings → Connections
   - Click the "+" button under OpenAI section
   - Enter URL: `http://host.docker.internal:8000/api/v1`
   - Enter API Key: `bedrock`
   - Click "Verify Connection"

## Available Models

Once connected, you'll see AWS Bedrock models like:
- anthropic.claude-3-sonnet-20240229-v1:0
- anthropic.claude-3-haiku-20240307-v1:0
- meta.llama3-8b-instruct-v1:0
- mistral.mistral-7b-instruct-v0:2
- And more based on your enabled models

## Troubleshooting

### "Access Denied" Error
If you see this error in the logs:
```
AccessDeniedException: You don't have access to the model with the specified model ID
```

Solution: Enable the model in AWS Bedrock Model Access page.

### Connection Failed
- Ensure both containers are on the same network
- Check AWS credentials are correct
- Verify the AWS region has Bedrock available

### View Logs
```bash
# View Bedrock Gateway logs
docker logs bedrock-gateway

# View Open WebUI logs
docker logs open-webui
```

## Security Best Practices

1. **Use IAM Roles in Production**: Instead of access keys, use IAM roles when deploying on AWS
2. **Limit Permissions**: Create IAM policies that only allow access to specific Bedrock models
3. **Rotate Credentials**: Regularly rotate your AWS access keys
4. **Use HTTPS**: In production, use a reverse proxy with SSL certificates

## Cost Considerations

AWS Bedrock charges per token processed. Monitor your usage in the AWS Console under Bedrock → Usage & Cost.

## References

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Bedrock Access Gateway](https://github.com/aws-samples/bedrock-access-gateway)
- [Open WebUI Bedrock Tutorial](https://docs.openwebui.com/tutorials/integrations/amazon-bedrock/) 