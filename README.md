<p align="center">
  <strong>English</strong> | <a href="./README.zh-CN.md">中文</a>
</p>

<h1 align="center">Codex Mail Workbench</h1>

<p align="center"><strong>Local-first email workspace for Codex and other coding agents</strong></p>
<p align="center">IMAP Sync · SQLite Mail Store · Read-First CLI · MCP Tools</p>

<table>
  <tr>
    <td width="33%" valign="top">
      <strong>Primary Use</strong><br/>
      Let an agent inspect configured mailboxes without giving it direct access to a mail client UI or mailbox password
    </td>
    <td width="33%" valign="top">
      <strong>Interface</strong><br/>
      Python CLI plus a read-only MCP stdio server over a local SQLite raw EML store
    </td>
    <td width="33%" valign="top">
      <strong>Privacy Boundary</strong><br/>
      Real accounts, synced mail, sync cursors, and personal notes live outside tracked source in a private local profile
    </td>
  </tr>
</table>

> `codex-mail-workbench` is a generic local email workbench for agents. It keeps
> mailbox state on your machine, exposes small read-first commands, and makes
> private account configuration an explicit local profile instead of repository
> content.

## Product Position

Agents are useful for mailbox triage, thread lookup, and context recovery, but
they should not need a live mail client session or pasted mailbox credentials.
This repository provides the reusable tooling layer:

- configure IMAP/SMTP account metadata in a local YAML file;
- resolve credentials from macOS Keychain;
- sync selected IMAP folders into a private SQLite store;
- search and read stored messages through stable CLI commands;
- expose the same read-only surface through MCP for Codex-compatible hosts.

The repository is intentionally local-first. It does not ship mailbox content,
real account configuration, or personal triage rules.

## What It Helps You Do

- Give Codex a reliable way to answer "what is in this mailbox?" without using
  Apple Mail automation as the primary path.
- Search recent or historical local email by account, folder, sender, subject,
  recipient, message id, or body text.
- Read selected messages by stable `email-store://...` references.
- Keep agent workflows read-first until a deliberate write surface is added.
- Publish the tool as a normal GitHub repository without leaking local mail
  state.

## Quick Start

Install the local commands from a checkout:

```bash
git clone https://github.com/gaofeng21cn/codex-mail-workbench.git
cd codex-mail-workbench
make install-local
```

Create a private repo-local profile:

```bash
mkdir -p local/sync-state
cp config/accounts.example.yaml local/accounts.yaml
```

Edit `local/accounts.yaml` with your real account metadata. Keep passwords or
app passwords in macOS Keychain, using the `credential_ref` values from the YAML:

```bash
security add-generic-password -s codex-mail-workbench -a keychain.work.imap -w '<app-password>'
```

Check the local profile:

```bash
CODEX_MAIL_HOME=./local codex-mail --json doctor
CODEX_MAIL_HOME=./local codex-mail --json accounts
```

Sync and inspect mail:

```bash
CODEX_MAIL_HOME=./local codex-mail --json sync --account work --mode incremental
CODEX_MAIL_HOME=./local codex-mail --json recent --account work --limit 20
CODEX_MAIL_HOME=./local codex-mail --json recent --account work --since 2026-06-13T00:00:00+08:00 --until 2026-06-17T00:00:00+08:00 --limit 100
CODEX_MAIL_HOME=./local codex-mail --json search "invoice" --account work --limit 10
CODEX_MAIL_HOME=./local codex-mail --json read 'email-store://work/INBOX/12345/abcdef1234567890'
```

## Runtime Model

The default private state directory is:

```text
~/.codex-mail-workbench/
  accounts.yaml
  mail.sqlite
  mail.sqlite-shm
  mail.sqlite-wal
  sync-state/
```

For development inside a checkout, prefer:

```bash
CODEX_MAIL_HOME=./local
```

The tracked repository should contain only generic code, examples, docs, tests,
and skill instructions. `local/` is ignored and is the intended place for real
accounts, synced mail, sync cursors, and private notes.

## CLI Surface

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

The current read path is intentionally narrow. Live send, delete, archive, and
move operations are not exposed by default.

## MCP

Run the read-only MCP server against the local SQLite store:

```bash
CODEX_MAIL_HOME=./local codex-mail-mcp --db ./local/mail.sqlite
```

Available tools:

- `mail_recent`
- `mail_search`
- `mail_read`

## For Agents

Use the CLI or MCP server instead of scraping a mail client UI.

Recommended operating pattern:

1. Run `codex-mail --json doctor`.
2. Run `codex-mail --json accounts` and treat the result as current account
   truth.
3. Sync explicitly when freshness matters.
4. Use `--since` and `--until` for explicit date windows such as "last three
   days".
5. Search metadata before opening message bodies.
6. Read selected messages by `storage_ref`.
7. Report account coverage and freshness gaps.

The companion skill lives at
[`skills/codex-mail-workbench/SKILL.md`](skills/codex-mail-workbench/SKILL.md).

## Privacy Boundary

This repository is designed to be public-safe.

Do not commit:

- real `accounts.yaml`
- `local/profile.md`
- `mail.sqlite`, `mail.sqlite-shm`, or `mail.sqlite-wal`
- `sync-state/`
- raw EML, MBOX, Maildir exports, `.env` files, passwords, or app passwords
- real account-specific examples

See [Local Profile](docs/local-profile.md) for the private profile layout and
publication checklist.

## Documentation

- [Architecture](docs/architecture.md)
- [Local Profile](docs/local-profile.md)
- [Companion Skill](skills/codex-mail-workbench/SKILL.md)

## Technical Validation

```bash
python -m pytest
detect-secrets scan --all-files
```

Before publishing, also run a privacy grep for local identifiers that should not
leave your machine.
