"""
Usage:
  python -m scripts.chat_cli "question" --token <access_token>
  python -m scripts.chat_cli "follow-up" --token <access_token> --session <session_id from previous reply>
"""
import argparse
import json
import httpx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", type=str)
    parser.add_argument("--token", required=True)
    parser.add_argument("--session", default=None, help="Reuse a session_id to keep short-term memory")
    args = parser.parse_args()

    payload = {"query": args.query, "session_id": args.session}
    headers = {"Authorization": f"Bearer {args.token}"}
    current_event = None

    with httpx.stream("POST", "http://localhost:8000/chat", json=payload, headers=headers, timeout=60) as response:
        if response.status_code != 200:
            print(f"HTTP {response.status_code}: {response.read().decode()}")
            return

        for line in response.iter_lines():
            if not line:
                continue
            if line.startswith("event:"):
                current_event = line.split(":", 1)[1].strip()
                continue
            if line.startswith("data:"):
                data = line.split(":", 1)[1].strip()
                if current_event == "session":
                    session_id = json.loads(data)["session_id"]
                    print(f"[session_id: {session_id}]")
                elif current_event == "sources":
                    sources = json.loads(data)
                    if sources:
                        print("Sources:", [s["source"] for s in sources])
                        print("-" * 50)
                elif current_event == "token":
                    print(data, end="", flush=True)
                elif current_event == "error":
                    err = json.loads(data)
                    print(f"\n[ERROR] {err['message']}")
                elif current_event == "done":
                    print("\n")


if __name__ == "__main__":
    main()