# Architecture

## Layers

1. Protocol layer: IMAP/SMTP account config and Keychain secret lookup.
2. Store layer: SQLite table `email_messages`, keyed by `(account_id, folder_slug, uid)`.
3. CLI layer: `codex-mail doctor/accounts/sync/recent/search/read`.
4. MCP layer: read-only `mail_recent`, `mail_search`, `mail_read`.
5. Skill layer: future Codex threads use the CLI first, MCP when configured by the host app.

## Store Reference

Messages are addressed as:

```text
email-store://<account_id>/<folder_slug>/<uid>/<raw_sha256_prefix>
```

This is stable for local reads and safer than Mail.app numeric ids.

## Future Write Path

Writes should be added as narrow commands:

- `draft`
- `mark`
- `move`
- `archive`

Live `send` should require an explicit user request and should record a local sent ledger.

