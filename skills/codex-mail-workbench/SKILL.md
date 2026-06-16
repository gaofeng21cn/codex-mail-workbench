---
name: codex-mail-workbench
description: Use when Codex should inspect a user's local email workbench through the codex-mail CLI or codex-mail-mcp: local IMAP/SQLite search, reading messages by storage_ref, syncing configured accounts, or triaging mailbox state without relying on Apple Mail automation.
---

# Codex Mail Workbench

Use this skill for mailbox work backed by the local `codex-mail` CLI. Prefer
read-only inspection first. Treat account configuration and synced mail as
private local state.

## Start

Verify the command and state first:

```bash
command -v codex-mail
codex-mail --json doctor
codex-mail --json accounts
```

The default state directory is `~/.codex-mail-workbench`. A project or user may
set `CODEX_MAIL_HOME` to another private directory, such as `./local`.

Credentials belong in macOS Keychain under service `codex-mail-workbench`; do not
ask the user to paste mailbox passwords into chat, docs, or config snippets.
Treat `codex-mail --json accounts` as the current account truth. Do not assume
configured account ids from memory or examples.

## Safe Read Path

Use read-only commands first:

```bash
codex-mail --json accounts
codex-mail --json recent --account work --limit 20
codex-mail --json search "invoice" --account personal --limit 20
codex-mail --json read 'email-store://...'
```

For fresh mail, sync explicitly:

```bash
codex-mail --json sync --account work --mode incremental
```

If multiple accounts are configured, sync and report coverage per account. If an
account fails to sync, keep that account as a freshness gap and continue
read-only inspection for accounts with usable local data.

## Triage Pattern

Use this pattern when the user asks to review recent mailbox state:

1. Run `codex-mail --json doctor` and `codex-mail --json accounts`.
2. If freshness matters, run `codex-mail --json sync --account <account> --mode incremental`
   for each relevant configured account.
3. Read recent metadata:

```bash
codex-mail --json recent --account <account> --limit 20
```

4. Search locally before opening more message bodies:

```bash
codex-mail --json search "<sender, subject, project, or thread clue>" --account <account> --limit 10
```

5. Read selected messages by `storage_ref`:

```bash
codex-mail --json read 'email-store://...'
```

Return a compact summary grouped by account. Include the action needed, why it
matters, freshness gaps, and the best local identifier. Do not expose long
quoted email text.

## Safety

- Prefer `storage_ref` over Apple Mail message ids.
- Do not send, delete, archive, or move mail unless the user explicitly asks for that exact write.
- If a query needs broad historical context, search locally first; only sync when freshness matters.
- Use Apple Mail automation only as a fallback for UI-local behavior.
- Do not treat sync success as proof that every mailbox was reviewed; report
  per-account sync and read coverage.
