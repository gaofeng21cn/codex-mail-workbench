from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


KEYCHAIN_SERVICE = "codex-mail-workbench"
LEGACY_KEYCHAIN_SERVICE = os.environ.get("CODEX_MAIL_LEGACY_KEYCHAIN_SERVICE", "")


@dataclass(frozen=True)
class MailEndpoint:
    host: str
    port: int
    security: str
    username: str
    credential_ref: str


@dataclass(frozen=True)
class MailAccount:
    account_id: str
    email: str
    imap: MailEndpoint
    smtp: MailEndpoint
    include_folders: list[str]
    exclude_folders: list[str]


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {path}")
    ruby = [
        "ruby",
        "-ryaml",
        "-rjson",
        "-e",
        "data = YAML.safe_load(File.read(ARGV[0]), aliases: true) || {}; puts JSON.generate(data)",
        str(path),
    ]
    result = subprocess.run(ruby, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"YAML 解析失败: {detail}")
    parsed = json.loads(result.stdout)
    if not isinstance(parsed, dict):
        raise ValueError("配置根节点必须是对象")
    return parsed


def _dict(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} 必须是对象")
    return value


def _str(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} 必须是非空字符串")
    return value.strip()


def _int(value: Any, field: str) -> int:
    if not isinstance(value, int):
        raise ValueError(f"{field} 必须是整数")
    return value


def _string_list(value: Any, field: str, default: list[str]) -> list[str]:
    if value is None:
        value = default
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
        raise ValueError(f"{field} 必须是字符串数组")
    return [x.strip() for x in value if x.strip()]


def _endpoint(raw: dict[str, Any], field: str) -> MailEndpoint:
    credential_ref = raw.get("credential_ref", raw.get("secret_ref"))
    return MailEndpoint(
        host=_str(raw.get("host"), f"{field}.host"),
        port=_int(raw.get("port"), f"{field}.port"),
        security=_str(raw.get("security"), f"{field}.security").lower(),
        username=_str(raw.get("username"), f"{field}.username"),
        credential_ref=_str(credential_ref, f"{field}.credential_ref"),
    )


def load_accounts_config(path: Path) -> dict[str, MailAccount]:
    data = load_yaml(path)
    accounts_raw = data.get("accounts")
    if not isinstance(accounts_raw, list):
        raise ValueError("accounts 必须是数组")
    accounts: dict[str, MailAccount] = {}
    for idx, item in enumerate(accounts_raw):
        raw = _dict(item, f"accounts[{idx}]")
        account_id = _str(raw.get("account_id"), f"accounts[{idx}].account_id")
        folders = _dict(raw.get("folders", {}), f"accounts[{idx}].folders")
        account = MailAccount(
            account_id=account_id,
            email=_str(raw.get("email"), f"accounts[{idx}].email"),
            imap=_endpoint(_dict(raw.get("imap"), f"accounts[{idx}].imap"), f"accounts[{idx}].imap"),
            smtp=_endpoint(_dict(raw.get("smtp"), f"accounts[{idx}].smtp"), f"accounts[{idx}].smtp"),
            include_folders=_string_list(
                folders.get("include"), f"accounts[{idx}].folders.include", ["*"]
            ),
            exclude_folders=_string_list(
                folders.get("exclude"), f"accounts[{idx}].folders.exclude", []
            ),
        )
        if account_id in accounts:
            raise ValueError(f"重复 account_id: {account_id}")
        accounts[account_id] = account
    return accounts


def load_account(path: Path, account_id: str) -> MailAccount:
    accounts = load_accounts_config(path)
    if account_id not in accounts:
        raise KeyError(f"找不到 account_id={account_id}")
    return accounts[account_id]


def keychain_get_secret(
    credential_ref: str,
    *,
    service: str = KEYCHAIN_SERVICE,
    legacy_service: str | None = LEGACY_KEYCHAIN_SERVICE,
) -> str:
    for svc in [service, legacy_service]:
        if not svc:
            continue
        cmd = ["security", "find-generic-password", "-s", svc, "-a", credential_ref, "-w"]
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    raise RuntimeError(f"Keychain 读取失败: account={credential_ref}")
