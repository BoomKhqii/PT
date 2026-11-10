from Agents import personal
from Agents.trading import SYSTEM_PROMPT as TRADING_PROMPT
from Agents.academic import SYSTEM_PROMPT as ACADEMIC_PROMPT
from Agents.personal import SYSTEM_PROMPT as PERSONAL_PROMPT
import requests
from router import route_request

MODEL = "qwen3.5:4b"

AGENTS = {
    "trading": (
        TRADING_PROMPT
    ),
    "academic": (
        ACADEMIC_PROMPT
    ),
    "personal": (
        PERSONAL_PROMPT
    ),
    "general": (
        "You are PT, a helpful local AI assistant."
    )
}


def ask_pt(message):
    # Step 1: PT decides which agent to use
    agent = route_request(message)
    print(f"[PT] Delegating to: {agent.upper()}")

    # Step 2: Load the specialist's instructions
    system_prompt = AGENTS[agent]

    # Step 3: Ask Qwen to respond as that specialist
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
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
    user_input = input("\nYou: ")

    if user_input.lower() == "exit":
        break

    try:
        answer = ask_pt(user_input)
        print(f"\nPT: {answer}")
    except (requests.RequestException, ValueError) as error:
        print(f"PT Error: {error}")
