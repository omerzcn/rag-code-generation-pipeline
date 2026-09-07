import requests

url = "http://127.0.0.1:8000/generate"

data = {
    "question": "How do I take a single distance measurement from an HC-SR04 ultrasonic sensor?"
}

response = requests.post(
    url=url, json=data, timeout=30,
)

print(response.status_code)
print(response.json())
