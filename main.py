
import requests
from router import route_request

MODEL = "qwen3.5:4b"

AGENTS = {
    "trading": (
        "You are PT's Trading Agent. "
        "Specialize in algorithmic trading, backtesting, "
        "risk management, and strategy analysis."
    ),
    "academic": (
        "You are PT's Academic Agent. "
        "Help with computer science, university subjects, "
        "learning concepts, and exam preparation."
    ),
    "personal": (
        "You are PT's Personal Life Agent. "
        "Help organize schedules, reminders, "
        "daily activities, and personal tasks. "
        "Do not claim to have saved a reminder unless a tool has done so."
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
