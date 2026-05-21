from codex_mail_workbench.sync import sanitize_folder_name, should_sync_folder


def test_sanitize_folder_name_keeps_imap_folder_refs_stable() -> None:
    assert sanitize_folder_name("Sent Items") == "Sent_Items"
    assert sanitize_folder_name("Junk E-mail") == "Junk_E-mail"
    assert sanitize_folder_name("父/子").startswith("folder_")
    assert sanitize_folder_name("父/子") != sanitize_folder_name("父/女")


def test_should_sync_folder_honors_include_and_exclude() -> None:
    assert should_sync_folder("INBOX", ["*"], ["Archive"])
    assert not should_sync_folder("Archive", ["*"], ["Archive"])
    assert should_sync_folder("INBOX", ["INBOX"], [])
    assert not should_sync_folder("Sent Items", ["INBOX"], [])
