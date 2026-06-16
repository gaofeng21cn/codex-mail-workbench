from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from . import __version__
from .config import KEYCHAIN_SERVICE, LEGACY_KEYCHAIN_SERVICE, load_accounts_config
from .message import extract_text_body
from .paths import default_config_path, default_db_path, default_state_dir
from .store import (
    connect_email_store,
    fetch_raw_email_by_storage_ref,
    get_message_by_storage_ref,
    list_messages_with_raw,
    list_messages,
)
from .sync import sync_account


def emit(payload: object, *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    if isinstance(payload, dict):
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(payload)


def fail(message: str, *, as_json: bool, code: int = 1) -> int:
    payload = {"ok": False, "error": message}
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
    else:
        print(f"ERROR: {message}", file=sys.stderr)
    return code


def open_conn(db: Path):
    return connect_email_store(db)


def cmd_doctor(args: argparse.Namespace) -> int:
    config_path = Path(args.config).expanduser()
    db_path = Path(args.db).expanduser()
    accounts = {}
    config_error = ""
    if config_path.exists():
        try:
            accounts = load_accounts_config(config_path)
        except Exception as exc:
            config_error = str(exc)
    payload = {
        "ok": not config_error,
        "version": __version__,
        "command": shutil.which("codex-mail"),
        "state_dir": str(default_state_dir()),
        "config_path": str(config_path),
        "config_exists": config_path.exists(),
        "config_error": config_error,
        "db_path": str(db_path),
        "db_exists": db_path.exists(),
        "accounts": sorted(accounts.keys()),
        "keychain_services": [
            svc for svc in [KEYCHAIN_SERVICE, LEGACY_KEYCHAIN_SERVICE] if svc
        ],
    }
    emit(payload, as_json=args.json)
    return 0 if payload["ok"] else 1


def cmd_accounts(args: argparse.Namespace) -> int:
    accounts = load_accounts_config(Path(args.config).expanduser())
    emit(
        {
            "ok": True,
            "accounts": [
                {
                    "account_id": account.account_id,
                    "email": account.email,
                    "imap_host": account.imap.host,
                    "smtp_host": account.smtp.host,
                    "include_folders": account.include_folders,
                    "exclude_folders": account.exclude_folders,
                }
                for account in accounts.values()
            ],
        },
        as_json=args.json,
    )
    return 0


def cmd_recent(args: argparse.Namespace) -> int:
    conn = open_conn(Path(args.db).expanduser())
    try:
        rows = list_messages(
            conn,
            account_ids=[args.account] if args.account else None,
            folder_slug=args.folder,
            since=args.since,
            until=args.until,
            limit=args.limit,
        )
    finally:
        conn.close()
    emit({"ok": True, "messages": rows}, as_json=args.json)
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    conn = open_conn(Path(args.db).expanduser())
    try:
        rows = list_messages(
            conn,
            account_ids=[args.account] if args.account else None,
            folder_slug=args.folder,
            query=args.query,
            since=args.since,
            until=args.until,
            limit=args.limit,
        )
        if args.include_body and len(rows) < args.limit:
            seen = {row["storage_ref"] for row in rows}
            query = args.query.lower()
            for meta, raw in list_messages_with_raw(
                conn,
                account_ids=[args.account] if args.account else None,
                folder_slug=args.folder,
                since=args.since,
                until=args.until,
                limit=args.max_scan,
            ):
                if meta["storage_ref"] in seen:
                    continue
                if query not in extract_text_body(raw).lower():
                    continue
                meta["body_hit"] = True
                rows.append(meta)
                seen.add(meta["storage_ref"])
                if len(rows) >= args.limit:
                    break
    finally:
        conn.close()
    emit({"ok": True, "messages": rows}, as_json=args.json)
    return 0


def cmd_read(args: argparse.Namespace) -> int:
    conn = open_conn(Path(args.db).expanduser())
    try:
        meta = get_message_by_storage_ref(conn, args.storage_ref)
        raw = fetch_raw_email_by_storage_ref(conn, args.storage_ref)
    finally:
        conn.close()
    if not meta or raw is None:
        return fail("message not found", as_json=args.json, code=2)
    meta["body_text"] = extract_text_body(raw)
    if args.include_raw:
        meta["raw_eml"] = raw.decode("utf-8", errors="replace")
    emit({"ok": True, "message": meta}, as_json=args.json)
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    payload = sync_account(
        config_path=Path(args.config).expanduser(),
        db_path=Path(args.db).expanduser(),
        account_id=args.account,
        mode=args.mode,
        limit_per_folder=args.limit_per_folder,
        dry_run=args.dry_run,
    )
    emit(payload, as_json=args.json)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="codex-mail")
    parser.add_argument("--json", action="store_true", help="输出稳定 JSON")
    parser.add_argument("--config", default=str(default_config_path()), help="accounts.yaml 路径")
    parser.add_argument("--db", default=str(default_db_path()), help="SQLite 邮件库路径")
    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor", help="检查配置、数据库和安装状态")
    doctor.set_defaults(func=cmd_doctor)

    accounts = sub.add_parser("accounts", help="列出配置账号")
    accounts.set_defaults(func=cmd_accounts)

    recent = sub.add_parser("recent", help="列出最近邮件")
    recent.add_argument("--account", default="")
    recent.add_argument("--folder", default="")
    recent.add_argument("--since", default="", help="include messages at or after this ISO datetime")
    recent.add_argument("--until", default="", help="include messages before this ISO datetime")
    recent.add_argument("--limit", type=int, default=20)
    recent.set_defaults(func=cmd_recent)

    search = sub.add_parser("search", help="搜索本地邮件元数据")
    search.add_argument("query")
    search.add_argument("--account", default="")
    search.add_argument("--folder", default="")
    search.add_argument("--since", default="", help="include messages at or after this ISO datetime")
    search.add_argument("--until", default="", help="include messages before this ISO datetime")
    search.add_argument("--limit", type=int, default=20)
    search.add_argument("--include-body", action=argparse.BooleanOptionalAction, default=True)
    search.add_argument("--max-scan", type=int, default=500)
    search.set_defaults(func=cmd_search)

    read = sub.add_parser("read", help="读取一封邮件正文")
    read.add_argument("storage_ref")
    read.add_argument("--include-raw", action="store_true")
    read.set_defaults(func=cmd_read)

    sync = sub.add_parser("sync", help="从 IMAP 同步邮件到本地 SQLite")
    sync.add_argument("--account", required=True)
    sync.add_argument("--mode", choices=["initial", "incremental"], default="incremental")
    sync.add_argument("--limit-per-folder", type=int, default=None)
    sync.add_argument("--dry-run", action="store_true")
    sync.set_defaults(func=cmd_sync)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except Exception as exc:
        return fail(str(exc), as_json=getattr(args, "json", False))


if __name__ == "__main__":
    raise SystemExit(main())
