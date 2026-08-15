from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .report import build_report, report_to_json
from .web import make_server


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a read-only workspace skill catalogue dashboard report."
    )
    parser.add_argument(
        "--catalog-root",
        action="append",
        required=True,
        type=Path,
        help="Canonical skill catalogue root. Repeat for multiple roots.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    telemetry = parser.add_mutually_exclusive_group()
    telemetry.add_argument("--telemetry-db", type=Path)
    telemetry.add_argument("--telemetry-json", type=Path)
    parser.add_argument("--output", type=Path, help="Optional JSON report path.")
    parser.add_argument("--serve", action="store_true", help="Serve the local read-only dashboard.")
    parser.add_argument("--host", default="127.0.0.1", choices=("127.0.0.1",))
    parser.add_argument("--port", type=int, default=8765)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not 0 <= args.port <= 65535:
        print("ERROR: --port must be between 0 and 65535", file=sys.stderr)
        return 2
    report = build_report(
        args.catalog_root,
        repo_root=args.repo_root,
        telemetry_db=args.telemetry_db,
        telemetry_json=args.telemetry_json,
    )
    rendered = report_to_json(report)
    if args.output is not None:
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        except OSError as exc:
            print(f"ERROR: could not write report: {exc}", file=sys.stderr)
            return 2
    if not args.serve:
        sys.stdout.write(rendered)
        return 0
    server = make_server(report, host=args.host, port=args.port)
    host, port = server.server_address[:2]
    print(f"Workspace Skill Catalogue: http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
