from pathlib import Path

from codex_mail_workbench.store import (
    connect_email_store,
    fetch_raw_email_by_storage_ref,
    list_messages,
    storage_ref_exists,
    upsert_email_message,
)


def test_upsert_list_and_fetch_raw_message(tmp_path: Path) -> None:
    conn = connect_email_store(tmp_path / "mail.sqlite")
    try:
        raw = b"Subject: hello\r\nMessage-ID: <m1@example.test>\r\n\r\nbody"
        storage_ref = upsert_email_message(
            conn,
            account_id="sysu",
            folder="INBOX",
            folder_slug="INBOX",
            uid=10,
            uidvalidity=123,
            message_id="<m1@example.test>",
            subject="hello",
            sender="a@example.test",
            recipient="b@example.test",
            date_iso="2026-05-17T09:00:00+08:00",
            raw_sha256="1" * 64,
            raw_eml=raw,
            attachments=[],
            ingest_ts="2026-05-17T09:01:00+08:00",
        )

        rows = list_messages(conn, account_ids=["sysu"], limit=5)

        assert storage_ref_exists(conn, storage_ref)
        assert fetch_raw_email_by_storage_ref(conn, storage_ref) == raw
        assert rows[0]["storage_ref"] == storage_ref
        assert rows[0]["subject"] == "hello"
    finally:
        conn.close()

