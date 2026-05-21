from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .message import extract_text_body
from .paths import default_db_path
from .store import (
    connect_email_store,
    fetch_raw_email_by_storage_ref,
    get_message_by_storage_ref,
    list_messages,
)


TOOLS = [
    {
        "name": "mail_recent",
        "description": "List recent local mail messages from the Codex Mail Workbench SQLite store.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "account": {"type": "string"},
                "folder": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 200},
            },
        },
    },
    {
        "name": "mail_search",
        "description": "Search local mail metadata by subject, sender, recipient, or message id.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "account": {"type": "string"},
                "folder": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 200},
            },
            "required": ["query"],
        },
    },
    {
        "name": "mail_read",
        "description": "Read one message body by storage_ref.",
        "inputSchema": {
            "type": "object",
            "properties": {"storage_ref": {"type": "string"}},
            "required": ["storage_ref"],
        },
    },
]


def text_result(payload: object) -> dict[str, Any]:
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(payload, ensure_ascii=False, indent=2),
            }
        ]
    }


def dispatch_tool(name: str, arguments: dict[str, Any], db_path: Path) -> dict[str, Any]:
    conn = connect_email_store(db_path)
    try:
        if name == "mail_recent":
            messages = list_messages(
                conn,
                account_ids=[arguments["account"]] if arguments.get("account") else None,
                folder_slug=str(arguments.get("folder") or "") or None,
                limit=int(arguments.get("limit") or 20),
            )
            return text_result({"ok": True, "messages": messages})
        if name == "mail_search":
            messages = list_messages(
                conn,
                account_ids=[arguments["account"]] if arguments.get("account") else None,
                folder_slug=str(arguments.get("folder") or "") or None,
                query=str(arguments["query"]),
                limit=int(arguments.get("limit") or 20),
            )
            return text_result({"ok": True, "messages": messages})
        if name == "mail_read":
            storage_ref = str(arguments["storage_ref"])
            meta = get_message_by_storage_ref(conn, storage_ref)
            raw = fetch_raw_email_by_storage_ref(conn, storage_ref)
            if not meta or raw is None:
                return text_result({"ok": False, "error": "message not found"})
            meta["body_text"] = extract_text_body(raw)
            return text_result({"ok": True, "message": meta})
    finally:
        conn.close()
    return text_result({"ok": False, "error": f"unknown tool: {name}"})


def handle_request(request: dict[str, Any], db_path: Path) -> dict[str, Any]:
    req_id = request.get("id")
    method = request.get("method")
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "codex-mail-workbench", "version": "0.1.0"},
            },
        }
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = request.get("params") or {}
        result = dispatch_tool(
            str(params.get("name") or ""),
            params.get("arguments") if isinstance(params.get("arguments"), dict) else {},
            db_path,
        )
        return {"jsonrpc": "2.0", "id": req_id, "result": result}
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"method not found: {method}"},
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="codex-mail-mcp")
    parser.add_argument("--db", default=str(default_db_path()))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    db_path = Path(args.db).expanduser()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request, db_path)
        except Exception as exc:
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32000, "message": str(exc)},
            }
        print(json.dumps(response, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
