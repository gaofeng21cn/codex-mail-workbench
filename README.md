# Codex Mail Workbench

独立邮件工作台，用于让 Codex 管理本机邮箱。它从旧数字分身项目抽出邮件协议层和本地库，不承接旧项目的知识资产化主线。

## 当前能力

- IMAP 同步到本地 SQLite raw EML store
- 本地 `recent/search/read` CLI
- 最小 MCP stdio server：`mail_recent`、`mail_search`、`mail_read`
- Codex companion skill
- 默认复用旧 `digital-twin-mail` Keychain 凭据，也支持新 service `codex-mail-workbench`

## 安装

```bash
make install-local
make migrate-from-digital-twin
codex-mail --json doctor
```

默认状态目录：

```text
~/.codex-mail-workbench/
  accounts.yaml
  mail.sqlite
  sync-state/
```

可用 `CODEX_MAIL_HOME` 指向其他状态目录。

## 常用命令

```bash
codex-mail --json accounts
codex-mail --json recent --account gaof57_sysu --limit 20
codex-mail --json search "Research稿件初审" --account gaof57_sysu --limit 20
codex-mail --json read 'email-store://gaof57_sysu/INBOX/1555475851/1d005c36d3391e4b'
codex-mail --json sync --account gaof57_sysu --mode incremental
```

## MCP

```bash
codex-mail-mcp --db ~/.codex-mail-workbench/mail.sqlite
```

当前 MCP 暴露只读工具，适合 Codex 查询邮件。写操作和发信需要单独加审批/草稿流程后再开放。

## 边界

- 不再依赖旧数字分身 repo 作为运行位置。
- 不直接读 Apple Mail 私有数据库。
- 旧 Apple Mail skill 保留为本机 UI fallback。
- 首版不开放 live send/delete/move，避免误操作。

