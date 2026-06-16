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
      secret_ref: mail.work.imap.password
    smtp:
      host: smtp.example.com
      port: 465
      security: ssl
      username: work@example.com
      secret_ref: mail.work.smtp.password
    folders:
      include: ["*"]
      exclude: ["Archive"]
""".strip(),
        encoding="utf-8",
    )

    accounts = load_accounts_config(config)

    assert list(accounts) == ["work"]
    assert accounts["work"].imap.host == "imap.example.com"
    assert accounts["work"].smtp.port == 465
    assert accounts["work"].include_folders == ["*"]
    assert accounts["work"].exclude_folders == ["Archive"]

