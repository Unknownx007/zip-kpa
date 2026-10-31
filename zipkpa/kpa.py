# ZIP-KPA — The Archive Whisperer
# Copyright (C) 2025 DEDSEC <https://github.com/Unknownx007>
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Mode 2 — Known-Plaintext Attack — DEDSEC / ZIP-KPA"""
import os
import re
import time
import shutil
import zipfile
import tempfile
import threading
import subprocess
from pathlib import Path

from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text

from .utils import (
    console, clear, pause, detect_encryption,
    list_encrypted_entries, find_bkcrack, raw_deflate,
    expand_input_path, expand_output_path,
)
from .ui import (
    show_banner, print_success_box, print_error_box,
    print_warning_box, print_info_box, print_quote,
    entries_table,
)


KPA_INFO = """[yellow]
[1] The ZIP uses LEGACY ZipCrypto encryption.
    (Not AES-256. Not WinZip AES. Not macOS encrypt.)

[2] You already have a REFERENCE COPY of at least one file
    inside the ZIP (≥ 12 matching bytes).

[3] The tool re-compresses your reference to match the ZIP
    entry's compression method automatically.

[4] `bkcrack` must be installed (see GitHub release).

[dim]⏱  RUNTIME GUIDE[/]
    12 bytes  →  1–2 hours
    20 bytes  →  30 min – 2 hours
    32 bytes  →  5 – 30 minutes
    50 bytes  →  1 – 5 minutes
    100+ bytes →  seconds[/]
