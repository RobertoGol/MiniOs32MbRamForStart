# -*- coding: utf-8 -*-
"""G1: host tests for SD shell/item manifest parsing and validation.

Run: python -X utf8 Python_compiler/verify_sd_manifest.py
"""

from __future__ import annotations

import os
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NATIVE = os.path.join(REPO, "CtOs", "native")
if NATIVE not in sys.path:
    sys.path.insert(0, NATIVE)

import sd_manifest  # noqa: E402


def make_check(fails):
    counts = {"ok": 0, "fail": 0}

    def check(name, cond):
        counts["ok" if cond else "fail"] += 1
        print(("  %-52s %s") % (name, "OK" if cond else "FAIL"))
        if not cond:
            fails.append(name)

    return check, counts


def expect_error(check, name, fn, contains):
    try:
        fn()
    except Exception as e:  # noqa: BLE001 - test expects validation error
        msg = str(e)
        ok = contains.lower() in msg.lower()
        check(name, ok)
        if not ok:
            print("    got: %s" % msg)
        return
    check(name, False)
    print("    got: <no error>")


def write_tmp(tmp, name, text):
    p = os.path.join(tmp, name)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return p


def main():
    fails = []
    check, counts = make_check(fails)
    tmp = tempfile.mkdtemp(prefix="ctos_sd_manifest_")

    shell_ok = """# shell manifest
format=ctos-shell-1
id=main-shell
name=Main Shell
version=1.0.0
min_ctos=0.9.0
payload=shell.ctos
entry=main
hash=sha256:%s
""" % ("a" * 64)

    item_ok = """format=ctos-item-1
id=game-001
type=game
name=Example Game
version=1.2.3
size=12345
installable=yes
content=content/game.pkg
"""

    shell = sd_manifest.validate_shell_manifest(
        sd_manifest.parse_manifest_text(shell_ok, "shell"), "shell")
    check("shell parses", shell.id == "main-shell")
    check("shell format", shell.format == "ctos-shell-1")
    check("shell hash", shell.hash.startswith("sha256:"))

    item = sd_manifest.validate_item_manifest(
        sd_manifest.parse_manifest_text(item_ok, "item"), "item")
    check("item parses", item.id == "game-001")
    check("item type", item.type == "game")
    check("item size", item.size == 12345)
    check("item installable bool", item.installable is True)

    sp = write_tmp(tmp, "shell.manifest", shell_ok)
    ip = write_tmp(tmp, "item.manifest", item_ok)
    check("load shell file", sd_manifest.load_shell_manifest(sp).payload == "shell.ctos")
    check("load item file", sd_manifest.load_item_manifest(ip).content == "content/game.pkg")

    spaced = "format = ctos-shell-1 \nid = s1\nname = N\nversion = 1\nmin_ctos = 1\npayload = shell.ctos\n"
    check("spaces around =", sd_manifest.validate_shell_manifest(sd_manifest.parse_manifest_text(spaced, "s")).id == "s1")
    expect_error(check, "duplicate key", lambda: sd_manifest.parse_manifest_text("id=a\nid=b\n", "d"), "duplicate key")
    expect_error(check, "unknown key", lambda: sd_manifest.validate_shell_manifest(sd_manifest.parse_manifest_text("format=ctos-shell-1\nid=a\nname=n\nversion=1\nmin_ctos=1\npayload=a.ctos\nextra=x\n", "u")), "unknown key")
    expect_error(check, "missing key", lambda: sd_manifest.validate_shell_manifest(sd_manifest.parse_manifest_text("format=ctos-shell-1\nid=a\nname=n\nversion=1\nmin_ctos=1\n", "m")), "missing required key")
    expect_error(check, "bad format", lambda: sd_manifest.validate_shell_manifest(sd_manifest.parse_manifest_text("format=ctos-shell-9\nid=a\nname=n\nversion=1\nmin_ctos=1\npayload=a.ctos\n", "f")), "unsupported format")
    expect_error(check, "bad id", lambda: sd_manifest.validate_shell_manifest(sd_manifest.parse_manifest_text("format=ctos-shell-1\nid=../bad\nname=n\nversion=1\nmin_ctos=1\npayload=a.ctos\n", "i")), "invalid id")
    expect_error(check, "bad payload absolute", lambda: sd_manifest.validate_shell_manifest(sd_manifest.parse_manifest_text("format=ctos-shell-1\nid=a\nname=n\nversion=1\nmin_ctos=1\npayload=/a.ctos\n", "p")), "invalid payload path")
    expect_error(check, "bad payload traversal", lambda: sd_manifest.validate_shell_manifest(sd_manifest.parse_manifest_text("format=ctos-shell-1\nid=a\nname=n\nversion=1\nmin_ctos=1\npayload=../a.ctos\n", "p")), "invalid payload path")
    expect_error(check, "bad payload backslash", lambda: sd_manifest.validate_shell_manifest(sd_manifest.parse_manifest_text("format=ctos-shell-1\nid=a\nname=n\nversion=1\nmin_ctos=1\npayload=a\\b.ctos\n", "p")), "invalid payload path")
    expect_error(check, "bad hash", lambda: sd_manifest.validate_shell_manifest(sd_manifest.parse_manifest_text("format=ctos-shell-1\nid=a\nname=n\nversion=1\nmin_ctos=1\npayload=a.ctos\nhash=md5:abc\n", "h")), "invalid hash")
    expect_error(check, "nul byte", lambda: sd_manifest.parse_manifest_text("id=a\x00b\n", "n"), "NUL")

    expect_error(check, "bad item type", lambda: sd_manifest.validate_item_manifest(sd_manifest.parse_manifest_text("format=ctos-item-1\nid=a\ntype=virus\nname=n\ncontent=c.bin\n", "t")), "invalid type")
    expect_error(check, "bad item size", lambda: sd_manifest.validate_item_manifest(sd_manifest.parse_manifest_text("format=ctos-item-1\nid=a\ntype=game\nname=n\ncontent=c.bin\nsize=-1\n", "s")), "invalid size")
    expect_error(check, "bad item bool", lambda: sd_manifest.validate_item_manifest(sd_manifest.parse_manifest_text("format=ctos-item-1\nid=a\ntype=game\nname=n\ncontent=c.bin\ninstallable=maybe\n", "b")), "invalid installable")
    expect_error(check, "bad item content", lambda: sd_manifest.validate_item_manifest(sd_manifest.parse_manifest_text("format=ctos-item-1\nid=a\ntype=game\nname=n\ncontent=/abs.bin\n", "c")), "invalid content path")

    total = counts["ok"] + counts["fail"]
    if fails:
        print("RESULT: FAIL %d/%d (%d failures)" % (counts["ok"], total, len(fails)))
        for f in fails:
            print(" - " + f)
        return 1
    print("RESULT: ALL OK %d/%d" % (counts["ok"], total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
