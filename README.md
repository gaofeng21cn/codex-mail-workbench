# Codex Mail Workbench

Codex Mail Workbench is a local mail workspace for Codex. It syncs IMAP
mailboxes into a private SQLite store, exposes a small read-first CLI, and can
serve the same local store to Codex through an MCP stdio server.

The public repository contains the reusable workbench code, documentation, and
examples. Real account configuration, mailbox content, sync state, and user
profile notes belong in an ignored local profile directory or in the directory
selected by `CODEX_MAIL_HOME`.

## Capabilities

- Sync selected IMAP folders into a local SQLite raw EML store.
- List, search, and read locally stored messages through `codex-mail`.
- Serve read-only MCP tools: `mail_recent`, `mail_search`, and `mail_read`.
- Provide a companion Codex skill for safe mailbox inspection.
- Keep credentials in macOS Keychain under service `codex-mail-workbench`.

## Install

```bash
make install-local
codex-mail --json doctor
```

The default state directory is:

```text
~/.codex-mail-workbench/
  accounts.yaml
  mail.sqlite
  sync-state/
```

For a repo-local private profile during development, point the workbench at
`./local`:

```bash
mkdir -p local/sync-state
CODEX_MAIL_HOME=./local codex-mail --json doctor
```

See [docs/local-profile.md](docs/local-profile.md) for the expected local file
layout and publication checklist.

## CLI Examples

```bash
CODEX_MAIL_HOME=./local codex-mail --json doctor
codex-mail --json accounts
codex-mail --json sync --account work --mode incremental
codex-mail --json recent --account work --limit 20
codex-mail --json search "invoice" --account personal --limit 20
codex-mail --json read 'email-store://work/INBOX/12345/abcdef1234567890'
```

## MCP

```bash
CODEX_MAIL_HOME=./local codex-mail-mcp --db ./local/mail.sqlite
```

The MCP server exposes read-only tools for Codex mailbox lookup. Sending,
deleting, archiving, or moving mail should only be added through explicit,
auditable commands with user approval.

## Privacy Boundary

- Commit only generic code, documentation, and examples.
- Do not commit real `accounts.yaml`, `profile.md`, `mail.sqlite`,
  `mail.sqlite-*`, or `sync-state/` files.
- Store mailbox passwords or app passwords in Keychain, not in YAML or docs.
- Prefer local `storage_ref` values over Apple Mail private ids.
- Keep the default workflow read-first. Live write operations require a
  deliberate command surface and an explicit user request.
