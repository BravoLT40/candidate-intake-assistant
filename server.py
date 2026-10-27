#!/usr/bin/env python3
"""
Simple local runner and API proxy for Bravo LT Candidate Intake Assistant.
Handles:
1. Serving static files (index.html, sample_candidate.json)
2. Proxying folder creation requests to Google Apps Script (bypassing CORS)
"""

import http.server
import socketserver
import webbrowser
import os
import sys
import json
import urllib.request
import urllib.error

PORT = 8505
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(DIRECTORY, "config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "sfDomain": "",
        "driveBridgeUrl": ""
    }

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        pass

    def do_POST(self):
        if self.path == "/api/config":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                new_cfg = json.loads(body.decode("utf-8"))
                cfg = load_config()
                cfg.update(new_cfg)
                save_config(cfg)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "config": cfg}).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        if self.path == "/api/create-drive-folder":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode("utf-8"))
                script_url = data.get("scriptUrl") or load_config().get("driveBridgeUrl", "")

                if not script_url or not script_url.startswith("http"):
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    resp = {
                        "success": False,
                        "error": "Google Apps Script Web App URL is not configured. Please paste your deployed script URL in settings (⚙️)."
                    }
                    self.wfile.write(json.dumps(resp).encode("utf-8"))
                    return

                # Send request to Google Apps Script Web App
                req_data = json.dumps(data).encode("utf-8")
                req = urllib.request.Request(
                    script_url,
                    data=req_data,
                    headers={"Content-Type": "application/json"}
                )
                
                opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler)
                try:
                    with opener.open(req, timeout=30) as response:
                        res_body = response.read().decode("utf-8")
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(res_body.encode("utf-8"))
                except urllib.error.HTTPError as he:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    if he.code == 401:
                        err_msg = (
                            "Google returned 401 Unauthorized. This means your Google Apps Script was deployed "
                            "with access restricted to 'Only myself' or 'Within Bravo LT'. "
                            "To fix: in script.google.com, click Deploy > Manage deployments > Edit, "
                            "and set 'Who has access' to 'Anyone' (or use the 1-click Browser Direct button)."
                        )
                    else:
                        err_msg = f"Google Apps Script HTTP Error {he.code}: {he.reason}"
                    self.wfile.write(json.dumps({"success": False, "is401": (he.code == 401), "error": err_msg}).encode("utf-8"))

            except Exception as e:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/config":
            cfg = load_config()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(cfg).encode("utf-8"))
            return
        super().do_GET()

def main():
    os.chdir(DIRECTORY)
    socketserver.TCPServer.allow_reuse_address = True
    
    try:
        with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
            url = f"http://localhost:{PORT}"
            print("=" * 60)
            print("  BRAVO LT - CANDIDATE INTAKE ASSISTANT")
            print("=" * 60)
            print(f"\n🚀 App is running locally at: {url}")
            print("\nOpening your default browser now...")
            print("Press Ctrl+C to stop the server anytime.\n")
            print("=" * 60)
            
            webbrowser.open(url)
            httpd.serve_forever()
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {PORT} is already in use. Connect to: http://localhost:{PORT}")
        else:
            raise e
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    main()
