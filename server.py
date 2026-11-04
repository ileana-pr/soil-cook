#!/usr/bin/env python3
"""local server: the page, plus a small database api.
listens on this computer only, so the database is not open to the network."""

import json
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "db" / "soil.sqlite"
HOST, PORT = "127.0.0.1", 8000
USER_KEYS = {"plan", "prices", "premix", "calls", "quotes", "tests"}
TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".mjs": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".ico": "image/x-icon",
}


def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.executescript((ROOT / "db" / "schema.sql").read_text())
    if con.execute("SELECT COUNT(*) AS n FROM suppliers").fetchone()["n"] == 0:
        rows = json.loads((ROOT / "db" / "seed-suppliers.json").read_text())
        con.executemany(
            """INSERT INTO suppliers
               (id, name, type, address, phone, website, hours, miles, ask_about)
               VALUES (:id, :name, :type, :address, :phone, :website, :hours, :miles, :ask_about)""",
            rows,
        )
        con.commit()
    return con


def suppliers_for_app(con):
    out = []
    for s in con.execute("SELECT * FROM suppliers ORDER BY id"):
        out.append({
            "n": s["id"],
            "name": s["name"],
            "type": s["type"],
            "addr": s["address"],
            "phone": s["phone"],
            "web": s["website"],
            "hours": s["hours"],
            "miles": s["miles"],
            "ask": s["ask_about"],
        })
    return out


def user_for_app(con):
    return {row["key"]: json.loads(row["value"]) for row in con.execute("SELECT key, value FROM user_data")}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("%s %s" % (self.command, self.path.split("?", 1)[0]))

    def send_json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("cache-control", "no-store")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("content-length", "0") or "0")
        raw = self.rfile.read(length) if length else b""
        try:
            return json.loads(raw or b"null"), None
        except json.JSONDecodeError:
            return None, "body must be json"

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path == "/api/state":
            con = connect()
            try:
                payload = {"suppliers": suppliers_for_app(con), "user": user_for_app(con)}
            finally:
                con.close()
            self.send_json(200, payload)
            return
        if path.startswith("/api/"):
            self.send_json(404, {"error": "not found"})
            return
        self.serve_file(path)

    def do_PUT(self):
        path = unquote(urlparse(self.path).path)
        if not path.startswith("/api/user/"):
            self.send_json(404, {"error": "not found"})
            return
        key = path[len("/api/user/"):]
        if key not in USER_KEYS:
            self.send_json(404, {"error": "unknown section"})
            return
        data, err = self.read_json()
        if err:
            self.send_json(400, {"error": err})
            return
        if not isinstance(data, dict):
            self.send_json(400, {"error": "body must be an object"})
            return
        con = connect()
        try:
            con.execute(
                """INSERT INTO user_data (key, value, updated_at)
                   VALUES (?, ?, datetime('now'))
                   ON CONFLICT(key) DO UPDATE SET
                     value = excluded.value,
                     updated_at = excluded.updated_at""",
                (key, json.dumps(data)),
            )
            con.commit()
        finally:
            con.close()
        self.send_json(200, {"ok": True})

    def serve_file(self, path):
        if path in ("/docs", "/db", "/server.py") or path.startswith("/docs/") or path.startswith("/db/"):
            self.send_error(404)
            return
        rel = "index.html" if path == "/" else path.lstrip("/")
        full = (ROOT / rel).resolve()
        if full != ROOT and ROOT not in full.parents:
            self.send_error(403)
            return
        if not full.is_file():
            self.send_error(404)
            return
        body = full.read_bytes()
        self.send_response(200)
        self.send_header("content-type", TYPES.get(full.suffix, "application/octet-stream"))
        self.send_header("cache-control", "no-store")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    connect().close()
    print(f"Soil Cook at http://{HOST}:{PORT}", flush=True)
    print("database file: db/soil.sqlite", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
