# Local Profile

This project is designed to keep reusable code public and mailbox-specific
state private. Use a local profile directory for real accounts, synced mail, and
user preferences.

## Directory Layout

The default private state directory is:

```text
~/.codex-mail-workbench/
  accounts.yaml
  profile.md
  mail.sqlite
  mail.sqlite-shm
  mail.sqlite-wal
  sync-state/
```

For development inside a checkout, use `./local` explicitly:

```bash
mkdir -p local/sync-state
export CODEX_MAIL_HOME=./local
codex-mail --json doctor
```

With `CODEX_MAIL_HOME=./local`, the workbench reads:

```text
local/accounts.yaml
local/mail.sqlite
local/sync-state/
```

`profile.md` is optional. It is for human-readable local notes such as preferred
triage categories, important senders, or response conventions. The current CLI
does not require it.

## accounts.yaml

Create `local/accounts.yaml` with placeholder-free local account ids. Account ids
should be stable labels such as `work` or `personal`; they do not need to expose
the real email address.

```yaml
accounts:
  - account_id: work
    email: user@example.com
    imap:
      host: imap.example.com
      port: 993
      security: ssl
      username: user@example.com
      secret_ref: work-imap
    smtp:
      host: smtp.example.com
      port: 465
      security: ssl
      username: user@example.com
      secret_ref: work-smtp
    folders:
      include:
        - INBOX
      exclude: []
```

Store passwords or app passwords in macOS Keychain under service
`codex-mail-workbench`; do not place secrets in YAML:

```bash
security add-generic-password -s codex-mail-workbench -a work-imap -w '<app-password>'
security add-generic-password -s codex-mail-workbench -a work-smtp -w '<app-password>'
```

Use different `secret_ref` values for each account or credential.

## Initialize State

After creating `accounts.yaml`, check the configuration:

```bash
CODEX_MAIL_HOME=./local codex-mail --json doctor
CODEX_MAIL_HOME=./local codex-mail --json accounts
```

Then run an explicit sync for each account:

```bash
CODEX_MAIL_HOME=./local codex-mail --json sync --account work --mode incremental
```

The sync command creates or updates:

- `local/mail.sqlite`
- `local/mail.sqlite-shm`
- `local/mail.sqlite-wal`
- `local/sync-state/<account_id>.json`

## Publication Checklist

Before publishing, committing, or opening a pull request, verify that the local
profile is not staged:

```bash
git status --short
git ls-files local
```

Do not commit:

- `local/accounts.yaml`
- `local/profile.md`
- `local/mail.sqlite`
- `local/mail.sqlite-shm`
- `local/mail.sqlite-wal`
- `local/sync-state/`
- any copied mailbox export, raw EML, credentials, app passwords, or real
  account-specific examples

The public repository should contain generic docs and examples only. Keep real
mailbox state in ignored local files or in another private path selected by
`CODEX_MAIL_HOME`.
