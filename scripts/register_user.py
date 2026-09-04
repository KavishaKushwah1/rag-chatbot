"""
Usage: python scripts\register_user.py test.hr@acme.com password123
Creates a Supabase auth user. Then go promote their department in the
Supabase dashboard (Table Editor -> profiles) if you need hr/engineering.
"""
import argparse
from app.auth.supabase_client import get_anon_client


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("email")
    parser.add_argument("password")
    args = parser.parse_args()

    client = get_anon_client()
    result = client.auth.sign_up({"email": args.email, "password": args.password})
    print(f"Created user: {result.user.id} ({result.user.email})")
    print("Default department is 'public'. Promote it in Supabase Table Editor -> profiles if needed.")


if __name__ == "__main__":
    main()