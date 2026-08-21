import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

WEB_DIR = Path(__file__).parent / "web"

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".ico": "image/x-icon",
}

MIN_STEPS = 1
MAX_STEPS = 32


class AgentState:
    def __init__(self, agent):
        self.agent = agent
        self.lock = threading.Lock()

    def run(self, query, max_steps=8):
        with self.lock:
            return self.agent.run(query, max_steps=max_steps)

    def reset(self):
        with self.lock:
            self.agent.reset()

    def tools(self):
        tools = []
        for fn in self.agent._functions.values():
            schema = getattr(fn, "_needle_tool", None)
            name = schema.get("name") if schema else getattr(fn, "__name__", "unknown")
            description = schema.get("description", "") if schema else ""
            parameters = []
            if schema:
                parameters = list(schema.get("parameters", {}).get("properties", {}))
            tools.append({"name": name, "description": description, "parameters": parameters})
        return tools


class Handler(BaseHTTPRequestHandler):
    state = None

    def _send_json(self, code, payload):
        data = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, path):
        try:
            data = path.read_bytes()
        except OSError:
            self._send_json(404, {"error": "not found"})
            return
        self.send_response(200)
        self.send_header("Content-Type", CONTENT_TYPES.get(path.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b""
        if not raw:
            return {}
        return json.loads(raw)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            self._send_file(WEB_DIR / "index.html")
        elif path == "/api/health":
            self._send_json(200, {"status": "ok", "model": "needle-2"})
        elif path == "/api/tools":
            self._send_json(200, {"tools": self.state.tools()})
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        try:
            body = self._read_json()
        except (ValueError, UnicodeDecodeError):
            self._send_json(400, {"error": "invalid JSON body"})
            return

        if path == "/api/run":
            self._handle_run(body)
        elif path == "/api/reset":
            self.state.reset()
            self._send_json(200, {"ok": True})
        else:
            self._send_json(404, {"error": "not found"})

    def _handle_run(self, body):
        query = body.get("query")
        if not isinstance(query, str) or not query.strip():
            self._send_json(400, {"error": "'query' must be a non-empty string"})
            return
        max_steps = body.get("max_steps", 8)
        if not isinstance(max_steps, int) or isinstance(max_steps, bool) or not MIN_STEPS <= max_steps <= MAX_STEPS:
            self._send_json(400, {"error": f"'max_steps' must be an integer between {MIN_STEPS} and {MAX_STEPS}"})
            return
        try:
            result = self.state.run(query.strip(), max_steps=max_steps)
        except Exception as exc:
            self._send_json(500, {"error": str(exc)})
            return
        self._send_json(200, result)

    def log_message(self, *args):
        pass


def serve(agent, host="127.0.0.1", port=8000):
    Handler.state = AgentState(agent)
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"web ui + api ready: http://{host}:{port}", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
