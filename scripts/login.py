"""
Usage: python scripts\login.py test.hr@acme.com password123
Prints an access token to use as: --token <value> in chat_cli.py
"""
import argparse
from app.auth.supabase_client import get_anon_client


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("email")
    parser.add_argument("password")
    args = parser.parse_args()

    client = get_anon_client()
    result = client.auth.sign_in_with_password({"email": args.email, "password": args.password})
    print(result.session.access_token)


if __name__ == "__main__":
    main()