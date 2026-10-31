# ZIP-KPA — The Archive Whisperer
# Copyright (C) 2025 DEDSEC <https://github.com/Unknownx007>
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Visuals, banners, boxes, quotes — DEDSEC / ZIP-KPA"""
import random
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align

from .utils import console


# ---------- Banner ----------
def show_banner():
    border       = "bright_magenta"
    doc          = "bright_cyan"
    zipper       = "bold bright_white"
    dedsec_style = "bold bright_green"
    zipkpa_style = "bold bright_yellow"
    stars_style  = "bright_green"
    eq_style     = "bright_yellow"

    raw = """XXXXXXXXXXXXXX
XXXXXXXXXXXXXdo.
XXX          Y88.
XXX           `Y8pXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXX            'Y8b.                           XX
XXX              Y8b.                          XX
XXX               `88opXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXX                `YXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXX                       X                        XXX
XXX                     XXXXX                      XXX
XXX                       X                        XXX
XXX                     XXXXX                      XXX
XXX     ********          X         +=======+      XXX
XXX     *DEDSEC*         XXX        |ZIP-KPA|      XXX
 XX     ********        dd bb       +=======+      XXX
XX                      d| |b                      XXX
XXX                     qq pp                      XXX
XXX                     'q|p`                      XXX
XXX                      '"`                       XXX
XXX                                                XXX
XXXX                                               XXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
=================[ ZIP-KPA BY DEDSEC ]================""".split("\n")
    raw = [l.rstrip() for l in raw]
    max_w = max(len(l) for l in raw)
    raw = [l.ljust(max_w) for l in raw]

    # Order matters — longer tokens first so they aren't shadowed
    tokens = [
        ("`88op",     doc),
        ("`Y8p",      doc),
        ("'Y8b.",     doc),
        ("Y88.",      doc),
        ("Y8b.",      doc),
        ("`Y",        doc),
        ("do.",       doc),
        ("*DEDSEC*",  dedsec_style),
        ("|ZIP-KPA|", zipkpa_style),
        ("********",  stars_style),
        ("+=======+", eq_style),
        ("dd bb",     zipper),
        ("d| |b",     zipper),
        ("qq pp",     zipper),
        ("'q|p`",     zipper),
        ('\'"`',      zipper),
	("ZIP-KPA BY DEDSEC", dedsec_style),
    ]
    tokens.sort(key=lambda t: -len(t[0]))

    body = Text()
    for line_idx, line in enumerate(raw):
        if line_idx > 0:
            body.append("\n")
        i = 0
        while i < len(line):
            for tok, style in tokens:
                if line[i:i + len(tok)] == tok:
                    body.append(tok, style=style)
                    i += len(tok)
                    break
            else:
                body.append(line[i], style=border)
                i += 1

    console.print()
    console.print(Panel(
        Align.center(body),
        title="[bold bright_magenta]◆ ZIP-KPA ◆[/]",
        border_style="bright_magenta",
        padding=(1, 2),
    ))


# ---------- Menu ----------
def show_menu():
    table = Table(show_header=False, box=None, padding=(0, 2), expand=False)
    table.add_column(style="bright_cyan bold", width=4, justify="right")
    table.add_column(style="bright_white bold", width=34)
    table.add_column(style="dim")

    table.add_row(r"\[1]", "💀  Brute Force", "wordlist → ZIP")
    table.add_row(r"\[2]", "🧠  Known-Plaintext Attack", "ZipCrypto only")
    table.add_row(r"\[3]", "ℹ   About / Credits", "author info")
    table.add_row(r"\[0]", "🚪  Exit", "")

    console.print()
    console.print(Panel(table, border_style="bright_magenta", padding=(1, 2)))


# ---------- Cowsay quotes ----------
COWS = [
    "Brute force is just cardio for CPUs.",
    "Your password was 'password123'? Bold strategy, Cotton.",
    "ZipCrypto: because 1993 called and wanted its encryption back.",
    "AES-256 walks into a bar. Bartender: 'We don't serve your kind.'",
    "Known plaintext is the universe telling you to trust no one.",
    "12 bytes is all it takes. Story of every hacker's life.",
    "The password isn't the goal. The keys are. The password is a decoy.",
    "bkcrack doesn't break passwords. It breaks assumptions.",
    "Two bytes walk into a bar. The bartender says: 'You look XORed.'",
    "Forensics is just archaeology with shell access.",
    "32 bytes of plaintext? Better bring a coffee. Or ten.",
]


def print_quote():
    quote = random.choice(COWS)
    console.print()
    console.print(Panel(
        Align.center(f"[italic cyan]{quote}[/]"),
        border_style="dim magenta",
        padding=(0, 1),
    ))


# ---------- Boxes ----------
def print_success_box(title, lines):
    body = "\n".join(str(ln) for ln in lines)
    console.print()
    console.print(Panel(
        body,
        title=f"[bold green]✓  {title}[/]",
        border_style="green",
        title_align="left",
        padding=(0, 1),
    ))


def print_error_box(title, lines):
    body = "\n".join(str(ln) for ln in lines)
    console.print()
    console.print(Panel(
        body,
        title=f"[bold red]✗  {title}[/]",
        border_style="red",
        title_align="left",
        padding=(0, 1),
    ))


def print_info_box(title, lines):
    body = "\n".join(str(ln) for ln in lines)
    console.print()
    console.print(Panel(
        body,
        title=f"[bold cyan]ℹ  {title}[/]",
        border_style="cyan",
        title_align="left",
        padding=(0, 1),
    ))


def print_warning_box(title, lines):
    body = "\n".join(str(ln) for ln in lines)
    console.print()
    console.print(Panel(
        body,
        title=f"[bold yellow]⚠  {title}[/]",
        border_style="yellow",
        title_align="left",
        padding=(0, 1),
    ))


# ---------- Tables ----------
def entries_table(entries):
    table = Table(
        title="[bold bright_cyan]Encrypted entries in the ZIP[/]",
        title_justify="left",
        border_style="bright_magenta",
        show_lines=False,
    )
    table.add_column("#", style="bright_yellow bold", justify="right", width=3)
    table.add_column("Filename", style="white")
    table.add_column("Size", style="cyan", justify="right")
    table.add_column("Method", style="bright_magenta")

    for i, e in enumerate(entries, 1):
        method = (
            "STORED" if e.compress_type == 0
            else "DEFLATED" if e.compress_type == 8
            else f"METHOD {e.compress_type}"
        )
        table.add_row(
            str(i),
            Text(e.filename),
            f"{e.file_size:,} B",
            method,
        )
    console.print()
    console.print(table)


# ---------- About ----------
def show_about():
    from . import __version__, __author__, TOOL_NAME
    from .utils import clear, pause
    clear()
    show_banner()
    console.print()
    console.print(Panel(
        "\n".join([
            f"[bright_magenta]Tool      :[/] {TOOL_NAME} v{__version__}",
            f"[bright_magenta]Author    :[/] {__author__}",
            f"[bright_magenta]GitHub    :[/] [cyan underline]https://github.com/Unknownx007[/]",
            f"[bright_magenta]Purpose   :[/] ZIP password recovery — brute force + known-plaintext.",
            f"[bright_magenta]License   :[/] AGPLv3. For authorized testing, CTFs, and forensics only.",
            f"[bright_magenta]Deps      :[/] pyzipper (AES), rich (UI), bkcrack (KPA)",
        ]),
        title="[bold cyan]ℹ  About[/]",
        border_style="cyan",
        title_align="left",
        padding=(1, 2),
    ))
    print_quote()
    pause()
