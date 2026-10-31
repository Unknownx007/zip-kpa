#!/usr/bin/env bash
# ZIP-KPA installer — DEDSEC
# Auto-detects OS/arch, installs Python deps, downloads + verifies bkcrack.
set -e

PY="python3"
command -v $PY >/dev/null 2>&1 || PY="python"

BK_VERSION="1.8.1"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "==============================================="
echo "  ZIP-KPA installer  —  DEDSEC"
echo "==============================================="

# ---------- 1. Python deps ----------
echo "[*] Upgrading pip..."
$PY -m pip install --upgrade pip >/dev/null 2>&1 || true

echo "[*] Installing Python dependencies..."
$PY -m pip install -r requirements.txt
echo "[✓] Python deps installed."

# ---------- 2. bkcrack (optional, for Mode 2) ----------
if [ -x "$PROJECT_DIR/bkcrack" ] || [ -x "$PROJECT_DIR/bkcrack.exe" ] || command -v bkcrack >/dev/null 2>&1; then
    echo "[✓] bkcrack already present. Skipping download."
    echo ""
    echo "[✓] Setup complete. Run:  $PY run.py"
    exit 0
fi

echo ""
echo "[*] Downloading bkcrack v${BK_VERSION} (needed for Mode 2 — KPA)..."

OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
    Linux*)
        case "$ARCH" in
            x86_64|amd64)
                ASSET="bkcrack-${BK_VERSION}-Linux-x86_64.tar.gz"
                SHA256="45dc7d81adbaaad5c0aa2d8615ea920fd08b732fda1ea945504e0a3e8dc1d2ab"
                ;;
            aarch64|arm64)
                ASSET="bkcrack-${BK_VERSION}-Linux-aarch64.tar.gz"
                SHA256="b467cf681a5f3a4d69dbb4f9afd15955e4cbfe838100032fa7c5539fbddbacf7"
                ;;
            *)
                echo "[!] Unsupported Linux arch: $ARCH — skipping bkcrack."
                echo "    Download manually: https://github.com/kimci86/bkcrack/releases"
                exit 0
                ;;
        esac
        ;;
    Darwin*)
        case "$ARCH" in
            x86_64)
                ASSET="bkcrack-${BK_VERSION}-macOS-x86_64.tar.gz"
                SHA256="d25501fc4c6d18b3e19c5b69c7d6c1eb3a34f7ce094b120283c61161fa02734d"
                ;;
            arm64)
                ASSET="bkcrack-${BK_VERSION}-macOS-arm64.tar.gz"
                SHA256="14c58845a03e8cb5b9f40edfe00af249c2271b947ded091d11bc73a9c61f5069"
                ;;
            *)
                echo "[!] Unsupported macOS arch: $ARCH — skipping bkcrack."
                exit 0
                ;;
        esac
        ;;
    *)
        echo "[!] Unsupported OS: $OS (use install.bat on Windows)"
        exit 0
        ;;
esac

URL="https://github.com/kimci86/bkcrack/releases/download/v${BK_VERSION}/${ASSET}"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT
cd "$TMPDIR"

echo "    URL: $URL"
if command -v wget >/dev/null 2>&1; then
    wget -q "$URL" -O "$ASSET"
elif command -v curl >/dev/null 2>&1; then
    curl -fsSL "$URL" -o "$ASSET"
else
    echo "[!] Neither wget nor curl available. Skipping bkcrack."
    exit 0
fi

# Verify SHA256
if command -v sha256sum >/dev/null 2>&1; then
    ACTUAL=$(sha256sum "$ASSET" | awk '{print $1}')
elif command -v shasum >/dev/null 2>&1; then
    ACTUAL=$(shasum -a 256 "$ASSET" | awk '{print $1}')
else
    ACTUAL=""
fi
if [ -n "$ACTUAL" ] && [ "$ACTUAL" != "$SHA256" ]; then
    echo "[!] SHA256 mismatch — refusing to install."
    echo "    expected: $SHA256"
    echo "    actual:   $ACTUAL"
    exit 1
fi
[ -n "$ACTUAL" ] && echo "[✓] SHA256 verified."

# Extract (.tar.gz on Linux/macOS)
tar -xzf "$ASSET"

# Locate the binary wherever the tarball extracted it
BK_BIN="$(find . -maxdepth 3 -type f -name bkcrack 2>/dev/null | head -n1)"
if [ -z "$BK_BIN" ]; then
    echo "[!] Could not find bkcrack binary after extraction."
    exit 1
fi

cp "$BK_BIN" "$PROJECT_DIR/bkcrack"
chmod +x "$PROJECT_DIR/bkcrack"

cd "$PROJECT_DIR"
if ./bkcrack --version >/dev/null 2>&1; then
    echo "[✓] bkcrack installed: $(./bkcrack --version | head -n1)"
else
    echo "[!] bkcrack installed but failed to execute. Check your architecture."
fi

echo ""
echo "[✓] Setup complete. Run:  $PY run.py"
