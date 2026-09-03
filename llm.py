from config import OLLAMA_MODEL, OPENROUTER_URL, OPENROUTER_API_KEY, OPENROUTER_MODEL
import ollama
import requests

def generate_local(prompt):
    response = ollama.chat(
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
            },
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()

        if "choices" in data:
            choices_list = data["choices"]
            first_choice = choices_list[0]
            message = first_choice.get("message")
            content = message.get("content")
            return content
        else:
            return None
        
    except requests.exceptions.RequestException as err:
        print(f"Request error occured: {err}")

def main():
    response = generate_api("Say hello in one sentence.")
    print(response)
    
if __name__ == "__main__":
    main()
