#!/usr/bin/env python3
"""Manage accounts for shared mode (server.py --multi-user).

    python3 tools/users.py add <name> [--admin] [--mine]   create an account (prompts for a password)
    python3 tools/users.py passwd <name>                    reset a password (signs that user out everywhere)
    python3 tools/users.py list
    python3 tools/users.py delete <name> [--purge]          remove an account (--purge also deletes its progress)

--mine makes the account keep using data/progress.db, so the progress you made in single-user mode
carries over. Friends can also sign themselves up if you start the server with CP_INVITE_CODE set.
"""
from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.auth import USERS_DIR, Accounts, AuthError  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add"); a.add_argument("name"); a.add_argument("--admin", action="store_true")
    a.add_argument("--mine", action="store_true", help="use the existing data/progress.db")
    a.add_argument("--password", help=argparse.SUPPRESS)
    p = sub.add_parser("passwd"); p.add_argument("name"); p.add_argument("--password", help=argparse.SUPPRESS)
    sub.add_parser("list")
    d = sub.add_parser("delete"); d.add_argument("name"); d.add_argument("--purge", action="store_true")
    args = ap.parse_args()
    acc = Accounts()

    def ask() -> str:
        if getattr(args, "password", None):
            return args.password
        pw = getpass.getpass("Password (8+ characters): ")
        if pw != getpass.getpass("Again: "):
            raise AuthError("Passwords don't match.")
        return pw

    try:
        if args.cmd == "add":
            acc.create_user(args.name, ask(), is_admin=args.admin, uses_main_db=args.mine)
            print(f"Created {args.name.lower()}.")
        elif args.cmd == "passwd":
            acc.set_password(args.name.lower(), ask())
            print("Password changed.")
        elif args.cmd == "list":
            for u in acc.users():
                flags = [f for f, on in (("admin", u["is_admin"]), ("main db", u["uses_main_db"])) if on]
                print(f"{u['username']:<24} created {u['created']}  {', '.join(flags)}")
        elif args.cmd == "delete":
            acc.delete_user(args.name.lower())
            if args.purge:
                for suffix in ("", "-wal", "-shm"):
                    (USERS_DIR / f"{args.name.lower()}.db{suffix}").unlink(missing_ok=True)
            print("Deleted.")
    except AuthError as e:
        raise SystemExit(str(e))


if __name__ == "__main__":
    main()
