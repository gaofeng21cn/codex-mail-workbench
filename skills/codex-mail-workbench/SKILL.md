---
name: codex-mail-workbench
description: Use when Codex should manage the user's local email workbench through the codex-mail CLI or codex-mail-mcp, especially for SYSU mail, local IMAP/SQLite search, reading messages by storage_ref, syncing mail, or triaging mailbox state without relying on Apple Mail automation.
---

# Codex Mail Workbench

Use this skill for mailbox work backed by the local `codex-mail` CLI.

## Start

Verify the command and state first:

```bash
command -v codex-mail
codex-mail --json doctor
```

The normal state directory is `~/.codex-mail-workbench`. Credentials are in macOS Keychain. The CLI can read old `digital-twin-mail` secrets while the new service is being adopted.

## Safe Read Path

Use read-only commands first:

```bash
codex-mail --json accounts
codex-mail --json recent --account gaof57_sysu --limit 20
codex-mail --json search "关键词" --account gaof57_sysu --limit 20
codex-mail --json read 'email-store://...'
```

For fresh mail, sync explicitly:

```bash
codex-mail --json sync --account gaof57_sysu --mode incremental
```

## Safety

- Prefer `storage_ref` over Apple Mail message ids.
- Do not send, delete, archive, or move mail unless the user explicitly asks for that exact write.
- If a query needs broad historical context, search locally first; only sync when freshness matters.
- Use Apple Mail automation only as a fallback for UI-local behavior.

