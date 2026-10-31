# ZIP-KPA — The Archive Whisperer
# Copyright (C) 2025 DEDSEC <https://github.com/Unknownx007>
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Shared helpers — DEDSEC / ZIP-KPA"""
import os
import sys
import zlib
import shutil
import zipfile
from pathlib import Path

from rich.console import Console

console = Console(highlight=False, force_terminal=True)


def clear():
    console.clear()


def pause(msg="Press ENTER to return to menu..."):
    console.print()
    try:
        console.input(f"[bold cyan]  ➤ {msg}[/]")
    except (KeyboardInterrupt, EOFError):
        pass


def safe_exit(code=0):
    console.print()
    console.print("[bold magenta]  [ DEDSEC ][/] [dim]Leaving quietly. No logs, no noise.[/]")
    sys.exit(code)


# ---------- Path helpers ----------
def expand_input_path(p: str) -> str:
    if not p:
        return p
    p = p.strip().strip('"').strip("'")
    return os.path.expanduser(p)


def expand_output_path(p: str) -> str:
    if not p:
        return p
    p = p.strip().strip('"').strip("'")
    p = os.path.abspath(os.path.expanduser(p))
    os.makedirs(p, exist_ok=True)
    return p


# ---------- ZIP inspection ----------
def detect_encryption(zip_path):
    try:
        with zipfile.ZipFile(zip_path) as zf:
            for info in zf.infolist():
                if not (info.flag_bits & 0x1):
                    continue
                if info.compress_type == 99:
                    return "aes"
                extra = info.extra or b""
                i = 0
                while i + 4 <= len(extra):
                    hid = int.from_bytes(extra[i:i+2], "little")
                    size = int.from_bytes(extra[i+2:i+4], "little")
                    if hid == 0x9901:
                        return "aes"
                    i += 4 + size
                return "zipcrypto"
            return "none"
    except Exception:
        return "unknown"


def list_encrypted_entries(zip_path):
    try:
        with zipfile.ZipFile(zip_path) as zf:
            return [i for i in zf.infolist() if i.flag_bits & 0x1]
    except Exception:
        return []


def find_bkcrack():
    for name in ("bkcrack", "bkcrack.exe"):
        w = shutil.which(name)
        if w:
            return w
    here = Path(__file__).resolve().parent.parent
    for c in [
        here / "bkcrack", here / "bkcrack.exe",
        here / "bin" / "bkcrack", here / "bin" / "bkcrack.exe",
        Path.cwd() / "bkcrack", Path.cwd() / "bkcrack.exe",
    ]:
        if c.is_file():
            return str(c)
    return None


def raw_deflate(data: bytes, level: int = 9) -> bytes:
    co = zlib.compressobj(level, zlib.DEFLATED, -15)
    return co.compress(data) + co.flush()
