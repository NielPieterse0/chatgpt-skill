from __future__ import annotations

import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .models import DashboardReport
from .report import report_to_dict, report_to_json


def _text(value: object) -> str:
    return html.escape("-" if value in {None, ""} else str(value))


def render_html(report: DashboardReport) -> str:
    payload = report_to_dict(report)
    summary = payload["summary"]
    rows: list[str] = []
    for skill in payload["skills"]:
        telemetry = skill["telemetry"]
        if telemetry["status"] in {"observed", "observed_incomplete"}:
            usage = (
                f"load {telemetry['loaded_count']} | apply {telemetry['applied_count']} | "
                f"complete {telemetry['completed_count']} | fail {telemetry['failed_count']}"
            )
        else:
            usage = telemetry["status"]
        last_used = telemetry["last_used_at"] or telemetry["last_used_status"]
        warnings = "; ".join(skill["warnings"]) if skill["warnings"] else ""
        rows.append(
            "<tr>"
            f"<td><strong>{_text(skill['name'])}</strong></td>"
            f"<td>{_text(skill['description'])}</td>"
            f"<td><code>{_text(skill['source_path'])}</code></td>"
            f"<td>{_text(skill['modified_at'])}</td>"
            f"<td>{_text(skill['status'])}</td>"
            f"<td>{_text(skill['adoption_status'])}</td>"
            f"<td>{_text(skill['evaluation_status'])}</td>"
            f"<td>{_text(usage)}</td>"
            f"<td>{_text(last_used)}</td>"
            f"<td>{_text(warnings)}</td>"
            "</tr>"
        )
    warning_items = "".join(f"<li>{_text(item)}</li>" for item in payload["warnings"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Workspace Skill Catalogue</title>
<style>
body{{font-family:system-ui,sans-serif;margin:2rem;color:#222}} .cards{{display:flex;gap:1rem;flex-wrap:wrap}}
.card{{border:1px solid #ccc;border-radius:.5rem;padding:.75rem 1rem;min-width:9rem}} table{{border-collapse:collapse;width:100%;margin-top:1rem;font-size:.9rem}}
th,td{{border:1px solid #ddd;padding:.5rem;vertical-align:top;text-align:left}} th{{position:sticky;top:0;background:#fff}}
code{{font-size:.8rem}} .warnings{{margin-top:1rem}} .scroll{{overflow:auto;max-height:70vh}}
</style>
</head>
<body>
<h1>Workspace Skill Catalogue</h1>
<div class="cards">
<div class="card"><strong>Total</strong><div>{summary['total_catalogue_count']}</div></div>
<div class="card"><strong>Active</strong><div>{summary['active_count']}</div></div>
<div class="card"><strong>Repo evaluated</strong><div>{summary['repo_evaluated_count']}</div></div>
<div class="card"><strong>Unevaluated</strong><div>{summary['unevaluated_count']}</div></div>
<div class="card"><strong>Coverage</strong><div>{float(summary['evaluation_coverage']) * 100:.1f}%</div></div>
</div>
<div class="warnings"><ul>{warning_items}</ul></div>
<div class="scroll"><table>
<thead><tr><th>Name</th><th>Description</th><th>Source</th><th>Modified</th><th>Status</th><th>Adoption</th><th>Evaluation</th><th>Usage</th><th>Last used</th><th>Warnings</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table></div>
</body></html>"""


def _handler(report: DashboardReport):
    html_body = render_html(report).encode("utf-8")
    json_body = report_to_json(report).encode("utf-8")

    class Handler(BaseHTTPRequestHandler):
        def _send(self, status: int, body: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _host_allowed(self) -> bool:
            port = int(self.server.server_address[1])
            supplied = self.headers.get("Host", "")
            return supplied in {"127.0.0.1", f"127.0.0.1:{port}"}

        def do_GET(self) -> None:
            if not self._host_allowed():
                self._send(403, b"forbidden\n", "text/plain; charset=utf-8")
            elif self.path == "/":
                self._send(200, html_body, "text/html; charset=utf-8")
            elif self.path == "/api/report":
                self._send(200, json_body, "application/json; charset=utf-8")
            else:
                self._send(404, b"not found\n", "text/plain; charset=utf-8")

        def _method_not_allowed(self) -> None:
            self._send(405, b"method not allowed\n", "text/plain; charset=utf-8")

        do_POST = _method_not_allowed
        do_PUT = _method_not_allowed
        do_PATCH = _method_not_allowed
        do_DELETE = _method_not_allowed

        def log_message(self, format: str, *args: object) -> None:
            return

    return Handler


def make_server(
    report: DashboardReport, *, host: str = "127.0.0.1", port: int = 8765
) -> ThreadingHTTPServer:
    if host != "127.0.0.1":
        raise ValueError("dashboard server host must be the literal loopback address 127.0.0.1")
    return ThreadingHTTPServer((host, port), _handler(report))
