"""
Usage: python scripts\chat_cli.py "question" --token <access_token>
Get a token first via scripts\login.py
"""
import argparse
import json
import httpx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", type=str)
    parser.add_argument("--token", required=True, help="Supabase access token from scripts/login.py")
    args = parser.parse_args()

    payload = {"query": args.query}
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
                if current_event == "sources":
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