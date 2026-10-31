# Wordlists folder

Drop your wordlists here. Recommended:

- **rockyou.txt** — classic, 14M passwords
  https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt
- **SecLists** — https://github.com/danielmiessler/SecLists
- **CrackStation** — https://crackstation.net/crackstation-wordlist-password-cracking-dictionary.htm

Use small wordlists first to test the tool:

```bash
printf 'password123\nletmein\nadmin\nsecret\nzipkpa\n' > wordlists/test.txt
```
