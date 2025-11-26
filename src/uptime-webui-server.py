#!/usr/bin/env python3
import sqlite3
import http.server
import socketserver
from pathlib import Path
import time
import json

DB = "/var/lib/uptime-checker/uptime.db"
PORT = 8080
HTML_FILE = Path(__file__).parent / "index.html"

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.serve_html()
        elif self.path == "/api/data":
            self.serve_data()
        else:
            self.send_error(404)
    
    def serve_html(self):
        with open(HTML_FILE, "r") as f:
            html = f.read()
        
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_data(self):
        now = int(time.time())
        day_ago = now - 86400
        
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        
        total = cursor.execute("SELECT COUNT(*) FROM checks WHERE timestamp > ?", (day_ago,)).fetchone()[0]
        down = cursor.execute("SELECT COUNT(*) FROM checks WHERE timestamp > ? AND status = 1", (day_ago,)).fetchone()[0]
        up = total - down
        uptime_pct = (up * 100 / total) if total > 0 else 0
        
        rows = cursor.execute("SELECT timestamp, status, response_time FROM checks WHERE timestamp > ? ORDER BY timestamp DESC LIMIT 100", (day_ago,)).fetchall()
        
        conn.close()
        
        data = {
            "uptime_pct": uptime_pct,
            "up": up,
            "total": total,
            "checks": [{"timestamp": r[0], "status": "UP" if r[1] == 0 else "DOWN", "response_time": r[2]} for r in rows]
        }
        
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server running on {PORT}")
    httpd.serve_forever()
