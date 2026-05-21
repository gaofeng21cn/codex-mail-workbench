import json
from pathlib import Path

from codex_mail_workbench.mcp_server import dispatch_tool
from codex_mail_workbench.store import connect_email_store, upsert_email_message


def test_mcp_dispatch_recent_returns_messages(tmp_path: Path) -> None:
    db = tmp_path / "mail.sqlite"
    conn = connect_email_store(db)
    try:
        upsert_email_message(
            conn,
            account_id="sysu",
            folder="INBOX",
            folder_slug="INBOX",
            uid=1,
            uidvalidity=1,
            message_id="<m@example.test>",
            subject="hello mcp",
            sender="a@example.test",
            recipient="b@example.test",
            date_iso="2026-05-17T09:00:00+08:00",
            raw_sha256="3" * 64,
            raw_eml=b"Subject: hello mcp\r\n\r\nbody",
            attachments=[],
            ingest_ts="2026-05-17T09:01:00+08:00",
        )
    finally:
        conn.close()

    result = dispatch_tool("mail_recent", {"account": "sysu", "limit": 5}, db)
    payload = json.loads(result["content"][0]["text"])

    assert payload["ok"] is True
    assert payload["messages"][0]["subject"] == "hello mcp"
