PYTHON ?= python3
PREFIX ?= $(HOME)/.local
BIN_DIR := $(PREFIX)/bin
ROOT := $(CURDIR)

.PHONY: test install-local migrate-mail-store

test:
	$(PYTHON) -m pytest -q

install-local:
	mkdir -p "$(BIN_DIR)"
	printf '%s\n' '#!/usr/bin/env bash' 'PYTHONPATH="$(ROOT)/src" exec "$(PYTHON)" -m codex_mail_workbench.cli "$$@"' > "$(BIN_DIR)/codex-mail"
	printf '%s\n' '#!/usr/bin/env bash' 'PYTHONPATH="$(ROOT)/src" exec "$(PYTHON)" -m codex_mail_workbench.mcp_server "$$@"' > "$(BIN_DIR)/codex-mail-mcp"
	chmod +x "$(BIN_DIR)/codex-mail" "$(BIN_DIR)/codex-mail-mcp"

migrate-mail-store:
	bash scripts/migrate-mail-store.sh
