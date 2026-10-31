# ZIP-KPA — The Archive Whisperer
# Copyright (C) 2025 DEDSEC <https://github.com/Unknownx007>
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Mode 1 — Brute Force — DEDSEC / ZIP-KPA"""
import zipfile
from pathlib import Path
from threading import Event, Lock
from concurrent.futures import ThreadPoolExecutor

from rich.prompt import Prompt
from rich.panel import Panel
from rich.progress import (
    Progress, SpinnerColumn, BarColumn, TextColumn,
    TimeElapsedColumn, MofNCompleteColumn,
)

try:
    import pyzipper
    HAS_PYZIPPER = True
except ImportError:
    HAS_PYZIPPER = False

from .utils import (
    console, clear, pause, detect_encryption, expand_input_path,
)
from .ui import (
    show_banner, print_success_box, print_error_box,
    print_warning_box, print_info_box, print_quote,
)


def _try_password(zip_path, entry_name, pw_bytes):
    try:
        with zipfile.ZipFile(zip_path) as zf:
            zf.read(entry_name, pwd=pw_bytes)
        return True
    except NotImplementedError:
        if HAS_PYZIPPER:
            try:
                with pyzipper.AESZipFile(zip_path) as zf:
                    zf.setpassword(pw_bytes)
                    zf.read(entry_name)
                return True
            except Exception:
                return False
        return False
    except Exception:
        return False


def brute_force(zip_path, wordlist_path):
    try:
        with zipfile.ZipFile(zip_path) as zf:
            enc_entries = [i for i in zf.infolist() if i.flag_bits & 0x1]
    except Exception as e:
        print_error_box("Cannot open ZIP", [str(e)])
        return None, 0, 0.0

    if not enc_entries:
        print_warning_box("Not encrypted", ["This ZIP has no password. Nothing to brute."])
        return None, 0, 0.0

    target = min(enc_entries, key=lambda i: i.file_size)
    enc_type = detect_encryption(zip_path)

    print_info_box("Target", [
        f"[bright_magenta]Entry :[/] {target.filename}",
        f"[bright_magenta]Size  :[/] {target.file_size:,} bytes",
        f"[bright_magenta]Crypt :[/] {enc_type.upper()}",
    ])

    if enc_type == "aes" and not HAS_PYZIPPER:
        print_error_box("AES detected — pyzipper missing",
                        ["Run: pip install pyzipper"])
        return None, 0, 0.0

    try:
        with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
            wordlist = [ln.rstrip("\r\n") for ln in f if ln.strip()]
    except Exception as e:
        print_error_box("Cannot read wordlist", [str(e)])
        return None, 0, 0.0

    if not wordlist:
        print_error_box("Empty wordlist", ["The file had no usable lines."])
        return None, 0, 0.0

    total = len(wordlist)
    console.print(f"\n  [dim]Loaded[/] [bold white]{total:,}[/] [dim]candidates[/]\n")

    found_event = Event()
    found_holder = []
    lock = Lock()
    attempts = [0]

    def worker(pw):
        if found_event.is_set():
            return
        attempts[0] += 1
        try:
            if _try_password(zip_path, target.filename,
                             pw.encode("utf-8", errors="ignore")):
                with lock:
                    if not found_event.is_set():
                        found_holder.append(pw)
                        found_event.set()
        except Exception:
            pass

    start = __import__("time").time()
    CHUNK = 2000

    progress = Progress(
        SpinnerColumn(style="bright_cyan"),
        TextColumn("[bold bright_cyan]Brute forcing[/]"),
        BarColumn(bar_width=36, style="dim cyan", complete_style="bright_cyan"),
        TextColumn("[bold white]{task.percentage:>3.1f}%[/]"),
        MofNCompleteColumn(),
        TextColumn("[dim]•[/]"),
        TextColumn("[bright_magenta]{task.fields[rate]}[/]"),
        TimeElapsedColumn(),
        console=console,
    )

    try:
        with progress:
            task = progress.add_task("", total=total, rate="0/s")
            for i in range(0, total, CHUNK):
                chunk = wordlist[i:i + CHUNK]
                with ThreadPoolExecutor(max_workers=16) as ex:
                    list(ex.map(worker, chunk))
                if found_event.is_set():
                    break

                elapsed = __import__("time").time() - start
                rate = attempts[0] / elapsed if elapsed > 0 else 0
                progress.update(
                    task,
                    completed=attempts[0],
                    rate=f"{rate:,.0f}/s",
                )
    except KeyboardInterrupt:
        console.print("\n[yellow]  [!] Interrupted by user.[/]")
        return None, attempts[0], __import__("time").time() - start

    elapsed = __import__("time").time() - start
    return (found_holder[0] if found_holder else None), attempts[0], elapsed


def run_menu():
    clear()
    show_banner()
    console.print()
    console.print(Panel(
        "[white]Guess passwords from a wordlist.[/]\n"
        "[dim]No reference file needed. Large wordlists take time.[/]",
        title="[bold yellow]💀  Mode 1 — Brute Force[/]",
        border_style="yellow",
        title_align="left",
        padding=(0, 2),
    ))

    wordlist_raw = Prompt.ask("\n  [bold magenta]➤ Path to wordlist[/]")
    wordlist = expand_input_path(wordlist_raw)
    if not wordlist or not Path(wordlist).is_file():
        print_error_box("Wordlist not found", [wordlist_raw or "(empty)"])
        pause()
        return

    zip_raw = Prompt.ask("  [bold magenta]➤ Path to .zip file[/]")
    zip_path = expand_input_path(zip_raw)
    if not zip_path or not Path(zip_path).is_file():
        print_error_box("ZIP not found", [zip_raw or "(empty)"])
        pause()
        return

    pw, attempts, elapsed = brute_force(zip_path, wordlist)

    if pw:
        print_success_box("PASSWORD FOUND", [
            f"[bold green]➤ {pw}[/]",
            "",
            f"[bright_magenta]Tested :[/] {attempts:,} attempts",
            f"[bright_magenta]Time   :[/] {elapsed:.2f}s",
        ])
    else:
        print_error_box("PASSWORD NOT FOUND", [
            f"[bright_magenta]Tested :[/] {attempts:,} attempts",
            "",
            "Try a bigger wordlist, or switch to Mode 2 (KPA).",
        ])

    print_quote()
    pause()
