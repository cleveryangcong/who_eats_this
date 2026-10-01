"""Local page to match each photo to a person. Run: python3 tools/label_server.py"""
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANSWERS = ROOT / "data" / "answers.json"
PORT = 8765


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if self.path in ("/label", "/label/"):
            self.path = "/tools/label.html"
        super().do_GET()

    def do_POST(self):
        if self.path != "/save":
            self.send_error(404)
            return
        body = self.rfile.read(int(self.headers["Content-Length"]))
        answers = json.loads(body)
        ANSWERS.write_text(json.dumps(answers, ensure_ascii=False, indent=1) + "\n")
        self.send_response(204)
        self.end_headers()


if __name__ == "__main__":
    print(f"Label photos: http://localhost:{PORT}/label")
    print(f"Play the game: http://localhost:{PORT}/")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
