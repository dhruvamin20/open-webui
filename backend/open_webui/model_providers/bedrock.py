import os
import json
import boto3


class BedrockClient:
    """Simple Bedrock provider for chat and embeddings."""

    def __init__(self, region=None, chat_model=None, embed_model=None):
        self.region = region or os.environ.get("BEDROCK_REGION")
        self.chat_model = chat_model or os.environ.get("BEDROCK_CHAT_MODEL")
        self.embed_model = embed_model or os.environ.get("BEDROCK_EMBED_MODEL")
        self.runtime = boto3.client("bedrock-runtime", region_name=self.region)

    def chat(self, messages: list[dict], **params):
        payload = {
            "messages": messages,
            **params,
        }
        response = self.runtime.invoke_model(
            modelId=self.chat_model,
            body=json.dumps(payload).encode(),
            contentType="application/json",
        )
        return json.loads(response["body"].read())

    def embeddings(self, input_texts: list[str], **params):
        payload = {
            "input": input_texts,
            **params,
        }
        response = self.runtime.invoke_model(
            modelId=self.embed_model,
            body=json.dumps(payload).encode(),
            contentType="application/json",
        )
        return json.loads(response["body"].read())
