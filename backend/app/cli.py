import argparse
import getpass
import sys

import psycopg2

from app import repository
from app.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from app.security import MAX_PASSWORD_BYTES, hash_password


def create_user(username):
    password = getpass.getpass("Password: ")
    if password != getpass.getpass("Repeat password: "):
        sys.exit("Passwords do not match")
    if not 8 <= len(password.encode()) <= MAX_PASSWORD_BYTES:
        sys.exit(f"Password must be 8-{MAX_PASSWORD_BYTES} bytes long")

    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, dbname=DB_NAME
    )
    try:
        with conn, conn.cursor() as cur:
            repository.create_user(cur, username, hash_password(password))
    finally:
        conn.close()
    print(f"User {username} saved")


def main():
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create-user", help="create a user or reset its password")
    create.add_argument("username")
    args = parser.parse_args()

    if args.command == "create-user":
        create_user(args.username)


if __name__ == "__main__":
    main()
