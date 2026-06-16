# Architecture

Codex Mail Workbench separates reusable mail tooling from private local state.
The public repository should describe and ship the generic workbench. A user's
real mail accounts, local database, sync cursors, and personal operating notes
stay outside the public source tree, normally in `./local` during development or
in another directory selected with `CODEX_MAIL_HOME`.

## Layers

1. Configuration layer: account metadata from `accounts.yaml`, with secrets
   resolved from macOS Keychain service `codex-mail-workbench`.
2. Protocol layer: IMAP sync using the configured account endpoints and folder
   include/exclude rules.
3. Store layer: SQLite table `email_messages`, keyed by
   `(account_id, folder_slug, uid)`, with raw EML retained locally.
4. CLI layer: `codex-mail doctor/accounts/sync/recent/search/read`.
5. MCP layer: read-only `mail_recent`, `mail_search`, and `mail_read`.
6. Skill layer: Codex uses the CLI first and the MCP server when the host app
   configures it.

## Store Reference

Messages are addressed as:

```text
email-store://<account_id>/<folder_slug>/<uid>/<raw_sha256_prefix>
```

This is stable for local reads and safer than Mail.app numeric ids.

## Public and Private Boundary

Public repository contents:

- reusable Python package under `src/`;
- tests for reusable behavior;
- documentation and generic examples;
- Codex skill instructions that use placeholder account ids such as `work` and
  `personal`.

Private local profile contents:

- `accounts.yaml` with real account ids, email addresses, IMAP/SMTP hosts,
  folder filters, usernames, and Keychain secret references;
- `profile.md` with the user's mailbox triage preferences or response style;
- `sync-state/` JSON files with per-account IMAP sync cursors;
- `mail.sqlite`, `mail.sqlite-shm`, and `mail.sqlite-wal` with synced message
  metadata and raw EML content.

The normal default state directory is `~/.codex-mail-workbench`. For a repo-local
private profile, run commands with `CODEX_MAIL_HOME=./local`. The repository
contract is that `local/` is private working state and must not be published.

## Future Write Path

Writes should be added as narrow commands:

- `draft`
- `mark`
- `move`
- `archive`

Live `send` should require an explicit user request and should record a local sent ledger.
