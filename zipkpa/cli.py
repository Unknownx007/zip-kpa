# ZIP-KPA — The Archive Whisperer
# Copyright (C) 2025 DEDSEC <https://github.com/Unknownx007>
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Main menu loop — DEDSEC / ZIP-KPA"""
import time
from .utils import console, clear, safe_exit
from .ui import show_banner, show_menu, show_about
from . import brute, kpa


def main_menu():
    while True:
        clear()
        show_banner()
        show_menu()

        choice = console.input(
            "\n  [bold magenta]➤[/] [dim]dedsec@zipkpa[/][bright_cyan]:~$[/] "
        ).strip()

        if choice == "1":
            brute.run_menu()
        elif choice == "2":
            kpa.run_menu()
        elif choice == "3":
            show_about()
        elif choice == "0":
            safe_exit()
        else:
            console.print(f"[red]  [-] Invalid option: {choice}[/]")
            time.sleep(1)


def main():
    try:
        main_menu()
    except KeyboardInterrupt:
        safe_exit(0)
