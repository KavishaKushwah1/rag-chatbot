"""
Usage: python scripts\\chat_cli.py "What is the PTO policy?"
Requires the API server running: uvicorn app.main:app --reload
"""
import argparse
import json
import httpx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", type=str)
    parser.add_argument("--permissions", nargs="*", default=None)
    args = parser.parse_args()

    payload = {"query": args.query, "permissions": args.permissions}

    with httpx.stream("POST", "http://localhost:8000/chat", json=payload, timeout=60) as response:
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
                elif current_event == "done":
                    print("\n")


if __name__ == "__main__":
    main()