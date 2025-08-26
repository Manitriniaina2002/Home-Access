#!/usr/bin/env python3
import sqlite3
from pathlib import Path
import sys

# locate project db (two levels up from scripts folder)
db = Path(__file__).resolve().parents[1] / 'db.sqlite3'
if not db.exists():
    print('No database file found at', db)
    sys.exit(0)

conn = sqlite3.connect(str(db))
cur = conn.cursor()
try:
    cur.execute("SELECT username, email, is_superuser, is_staff FROM auth_user")
    rows = cur.fetchall()
    if not rows:
        print('No users found in auth_user table')
    else:
        print('username | email | is_superuser | is_staff')
        for r in rows:
            username = r[0]
            email = r[1] or ''
            is_super = r[2]
            is_staff = r[3]
            print(f"{username} | {email} | {is_super} | {is_staff}")
except Exception as e:
    print('Error querying auth_user:', e)
finally:
    conn.close()
