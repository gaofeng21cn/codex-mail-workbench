# Codex Mail Workbench

本仓库是一个给 Codex 和其他 coding agent 使用的本地邮件工作台。

它把 IMAP 邮箱同步到本机 SQLite raw EML store，提供 read-first CLI，并可通过
MCP stdio server 暴露只读邮件查询工具。真实账号配置、邮件库、同步游标和个人
triage 规则不进入 Git，放在 ignored 的本地 profile 中。

## 适用场景

- 让 Codex 查询本地邮箱，而不是优先依赖 Apple Mail UI 自动化。
- 按账号、文件夹、发件人、主题、收件人、message id 或正文搜索本地邮件。
- 通过稳定的 `email-store://...` 引用读取选定邮件。
- 为 agent 邮件 triage 提供一个可复用、可发布、隐私边界清楚的工具层。

## 快速开始

安装本地命令：

```bash
git clone https://github.com/gaofeng21cn/codex-mail-workbench.git
cd codex-mail-workbench
make install-local
```

创建本地私有 profile：

```bash
mkdir -p local/sync-state
cp config/accounts.example.yaml local/accounts.yaml
```

编辑 `local/accounts.yaml`，写入真实账号元数据。密码或 app password 放入
macOS Keychain，不写进 YAML：

```bash
security add-generic-password -s codex-mail-workbench -a keychain.work.imap -w '<app-password>'
```

检查配置：

```bash
CODEX_MAIL_HOME=./local codex-mail --json doctor
CODEX_MAIL_HOME=./local codex-mail --json accounts
```

同步并读取：

```bash
CODEX_MAIL_HOME=./local codex-mail --json sync --account work --mode incremental
CODEX_MAIL_HOME=./local codex-mail --json recent --account work --limit 20
CODEX_MAIL_HOME=./local codex-mail --json recent --account work --since 2026-06-13T00:00:00+08:00 --until 2026-06-17T00:00:00+08:00 --limit 100
CODEX_MAIL_HOME=./local codex-mail --json search "invoice" --account work --limit 10
CODEX_MAIL_HOME=./local codex-mail --json read 'email-store://work/INBOX/12345/abcdef1234567890'
```

## 本地状态目录

默认状态目录：

```text
~/.codex-mail-workbench/
  accounts.yaml
  mail.sqlite
  mail.sqlite-shm
  mail.sqlite-wal
  sync-state/
```

开发时可以显式使用仓库内 ignored 的 `./local`：

```bash
CODEX_MAIL_HOME=./local
```

`local/` 中可以放真实 `accounts.yaml`、`profile.md`、邮件库和同步状态；这些内容
不应提交到公开仓库。

## CLI

```bash
codex-mail --json doctor
codex-mail --json accounts
codex-mail --json sync --account <account> --mode incremental
codex-mail --json recent --account <account> --limit 20
codex-mail --json recent --account <account> --since <start-iso> --until <end-iso> --limit 100
codex-mail --json search "<query>" --account <account> --limit 20
codex-mail --json search "<query>" --account <account> --since <start-iso> --until <end-iso> --limit 20
codex-mail --json read 'email-store://...'
```

当前默认只开放读取路径。发送、删除、归档、移动等写操作应作为单独、可审计、
需要明确用户请求的命令面再加入。

## MCP

```bash
CODEX_MAIL_HOME=./local codex-mail-mcp --db ./local/mail.sqlite
```

MCP 当前暴露：

- `mail_recent`
- `mail_search`
- `mail_read`

## 给 Agent 的使用方式

推荐流程：

1. 运行 `codex-mail --json doctor`。
2. 运行 `codex-mail --json accounts`，以输出作为当前账号真相。
3. 需要新鲜性时显式 sync。
4. 对“最近三天”等时间窗口，使用明确的 `--since` / `--until` ISO 边界。
5. 先搜索 metadata，再读取少量选定正文。
6. 用 `storage_ref` 读取邮件。
7. 汇报每个账号的覆盖范围和 freshness gap。

伴随 skill 位于
[`skills/codex-mail-workbench/SKILL.md`](skills/codex-mail-workbench/SKILL.md)，
UI discovery 元数据位于
[`skills/codex-mail-workbench/agents/openai.yaml`](skills/codex-mail-workbench/agents/openai.yaml)。

## 隐私边界

不要提交：

- 真实 `accounts.yaml`
- `local/profile.md`
- `mail.sqlite`、`mail.sqlite-shm`、`mail.sqlite-wal`
- `sync-state/`
- raw EML、MBOX、Maildir 导出、`.env`、密码或 app password
- 真实账号相关示例

更多本地 profile 说明见 [docs/local-profile.md](docs/local-profile.md)。

## 验证

```bash
python -m pytest
detect-secrets scan --all-files
```

发布前还应执行一次针对本机个人标识的 grep，确认公开树中没有本地隐私信息。
