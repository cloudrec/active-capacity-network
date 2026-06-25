# Troubleshooting — Windows Preview Node

**"Python is not recognized" / Python not found**
- Install Python 3.9+ from https://www.python.org/downloads/ and tick
  "Add python.exe to PATH". Reopen the command window. The `.bat` files also try `py`.

**SmartScreen / "Windows protected your PC"**
- Expected for an unsigned preview package. Choose "More info" → "Run anyway" only if you
  trust this source. You can read every script first; nothing is compiled or hidden.

**`CHECK_STATUS.bat` shows an error / no network**
- Confirm internet access and that https://capacity.469diamond.com opens in a browser.
- Corporate proxies/firewalls may block it. Try another network.

**Status shows `stale: true`**
- The site serves cached public data; a brief stale window is normal. Retry later. No action needed.

**Antivirus flags the .bat/.ps1**
- These are plain text. Review them. Whitelist the folder if your AV is over-cautious about
  scripts that make HTTPS calls.

**PowerShell "running scripts is disabled"**
- Run: `powershell -ExecutionPolicy Bypass -File node-health-check.ps1` (one-off, no system change).

**How do I stop it?**
- Press Ctrl+C in the node window, or close the window. No background service is installed.

Still stuck? Run `python acn_node.py diagnostics` and share the generated ZIP (no secrets in it).

**PowerShell ParserError ("Unexpected token", "Missing closing ')'", "value expression following '+'")**
- Fixed in package **0.5.2-psfix-preview** and later. Older scripts contained a non-ASCII dash that
  Windows PowerShell 5.1 mis-decoded on non-English (e.g. Russian) locales, breaking the parser.
- If you see this error, download **0.5.2-psfix-preview or later** and re-extract. All `.ps1`
  scripts are now pure ASCII. Verify the ZIP SHA-256 from `/api/node-packages/windows/checksum`.
