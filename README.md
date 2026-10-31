<div align="center">

<img width="918" height="449" alt="0" src="https://github.com/user-attachments/assets/ab86093e-da90-4c6b-8ba7-1aaa1cd7f4be" />

# ZIP-KPA — The Archive Whisperer

**Dual-mode ZIP password recovery toolkit**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)]()
[![Author](https://img.shields.io/badge/author-DEDSEC-brightgreen.svg)](https://github.com/Unknownx007)

*Brute-Force · Known-Plaintext · ZipCrypto & AES*

</div>

---

## 🧠 What is this?

**ZIP-KPA** is a Python CLI toolkit that recovers passwords from ZIP archives using **two independent attack modes**:

| Mode | Method | Works On |
|------|--------|----------|
| **1** | **Brute Force** — try every password in a wordlist | ZipCrypto **and** AES-256 |
| **2** | **Known-Plaintext Attack (KPA)** — recover internal keys from a known reference file | ZipCrypto **only** |

Mode 2 is a **Biham–Kocher attack** wrapped around [`bkcrack`](https://github.com/kimci86/bkcrack): if you already have a copy of *any* file inside the encrypted ZIP, it can recover the encryption keys **without ever guessing the password**.

> ⚠️ **Mode 2 will NOT work on AES-256 ZIPs.** That's a mathematical limitation, not a bug. AES is not vulnerable to the Biham–Kocher attack.

---

## ✨ Features

- 🎯 **Two attack modes** in one tool — brute force + KPA
- ⚡ **Multi-threaded brute force** with 16 workers and live progress bars
- 🔑 **Key recovery** from a reference file (≥12 bytes) without password guessing
- 🧬 **Auto re-compression** — the tool tries STORED, DEFLATE levels 9/6/1 to match the encrypted stream
- 🔒 **AES support** in brute-force mode (via `pyzipper`)
- 🎨 **Rich UI** — colored banners, tables, spinners, progress bars
- 🐄 **Cowsay wisdom** between menus (because why not)
- 🌍 **Cross-platform** — Windows, Linux, macOS (x86_64 + ARM64)
- 🛡️ **Graceful failures** — detects AES, missing `bkcrack`, malformed paths, empty wordlists

---

## 📦 Installation

### 🐧 Linux 

```bash
git clone https://github.com/Unknownx007/zip-kpa.git
cd zip-kpa
python3 run.py
```


## 🚀 Usage

```bash
python3 run.py
```

### Mode 1 — Brute Force

1. Select **`[1]`**
2. Enter path to your wordlist (e.g. `wordlists/rockyou.txt`)
3. Enter path to the target `.zip`
4. Watch the progress bar
5. Password (if found) is displayed in a green box

```
╔══════════════════════════════════════════════════╗
║  ✓  PASSWORD FOUND                               ║
╠══════════════════════════════════════════════════╣
║ ➤ password123                                    ║
║                                                  ║
║ Tested : 2,847,391 attempts                      ║
║ Time   : 43.21s                                  ║
╚══════════════════════════════════════════════════╝
```

### Mode 2 — Known-Plaintext Attack

1. Select **`[2]`**
2. Read the requirements panel (ZipCrypto only, ≥12 bytes reference)
3. Enter target `.zip` path
4. Pick which encrypted entry to attack
5. Enter path to your **reference file** (a copy of a file inside the ZIP)
6. Wait for `bkcrack` to recover the keys
7. Choose to decrypt all entries to a folder

```
╔══════════════════════════════════════════════════╗
║  ✓  KEYS RECOVERED                               ║
╠══════════════════════════════════════════════════╣
║ key0 : 34653ad1                                  ║
║ key1 : d67a03fd                                  ║
║ key2 : 014c37c9                                  ║
║                                                  ║
║ Method : deflate-l9                              ║
║ Entry  : secret.txt                              ║
╚══════════════════════════════════════════════════╝
```

---

## 🔬 How the KPA works (short version)

ZipCrypto is a legacy stream cipher. If an attacker knows **any 12+ consecutive bytes** of the *plaintext stream* (which is the compressed output, not the raw file), they can solve a system of equations over the internal state and recover the three 32-bit keys `key0`, `key1`, `key2`. Those keys are sufficient to decrypt the entire archive — the original password is never needed.

`bkcrack` does the math. **ZIP-KPA** automates the pipeline:

1. Detects the ZIP encryption type (refuses AES)
2. Extracts the ciphertext of the target entry
3. Prepares the plaintext based on STORED / DEFLATED
4. Calls `bkcrack` with the right arguments
5. Parses the keys from the output
6. Creates an unlocked copy of the archive

### ⏱ Runtime depends on plaintext size

| Plaintext size | Typical runtime |
|---|---|
| 12 bytes | 1–2 hours |
| 20 bytes | 30 min – 2 hours |
| 32 bytes | 5 – 30 minutes |
| 50 bytes | 1 – 5 minutes |
| **100+ bytes** | **seconds** |

**Use a reference file of 100+ bytes** if you want fast results.

---

## 📋 Requirements for Mode 2 (checklist)

KPA works **only when ALL of these are true**:

- [x] The ZIP uses **legacy ZipCrypto** encryption
- [x] You have a **reference copy** of at least one file inside the ZIP
- [x] The reference has **≥ 12 matching bytes** with the encrypted stream
- [x] `bkcrack` binary is installed and executable

If **any** of these is false → KPA cannot work. That's not a bug, it's the math.

---

## 📖 Examples

### CTF challenge

```bash
# You have flag.zip and known.txt (which is inside the ZIP)
python3 run.py
# → [2]
# → flag.zip
# → entry 1 (known.txt)
# → reference: known.txt
# → keys recovered → decrypt → flag extracted
```

### Forensic recovery of a legacy backup

```bash
# You have backup_2012.zip (ZipCrypto) and copy of config.ini
# that was known to be inside
python3 run.py
# → [2]
# → backup_2012.zip
# → entry N (config.ini)
# → reference: config.ini (100+ bytes for fast recovery)
# → keys recovered → decrypt → full archive extracted
```

### Brute force a modern AES ZIP

```bash
# You have secret.zip (AES) and rockyou.txt
python3 run.py
# → [1]
# → rockyou.txt
# → secret.zip
# → progress bar → password found
```

---

## 📁 Project structure

```
zip-kpa/
├── README.md
├── LICENSE
├── requirements.txt
├── install.sh
├── install.bat
├── run.py
├── .gitignore
├── zipkpa/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── ui.py
│   ├── utils.py
│   ├── brute.py
│   └── kpa.py
└── wordlists/
    └── README.md
```

---

## 📝 Wordlists

Drop your wordlists in `wordlists/`. Recommended:

- [rockyou.txt](https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt) — 14M passwords
- [SecLists](https://github.com/danielmiessler/SecLists) — comprehensive collections
- [CrackStation](https://crackstation.net/crackstation-wordlist-password-cracking-dictionary.htm) — 1.5B candidates

Quick test wordlist:

```bash
printf 'password\n123456\nadmin\nletmein\nzipkpa\n' > wordlists/test.txt
```

---

## ⚠️ Legal & ethical notice

This tool is intended **only** for:

- ✅ CTF challenges and labs you own
- ✅ Digital forensics on archives you are **explicitly authorized** to examine
- ✅ Security audits under written permission
- ✅ Educational study of legacy cryptography

**Do not** use this tool against archives you do not own or do not have written authorization to test. Unauthorized use may violate laws in your jurisdiction (Computer Fraud and Abuse Act in the US, Computer Misuse Act in the UK, similar laws everywhere).

The author is **not responsible** for any misuse.

---

## 🙏 Credits

- **[bkcrack](https://github.com/kimci86/bkcrack)** — the C++ implementation of the Biham–Kocher attack that makes Mode 2 possible
- **[Rich](https://github.com/Textualize/rich)** — beautiful terminal UI
- **[pyzipper](https://github.com/danifus/pyzipper)** — AES-ZIP support in Python
- **[Biham & Kocher, 1993](https://www.cs.technion.ac.il/users/wwwb/cgi-bin/tr-get.cgi/1993/CS/CS0884.pdf)** — *A Known Plaintext Attack on the PKZIP Stream Cipher*

---

## 📜 License

**GNU Affero General Public License v3.0 (AGPL-3.0-or-later)**

```
Copyright (C) 2025 DEDSEC <https://github.com/Unknownx007>
```

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

**You must:**

- 📌 Keep the copyright notice (`Copyright (C) 2025 DEDSEC`)
- 📌 Credit the original author in any redistribution
- 📌 Share your source if you distribute or offer this as a network service
- 📌 License your fork under AGPLv3

Full text: [LICENSE](LICENSE) · [gnu.org/licenses/agpl-3.0](https://www.gnu.org/licenses/agpl-3.0.html)

---

## 👤 Author

**DEDSEC**

- GitHub: [@Unknownx007](https://github.com/Unknownx007)
- Project: [github.com/Unknownx007/zip-kpa](https://github.com/Unknownx007/zip-kpa)

---

<div align="center">

**⭐ Star this repo if you find it useful ⭐**

*"Known plaintext is the universe telling you to trust no one."*

</div>
