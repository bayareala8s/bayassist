import boto3
import json

bedrock = boto3.client("bedrock-runtime")

# TODO: update this to the exact Claude 3.5 Sonnet model ID enabled in your account
# Example (check your console for the exact suffix):
# MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"


def invoke_claude(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    """
    Call Anthropic Claude via Amazon Bedrock using the correct Anthropic JSON schema.

    Bedrock Anthropic format requires:
      - anthropic_version
      - messages: list with role in {"user","assistant"}
      - system: string or list of strings
    """

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4000,
        "temperature": temperature,
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt,
                    }
                ],
            }
        ],
    }

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json",
    )

    payload = json.loads(response["body"].read())
    # Anthropic responses from Bedrock look like:
    # { "content": [ { "type": "text", "text": "..." } ], ... }
    return payload["content"][0]["text"]