"""


def parse_bkcrack_keys(stdout):
    m = re.search(r"Keys:\s*([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})", stdout)
    if m:
        return [m.group(1).lower(), m.group(2).lower(), m.group(3).lower()]
    k0 = re.search(r"key0\s*[:=]\s*([0-9a-fA-F]{8})", stdout, re.I)
    k1 = re.search(r"key1\s*[:=]\s*([0-9a-fA-F]{8})", stdout, re.I)
    k2 = re.search(r"key2\s*[:=]\s*([0-9a-fA-F]{8})", stdout, re.I)
    if k0 and k1 and k2:
        return [k0.group(1).lower(), k1.group(1).lower(), k2.group(1).lower()]
    return None


def _run_bkcrack_streaming(cmd, timeout=3600):
    output_lines = []
    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1,
        )
    except FileNotFoundError:
        return "", None

    def _reader():
        try:
            for line in proc.stdout:
                output_lines.append(line)
        except Exception:
            pass

    threading.Thread(target=_reader, daemon=True).start()

    start = time.time()
    timed_out = False

    with Live(console=console, refresh_per_second=10, transient=True) as live:
        try:
            while proc.poll() is None:
                elapsed = int(time.time() - start)
                mm, ss = divmod(elapsed, 60)
                live.update(Spinner(
                    "dots12",
                    text=Text.from_markup(
                        f"[bright_cyan]bkcrack working[/]   "
                        f"[dim]elapsed[/] [bold white]{mm:02d}:{ss:02d}[/]   "
                        f"[dim](Ctrl+C to abort)[/]"
                    ),
                ))
                time.sleep(0.1)
                if elapsed > timeout:
                    proc.kill()
                    timed_out = True
                    break
        except KeyboardInterrupt:
            proc.kill()
            console.print("\n[yellow]  [!] Interrupted by user.[/]")
            return "", None

    if timed_out:
        print_warning_box("Timeout", [f"bkcrack exceeded {timeout}s"])
        return "".join(output_lines), None

    return "".join(output_lines), proc.returncode


def kpa_attack(zip_path, entry_name, reference_path):
    bkcrack = find_bkcrack()
    if not bkcrack:
        return {"ok": False, "reason": "bkcrack binary not found."}

    enc = detect_encryption(zip_path)
    if enc == "aes":
        return {"ok": False, "reason": "ZIP uses AES-256 — KPA is inapplicable."}
    if enc == "none":
        return {"ok": False, "reason": "ZIP is not encrypted."}
    if enc != "zipcrypto":
        return {"ok": False, "reason": f"Could not confirm ZipCrypto (got: {enc})."}

    with zipfile.ZipFile(zip_path) as zf:
        entries = {i.filename: i for i in zf.infolist() if i.flag_bits & 0x1}

    if entry_name not in entries:
        return {"ok": False, "reason": f"Entry '{entry_name}' not in ZIP."}

    info = entries[entry_name]
    method = info.compress_type

    try:
        ref_data = Path(reference_path).read_bytes()
    except Exception as e:
        return {"ok": False, "reason": f"Cannot read reference: {e}"}

    if len(ref_data) < 12:
        return {"ok": False, "reason": "Reference file has < 12 bytes."}

    if method == zipfile.ZIP_STORED:
        print_info_box("Plaintext prep", ["Entry is STORED — reference bytes used directly."])
        candidates = [("stored", ref_data)]
    elif method == zipfile.ZIP_DEFLATED:
        print_info_box("Plaintext prep",
                       ["Entry is DEFLATED — re-compressing at levels 9, 6, 1."])
        candidates = [(f"deflate-l{lvl}", raw_deflate(ref_data, lvl)) for lvl in (9, 6, 1)]
    else:
        return {"ok": False, "reason": f"Unsupported compression method: {method}"}

    tmpdir = tempfile.mkdtemp(prefix="zipkpa_")
    try:
        for label, pt_bytes in candidates:
            pt_file = os.path.join(tmpdir, f"plaintext_{label}.bin")
            Path(pt_file).write_bytes(pt_bytes)

            console.print(
                f"\n  [bright_cyan]➤[/] Trying [bold]{label}[/] "
                f"[dim]({len(pt_bytes)} bytes)[/]"
            )
            if len(pt_bytes) < 50:
                print_warning_box("Small plaintext", [
                    f"Only {len(pt_bytes)} bytes — this may take 5–30 minutes.",
                    "For fast recovery, use a reference file of 100+ bytes.",
                ])

            cmd = [bkcrack, "-C", zip_path, "-c", entry_name, "-p", pt_file]
            output, returncode = _run_bkcrack_streaming(cmd, timeout=3600)

            keys = parse_bkcrack_keys(output)
            if keys:
                print_success_box("Keys recovered", [f"[bold green]{'  '.join(keys)}[/]"])
                return {"ok": True, "keys": keys, "compression": label,
                        "entry": entry_name, "tmpdir": tmpdir}

            last = (output.strip().splitlines() or ["(no output)"])[-1][:100]
            console.print(f"[yellow]  [!] No keys from {label}: {last}[/]")

        return {"ok": False, "reason":
                ("bkcrack failed on all plaintext candidates. Your reference "
                 "likely does not match the encrypted stream, or a different "
                 "compression level was used. Try a larger reference file.")}
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def decrypt_entries(zip_path, keys, out_dir):
    bkcrack = find_bkcrack()
    if not bkcrack:
        return False, "bkcrack not found"
    out_dir = expand_output_path(out_dir)

    tmp_zip = os.path.join(
        tempfile.gettempdir(),
        f"zipkpa_dec_{os.getpid()}_{int(time.time())}.zip",
    )
    try:
        cmd = [bkcrack, "-C", zip_path, "-k", *keys, "-D", tmp_zip]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        combined = ((r.stdout or "") + "\n" + (r.stderr or "")).strip()
        if r.returncode != 0 or not os.path.isfile(tmp_zip):
            return False, f"bkcrack -D failed:\n{combined}"
        try:
            with zipfile.ZipFile(tmp_zip) as zf:
                zf.extractall(out_dir)
        except Exception as e:
            return False, f"Extraction failed: {e}"
        return True, f"Extracted to {out_dir}"
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        try:
            if os.path.isfile(tmp_zip):
                os.remove(tmp_zip)
        except Exception:
            pass


def run_menu():
    clear()
    show_banner()
    console.print()
    console.print(Panel(
        KPA_INFO,
        title="[bold yellow]⚠  Mode 2 — Known-Plaintext Attack[/]",
        border_style="yellow",
        title_align="left",
        padding=(1, 2),
    ))
    Prompt.ask("  [bold cyan]➤ Press ENTER once you've read the requirements[/]",
               default="", show_default=False)

    if not find_bkcrack():
        print_error_box("bkcrack not found", [
            "Download: github.com/kimci86/bkcrack/releases",
            "Place binary in PATH or next to run.py.",
        ])
        pause()
        return

    zip_raw = Prompt.ask("\n  [bold magenta]➤ Path to target .zip[/]")
    zip_path = expand_input_path(zip_raw)
    if not zip_path or not Path(zip_path).is_file():
        print_error_box("ZIP not found", [zip_raw or "(empty)"])
        pause()
        return

    if detect_encryption(zip_path) == "aes":
        print_error_box("AES-256 detected",
                        ["KPA does not work on AES-256.", "Use Mode 1 instead."])
        pause()
        return

    entries = list_encrypted_entries(zip_path)
    if not entries:
        print_warning_box("No encrypted entries",
                          ["Nothing to attack in this ZIP."])
        pause()
        return

    entries_table(entries)

    pick = Prompt.ask("\n  [bold magenta]➤ Select entry number[/]")
    try:
        idx = int(pick) - 1
        if idx < 0 or idx >= len(entries):
            raise ValueError
        entry_name = entries[idx].filename
    except Exception:
        print_error_box("Invalid selection", [pick or "(empty)"])
        pause()
        return

    ref_raw = Prompt.ask("  [bold magenta]➤ Path to reference file[/]")
    ref_path = expand_input_path(ref_raw)
    if not ref_path or not Path(ref_path).is_file():
        print_error_box("Reference not found", [ref_raw or "(empty)"])
        pause()
        return

    console.print("\n  [bright_cyan]➤[/] Firing bkcrack...")
    result = kpa_attack(zip_path, entry_name, ref_path)

    if result.get("ok"):
        print_success_box("KEYS RECOVERED", [
            f"[bright_magenta]key0 :[/] [bold white]{result['keys'][0]}[/]",
            f"[bright_magenta]key1 :[/] [bold white]{result['keys'][1]}[/]",
            f"[bright_magenta]key2 :[/] [bold white]{result['keys'][2]}[/]",
            "",
            f"[bright_magenta]Method :[/] {result['compression']}",
            f"[bright_magenta]Entry  :[/] {result['entry']}",
        ])
        if Confirm.ask("\n  [bold cyan]➤ Decrypt ALL entries now?[/]", default=False):
            out_raw = Prompt.ask(
                "  [bold magenta]➤ Output directory[/]",
                default="./unlocked",
            )
            out_dir = expand_output_path(out_raw or "./unlocked")
            ok, msg = decrypt_entries(zip_path, result["keys"], out_dir)
            if ok:
                print_success_box("DECRYPTED", [msg])
            else:
                print_error_box("Decryption failed", msg.split("\n"))
    else:
        print_error_box("KPA FAILED", [result.get("reason", "unknown")])

    print_quote()
    pause()
