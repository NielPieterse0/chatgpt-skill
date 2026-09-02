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
    compliance = summary.get("compliance", {})
    compliance_counts = compliance.get("counts", {}) if isinstance(compliance, dict) else {}
    compliance_status = compliance.get("status", "not_available") if isinstance(compliance, dict) else "invalid"
    audit_age = compliance.get("audit_age_days") if isinstance(compliance, dict) else None
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
    intake_rows: list[str] = []
    for item in payload["intake"]:
        issue = item["source_issue"]
        assessments = " | ".join(
            f"{name}:{state}" for name, state in sorted(item["assessment_states"].items())
        )
        warnings = "; ".join(item["warnings"]) if item["warnings"] else ""
        intake_rows.append(
            "<tr>"
            f"<td><strong>{_text(item['candidate_id'])}</strong></td>"
            f"<td>{_text(item['candidate_type'])}</td>"
            f"<td>{_text(item['provenance_type'])} / {_text(item['provenance_state'])}</td>"
            f"<td>{_text(item['license_state'])}</td>"
            f"<td>{_text(assessments)}</td>"
            f"<td>{_text(item['evaluation_state'])}</td>"
            f"<td>{_text(item['disposition'])}</td>"
            f"<td>{_text(item['next_action'])}</td>"
            f"<td>{_text(issue['repository'])}#{_text(issue['number'])}</td>"
            f"<td>{_text(item['work_management_state'])}</td>"
            f"<td>{_text(warnings)}</td>"
            "</tr>"
        )
    work_status = payload["sources"]["work_management"]["status"]
    work_verified = work_status == "observed"
    work_groups: dict[str, list[str]] = {}
    for item in payload["work"]:
        issue = item["source_issue"]
        issue_link = (
            f'<a href="{html.escape(str(issue["url"]), quote=True)}">'
            f'#{_text(issue["number"])}</a>'
        )
        row = (
            "<tr>"
            f"<td>{issue_link}</td><td><strong>{_text(item['title'])}</strong></td>"
            f"<td>{_text(item['work_state'])}</td><td>{_text(item['priority'])}</td>"
            f"<td>{_text(item['effort'])}</td><td>{_text(item['execution_owner'])}</td>"
            f"<td>{_text(item['blocked_by'])}</td>"
            "</tr>"
        )
        if work_verified:
            group_name = f"State: {item['work_state']}"
        else:
            group_name = f"Unverified state: {item['work_state']}"
        work_groups.setdefault(group_name, []).append(row)
    work_sections = "".join(
        f"<h3>{_text(name)} ({len(group)})</h3><div class=\"scroll\"><table>"
        "<thead><tr><th>Issue</th><th>Work</th><th>KIS state</th><th>Priority</th><th>Effort</th>"
        "<th>Owner</th><th>Blocked by</th></tr></thead>"
        f"<tbody>{''.join(group)}</tbody></table></div>"
        for name, group in work_groups.items()
        if group
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
<div class="card"><strong>Compliance</strong><div>{_text(compliance_status)}</div><div>C {compliance_counts.get('compliant', 0)} | P {compliance_counts.get('partial', 0)} | N {compliance_counts.get('non_compliant', 0)} | U {compliance_counts.get('unevidenced', 0)}</div></div>
<div class="card"><strong>Audit age</strong><div>{_text(audit_age)} days</div></div>
<div class="card"><strong>Intake candidates</strong><div>{summary['intake_candidate_count']}</div></div>
<div class="card"><strong>Intake actionable</strong><div>{summary['intake_actionable_count']}</div></div>
<div class="card"><strong>Intake WM blocked</strong><div>{summary['intake_work_management_blocked_count']}</div></div>
<div class="card"><strong>Open Work items</strong><div>{_text(summary['work_item_count'])}</div></div>
</div>
<div class="warnings"><ul>{warning_items}</ul></div>
<h2>Lifecycle work queue</h2>
<p>Work projection status: <strong>{_text(work_status)}</strong></p>
{work_sections}
<h2>Skill catalogue</h2>
<div class="scroll"><table>
<thead><tr><th>Name</th><th>Description</th><th>Source</th><th>Modified</th><th>Status</th><th>Adoption</th><th>Evaluation</th><th>Usage</th><th>Last used</th><th>Warnings</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table></div>
<h2>Intake queue</h2>
<div class="scroll"><table>
<thead><tr><th>Candidate</th><th>Type</th><th>Provenance</th><th>License</th><th>Assessments</th><th>Evaluation</th><th>Disposition</th><th>Next action</th><th>Source issue</th><th>Work Management</th><th>Warnings</th></tr></thead>
<tbody>{''.join(intake_rows)}</tbody>
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
            content_length = self.headers.get("Content-Length")
            if content_length is not None:
                try:
                    remaining = int(content_length)
                except ValueError:
                    remaining = 0
                if remaining > 0:
                    self.rfile.read(remaining)
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
