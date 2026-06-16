import json
import os
import subprocess
import sys
from pathlib import Path

from codex_mail_workbench.store import connect_email_store, upsert_email_message


def run_cli(db: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    root = Path(__file__).resolve().parents[1]
    env["PYTHONPATH"] = str(root / "src")
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "codex_mail_workbench.cli",
            "--db",
            str(db),
            "--json",
            *args,
        ],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def seed_message(db: Path) -> str:
    conn = connect_email_store(db)
    try:
        raw = (
            b"Subject: Research thread\r\n"
            b"From: editor@example.test\r\n"
            b"To: work@example.com\r\n"
            b"Message-ID: <seed@example.test>\r\n"
            b"\r\n"
            b"Please review this manuscript."
        )
        return upsert_email_message(
            conn,
            account_id="work",
            folder="INBOX",
            folder_slug="INBOX",
            uid=1,
            uidvalidity=1,
            message_id="<seed@example.test>",
            subject="Research thread",
            sender="editor@example.test",
            recipient="work@example.com",
            date_iso="2026-05-17T09:00:00+08:00",
            raw_sha256="2" * 64,
            raw_eml=raw,
            attachments=[],
            ingest_ts="2026-05-17T09:01:00+08:00",
        )
    finally:
        conn.close()


def test_cli_recent_search_and_read_json(tmp_path: Path) -> None:
    db = tmp_path / "mail.sqlite"
    storage_ref = seed_message(db)

    recent = run_cli(db, "recent", "--account", "work", "--limit", "10")
    search = run_cli(db, "search", "manuscript", "--account", "work")
    read = run_cli(db, "read", storage_ref)

    assert recent.returncode == 0, recent.stderr
    assert search.returncode == 0, search.stderr
    assert read.returncode == 0, read.stderr

    recent_payload = json.loads(recent.stdout)
    search_payload = json.loads(search.stdout)
    read_payload = json.loads(read.stdout)

    assert recent_payload["ok"] is True
    assert recent_payload["messages"][0]["subject"] == "Research thread"
    assert search_payload["messages"][0]["storage_ref"] == storage_ref
    assert "Please review" in read_payload["message"]["body_text"]


def test_cli_recent_filters_by_date_window(tmp_path: Path) -> None:
    db = tmp_path / "mail.sqlite"
    conn = connect_email_store(db)
    try:
        for uid, subject, date_iso in [
            (1, "older thread", "2026-05-16T09:00:00+08:00"),
            (2, "current thread", "2026-05-17T09:00:00+08:00"),
        ]:
            upsert_email_message(
                conn,
                account_id="work",
                folder="INBOX",
                folder_slug="INBOX",
                uid=uid,
                uidvalidity=1,
                message_id=f"<cli-{uid}@example.test>",
                subject=subject,
                sender="editor@example.test",
                recipient="work@example.com",
                date_iso=date_iso,
                raw_sha256=str(uid) * 64,
                raw_eml=b"Subject: test\r\n\r\nbody",
                attachments=[],
                ingest_ts=date_iso,
            )
    finally:
        conn.close()

    result = run_cli(
        db,
        "recent",
        "--account",
        "work",
        "--since",
        "2026-05-17T00:00:00+08:00",
        "--until",
        "2026-05-18T00:00:00+08:00",
        "--limit",
        "10",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert [row["subject"] for row in payload["messages"]] == ["current thread"]


def test_cli_doctor_omits_empty_legacy_keychain_service(tmp_path: Path) -> None:
    db = tmp_path / "mail.sqlite"
    result = run_cli(db, "doctor")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["keychain_services"] == ["codex-mail-workbench"]
