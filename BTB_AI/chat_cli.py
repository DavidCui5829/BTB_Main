"""Interactive multi-turn REPL for testing the /chat endpoint locally.

Usage:
    python chat_cli.py [base_url]
"""

import sys

import requests

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8008"


def main() -> None:
    session_id = None
    print(f"Connected to {BASE_URL}. Type 'exit' to quit, 'reset' to start a new session.\n")

    while True:
        question = input("You: ").strip()
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break
        if question.lower() == "reset":
            if session_id:
                requests.delete(f"{BASE_URL}/chat/{session_id}")
            session_id = None
            print("(session reset)\n")
            continue

        resp = requests.post(
            f"{BASE_URL}/chat",
            json={"question": question, "session_id": session_id},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        session_id = data["session_id"]

        print(f"\nBot: {data['answer']}\n")
        for src in data["sources"]:
            print(f"  source: {src['interview']} / {src['topic']}")
        print()


if __name__ == "__main__":
    main()
