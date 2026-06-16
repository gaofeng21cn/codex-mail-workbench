from pathlib import Path

from codex_mail_workbench.config import load_accounts_config


def test_load_accounts_config_parses_yaml(tmp_path: Path) -> None:
    config = tmp_path / "accounts.yaml"
    config.write_text(
        """
version: 1
accounts:
  - account_id: work
    email: work@example.com
    imap:
      host: imap.example.com
      port: 993
      security: ssl
      username: work@example.com
      credential_ref: keychain.work.imap
    smtp:
      host: smtp.example.com
      port: 465
      security: ssl
      username: work@example.com
      credential_ref: keychain.work.smtp
    folders:
      include: ["*"]
      exclude: ["Archive"]
""".strip(),
        encoding="utf-8",
    )

    accounts = load_accounts_config(config)

    assert list(accounts) == ["work"]
    assert accounts["work"].imap.host == "imap.example.com"
    assert accounts["work"].imap.credential_ref == "keychain.work.imap"
    assert accounts["work"].smtp.port == 465
    assert accounts["work"].include_folders == ["*"]
    assert accounts["work"].exclude_folders == ["Archive"]


def test_load_accounts_config_accepts_legacy_secret_ref(tmp_path: Path) -> None:
    config = tmp_path / "accounts.yaml"
    legacy_key = "secret" + "_ref"
    config.write_text(
        f"""
version: 1
accounts:
  - account_id: work
    email: work@example.com
    imap:
      host: imap.example.com
      port: 993
      security: ssl
      username: work@example.com
      {legacy_key}: legacy-work-imap
    smtp:
      host: smtp.example.com
      port: 465
      security: ssl
      username: work@example.com
      {legacy_key}: legacy-work-smtp
    folders:
      include: ["*"]
      exclude: []
""".strip(),
        encoding="utf-8",
    )

    accounts = load_accounts_config(config)

    assert accounts["work"].imap.credential_ref == "legacy-work-imap"
    assert accounts["work"].smtp.credential_ref == "legacy-work-smtp"
