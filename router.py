
import json
import requests
# from memory.retrieval import retrieve_memory

MODEL = "qwen3.5:4b"
ROUTER_PROMPT = """
    Choose the agent and decide whether saved user information would help answer
    the request. Return exactly one JSON object in this format:

    {"agent": "general", "memory_terms": []}
    - The agent must be one of: general, personal, academic, trading.
    - For memory_terms, return up to 5 short keywords or phrases that could appear in a saved memory. Prefer names, topics, and distinctive terms.
    - Use recent conversation, if provided, to resolve references like "thatproject" or "my usual language".
    - Return an empty list for greetings and requests that can be answered without saved user information.
    - Return plain search terms. Python will turn them into FTS5 syntax.

    User: What programming language do I prefer?
    Output: {"agent": "personal", "memory_terms": ["programming language", "prefer", "prefers"]}

    User: Explain what a Python list is.
    Output: {"agent": "general", "memory_terms": []}
"""

def route_request(message):
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": MODEL,
            "messages": [
                # This is context of Qwen, which is the agent router. It will determine which agent to route the request to based on the message content.
                { "role": "system", "content": ROUTER_PROMPT },
                { "role": "user", "content": message }
            ],
            "format": "json",
            "stream": False,
            "options": {"temperature": 0},
            "think": False,
        },
        timeout=120
    )

    response.raise_for_status()

    content = response.json()["message"]["content"]
    print("Router content:", repr(content))
    result = json.loads(content)

    agent = result.get("agent", "general")

    if agent not in ["trading", "academic", "personal", "general"]:
        return "general", []

    raw_terms = result.get("memory_terms", []) # List of terms to search for in memory
    terms = ( # Filter out any non-string or empty terms
        [term.strip() for term in raw_terms if isinstance(term, str) and term.strip()]
        if isinstance(raw_terms, list)
        else []
    )
    return agent, terms


if __name__ == "__main__":
    while True:
        message = input("You: ")

        if message.lower() == "exit":
            break

        try:
            agent, terms = route_request(message)
            print(f"PT selected: {agent.upper()} AGENT")
            print(f"Memory terms: {terms}")
        except (requests.RequestException, ValueError) as error:
            print(f"Routing error: {error}")
