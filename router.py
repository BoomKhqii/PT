
import json
import requests

MODEL = "qwen3.5:4b"

def route_request(message):
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": MODEL,
            "messages": [
                {
                    # This is context of Qwen, which is the agent router. It will determine which agent to route the request to based on the message content.
                    "role": "system",
                    "content": (
                        "You are PT's agent router. "
                        "Choose the most appropriate agent for the request. "
                        "Options: trading, academic, personal, general. "
                        "Trading handles trading and backtests. "
                        "Academic handles studies and university. "
                        "Personal handles schedules and reminders. "
                        "General handles everything else. "
                        'Return JSON only: {"agent": "name"}'
                    )
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            "format": "json",
            "stream": False,
            "options": {"temperature": 0}
        },
        timeout=120
    )

    response.raise_for_status()

    content = response.json()["message"]["content"]
    result = json.loads(content)

    agent = result.get("agent", "general")

    if agent not in ["trading", "academic", "personal", "general"]:
        return "general"

    return agent


if __name__ == "__main__":
    while True:
        message = input("You: ")

        if message.lower() == "exit":
            break

        try:
            agent = route_request(message)
            print(f"PT selected: {agent.upper()} AGENT")
        except (requests.RequestException, ValueError) as error:
            print(f"Routing error: {error}")
