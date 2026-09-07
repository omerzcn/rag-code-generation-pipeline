from config import OLLAMA_MODEL, OLLAMA_HOST, OPENROUTER_URL, OPENROUTER_API_KEY, OPENROUTER_MODEL
import ollama
import requests

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

def main():
    response = generate_api("Say hello in one sentence.")
    print(response)
    
if __name__ == "__main__":
    main()
