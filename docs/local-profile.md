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

## Private Agent Overlay

For personal mailbox assistance, keep private Agent-readable rules under
`local/`. These files are ignored by Git and should not be pushed to the public
repository.

Recommended layout:

```text
local/
  AGENTS.md
  profile.md
  accounts.yaml
  skills/
    personal-mail-assistant/
      SKILL.md
  policies/
    mailbox-triage.md
    journal-review-policy.md
    manuscript-status-policy.md
    reply-drafting-policy.md
  templates/
    decline-review.md
    manuscript-status-reply.md
    meeting-reply.md
  context/
    obsidian.md
    people.md
    projects.md
  notes/
    examples.md
```

The public repository provides the tool surface. The private overlay provides
judgment: which mail matters, what can be archived, when the user must reply,
what context to consult, and what draft style to use.

Use `local/AGENTS.md` as the private entry point for agents. A typical private
entry should tell the agent to read `local/profile.md`, `local/policies/`,
`local/context/`, and relevant templates before judging mail. The public skill
will only point to this overlay; it should not contain personal policy content.

One-shot prompts such as "check the last three days of mail" should be handled
as an agent workflow:

1. Read the private overlay instructions.
2. Run `codex-mail --json doctor` and `codex-mail --json accounts`.
3. Sync relevant accounts when freshness matters.
4. Search and read recent mail through `codex-mail`.
5. Apply private text policies to classify reminders, archive candidates, and
   draft candidates.
6. Return proposed actions with `storage_ref`, reason, confidence, and any
   required confirmation.

The default boundary is read-first. Archive, delete, send, or other mailbox
writes should require explicit user confirmation unless the private overlay
defines a narrow, reversible, auditable action surface and the user has enabled
it.

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
      credential_ref: work-imap
    smtp:
      host: smtp.example.com
      port: 465
      security: ssl
      username: user@example.com
      credential_ref: work-smtp
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

Use different `credential_ref` values for each account or credential. Existing
local profiles that still use `secret_ref` remain supported for compatibility.
If you are migrating from an older private Keychain service name, set
`CODEX_MAIL_LEGACY_KEYCHAIN_SERVICE=<service-name>` locally instead of editing
the public repository.

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
