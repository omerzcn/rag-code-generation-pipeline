from config import (
    OLLAMA_MODEL, OLLAMA_HOST, OPENROUTER_URL, OPENROUTER_API_KEY, OPENROUTER_MODEL, 
    AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_DEPLOYMENT,
    LLM_PROVIDER
)
import ollama
import requests
from openai import OpenAI

def generate_local(prompt):
    client = ollama.Client(host=OLLAMA_HOST)
    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ]
    )

    return response["message"]["content"]

def generate_api(prompt):
    try:
        response = requests.post(
            url=OPENROUTER_URL,
            headers={
                "Authorization": ("Bearer " + OPENROUTER_API_KEY),
                "Content-Type": "application/json",
            },
            json={
                "model": OPENROUTER_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "max_tokens": 3000,
            },
            timeout=(10, 90),
        )
        response.raise_for_status()
        data = response.json()

        choices = data.get("choices")
        if not choices:
            raise ValueError("No choices returned by OpenRouter")
        
        message = choices[0].get("message")
        if not message:
            raise ValueError("No message returned by OpenRouter")

        content = message.get("content")
        if not content:
            raise ValueError("Empty content returned by OpenRouter")

        return content
    
    except requests.exceptions.RequestException as err:
        raise RuntimeError("OpenRouter request failed: " + str(err)) from err

def generate_azure(prompt):
    client = OpenAI(
        base_url=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_KEY
    )

    response = client.responses.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        input=prompt,
    )

    return response.output_text

def generate(prompt):
    if LLM_PROVIDER == "local":
        return generate_local(prompt)
    elif LLM_PROVIDER == "openrouter":
        return generate_api(prompt)
    elif LLM_PROVIDER == "azure":
        return generate_azure(prompt)
    else:
        raise ValueError(f"Unsupported LLM Provider: {LLM_PROVIDER}")

def main():
    response = generate("What is the capital of Turkey?")
    print(response)

if __name__ == "__main__":
    main()
