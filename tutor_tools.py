#!/usr/bin/env python3
"""Lokale Quellen und Lernfortschritt für einen Codex-Tutor; kein API-Aufruf."""
import argparse
import datetime
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = ROOT / "data" / "tutor.sqlite3"
MAX_BYTES = 2_000_000
VALID_STATUS = ("üben", "sicher")

def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB))
    db.row_factory = sqlite3.Row
    db.executescript("""
    CREATE TABLE IF NOT EXISTS documents (
      id INTEGER PRIMARY KEY, title TEXT NOT NULL, body TEXT NOT NULL, created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS progress (
      id INTEGER PRIMARY KEY, topic TEXT NOT NULL, status TEXT NOT NULL,
      note TEXT NOT NULL, created_at TEXT NOT NULL);
    """)
    return db

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

def import_document(title, body):
    title = Path(title).name
    if not title or Path(title).suffix.lower() not in (".md", ".txt", ".json"):
        raise ValueError("Nur Dateien mit .md, .txt oder .json sind unterstützt.")
    if not body.strip() or len(body.encode("utf-8")) > MAX_BYTES:
        raise ValueError("Datei ist leer oder größer als 2 MB.")
    if title.lower().endswith(".json"):
        json.loads(body)
    with connect() as db:
        cur = db.execute("INSERT INTO documents(title, body, created_at) VALUES(?,?,?)", (title, body, now()))
        return {"id":cur.lastrowid,"title":title,"lines":len(body.splitlines())}

def list_documents():
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT id,title,created_at FROM documents ORDER BY id DESC")]

def search(query):
    words = list(dict.fromkeys(re.findall(r"\w+", query.casefold())))
    if not words:
        raise ValueError("Bitte Suchbegriffe eingeben.")
    matches = []
    with connect() as db:
        for doc in db.execute("SELECT id,title,body FROM documents"):
            for line_number, line in enumerate(doc["body"].splitlines(), 1):
                score = sum(word in line.casefold() for word in words)
                if score:
                    matches.append({"document_id":doc["id"],"document":doc["title"],"line":line_number,"text":line[:600],"score":score})
    return sorted(matches, key=lambda x: (-x["score"], x["document_id"], x["line"]))[:8]

def record(topic, status, note):
    if not topic.strip() or len(topic) > 200 or status not in VALID_STATUS or len(note) > 2000:
        raise ValueError("Thema und Status prüfen; Status muss 'üben' oder 'sicher' sein.")
    with connect() as db:
        cur = db.execute("INSERT INTO progress(topic,status,note,created_at) VALUES(?,?,?,?)",
                         (topic.strip(), status, note.strip(), now()))
        return {"id":cur.lastrowid,"topic":topic.strip(),"status":status}

def progress():
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT topic,status,note,created_at FROM progress ORDER BY id DESC LIMIT 100")]

def serve(port):
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass
        def valid_host(self):
            return self.headers.get("Host", "") in ("127.0.0.1:%d" % port, "localhost:%d" % port)
        def respond(self, code, data, kind="application/json; charset=utf-8"):
            payload = data if isinstance(data, bytes) else json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(payload)
        def do_GET(self):
            if not self.valid_host():
                return self.respond(403, {"error":"Ungültiger Host"})
            if self.path in ("/", "/index.html"):
                return self.respond(200, (ROOT / "index.html").read_bytes(), "text/html; charset=utf-8")
            if self.path == "/api/documents":
                return self.respond(200, list_documents())
            if self.path == "/api/progress":
                return self.respond(200, progress())
            self.respond(404, {"error":"Nicht gefunden"})
        def do_POST(self):
            origin = self.headers.get("Origin", "")
            if not self.valid_host() or origin not in ("http://127.0.0.1:%d" % port, "http://localhost:%d" % port):
                return self.respond(403, {"error":"Nur lokale Anfragen sind erlaubt"})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > MAX_BYTES + 4096:
                    raise ValueError("Ungültige Anfragegröße.")
                if not self.headers.get("Content-Type", "").lower().startswith("application/json"):
                    raise ValueError("JSON erforderlich.")
                data = json.loads(self.rfile.read(length).decode("utf-8"))
                if self.path == "/api/import":
                    result = import_document(data.get("title", ""), data.get("body", ""))
                elif self.path == "/api/search":
                    result = search(data.get("query", ""))
                elif self.path == "/api/record":
                    result = record(data.get("topic", ""), data.get("status", ""), data.get("note", ""))
                else:
                    return self.respond(404, {"error":"Nicht gefunden"})
                self.respond(200, result)
            except (ValueError, TypeError, UnicodeError, json.JSONDecodeError) as exc:
                self.respond(400, {"error":str(exc)})
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print("Cockpit: http://127.0.0.1:%d/ (Strg+C beendet den Server)" % port, flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()

def main():
    p = argparse.ArgumentParser(description="Quellen und Lernstand für Codex verwalten.")
    subs = p.add_subparsers(dest="command", required=True)
    load = subs.add_parser("import", help="Textdatei importieren")
    load.add_argument("path")
    find = subs.add_parser("search", help="Quellenstellen suchen")
    find.add_argument("query")
    subs.add_parser("list", help="Importierte Quellen anzeigen")
    rec = subs.add_parser("record", help="Bestätigten Lernstand speichern")
    rec.add_argument("topic")
    rec.add_argument("status", choices=VALID_STATUS)
    rec.add_argument("--note", default="")
    subs.add_parser("progress", help="Lernstand anzeigen")
    srv = subs.add_parser("serve", help="Lokales Cockpit starten")
    srv.add_argument("--port", type=int, default=8765)
    args = p.parse_args()
    try:
        if args.command == "import":
            path = Path(args.path)
            if path.stat().st_size > MAX_BYTES:
                raise ValueError("Datei ist größer als 2 MB.")
            result = import_document(path.name, path.read_text(encoding="utf-8"))
        elif args.command == "search":
            result = search(args.query)
        elif args.command == "list":
            result = list_documents()
        elif args.command == "record":
            result = record(args.topic, args.status, args.note)
        elif args.command == "progress":
            result = progress()
        else:
            if not 1024 <= args.port <= 65535:
                raise ValueError("Port muss zwischen 1024 und 65535 liegen.")
            serve(args.port)
            return
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, sqlite3.Error) as exc:
        print("Fehler: " + str(exc), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
