from pathlib import Path

from codex_mail_workbench.config import load_accounts_config


def test_load_accounts_config_parses_yaml(tmp_path: Path) -> None:
    config = tmp_path / "accounts.yaml"
    config.write_text(
        """
version: 1
accounts:
  - account_id: sysu
    email: gaof57@mail.sysu.edu.cn
    imap:
      host: mail.sysu.edu.cn
      port: 993
      security: ssl
      username: gaof57@mail.sysu.edu.cn
      secret_ref: dt.mail.gaof57_sysu.imap.password
    smtp:
      host: mail.sysu.edu.cn
      port: 465
      security: ssl
      username: gaof57@mail.sysu.edu.cn
      secret_ref: dt.mail.gaof57_sysu.smtp.password
    folders:
      include: ["*"]
      exclude: ["Archive"]
""".strip(),
        encoding="utf-8",
    )

    accounts = load_accounts_config(config)

    assert list(accounts) == ["sysu"]
    assert accounts["sysu"].imap.host == "mail.sysu.edu.cn"
    assert accounts["sysu"].smtp.port == 465
    assert accounts["sysu"].include_folders == ["*"]
    assert accounts["sysu"].exclude_folders == ["Archive"]

