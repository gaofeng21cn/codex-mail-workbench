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
            account_id="work",
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

    result = dispatch_tool("mail_recent", {"account": "work", "limit": 5}, db)
    payload = json.loads(result["content"][0]["text"])

    assert payload["ok"] is True
    assert payload["messages"][0]["subject"] == "hello mcp"


def test_mcp_dispatch_recent_filters_by_date_window(tmp_path: Path) -> None:
    db = tmp_path / "mail.sqlite"
    conn = connect_email_store(db)
    try:
        for uid, subject, date_iso in [
            (1, "old mcp", "2026-05-16T09:00:00+08:00"),
            (2, "new mcp", "2026-05-17T09:00:00+08:00"),
        ]:
            upsert_email_message(
                conn,
                account_id="work",
                folder="INBOX",
                folder_slug="INBOX",
                uid=uid,
                uidvalidity=1,
                message_id=f"<mcp-{uid}@example.test>",
                subject=subject,
                sender="a@example.test",
                recipient="b@example.test",
                date_iso=date_iso,
                raw_sha256=str(uid) * 64,
                raw_eml=b"Subject: test\r\n\r\nbody",
                attachments=[],
                ingest_ts=date_iso,
            )
    finally:
        conn.close()

    result = dispatch_tool(
        "mail_recent",
        {
            "account": "work",
            "since": "2026-05-17T00:00:00+08:00",
            "until": "2026-05-18T00:00:00+08:00",
            "limit": 5,
        },
        db,
    )
    payload = json.loads(result["content"][0]["text"])

    assert payload["ok"] is True
    assert [row["subject"] for row in payload["messages"]] == ["new mcp"]
