import requests

def ask_pt(message):
    response = requests.post(
        "http://localhost:11434/api/chat",
            json={
                "model": "qwen3.5:4b",
                    "messages": [
                    {
                        "role": "system",
                        "content": "You are PT, my local AI assistant."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                        "stream": False
            },
                timeout=120
        )

    response.raise_for_status()
    return response.json()["message"]["content"]


while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    print("PT:", ask_pt(user_input))
