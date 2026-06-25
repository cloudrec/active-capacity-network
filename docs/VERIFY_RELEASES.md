# Verify Releases

> Always verify a download's **SHA-256** before running it. The installer also
> verifies hashes automatically and refuses non-HTTPS sources.

## Why

This project ships scripts and (eventually) binaries that run on your machine.
Verifying the checksum ensures the file was not tampered with in transit.

## Verify a file

**Windows (PowerShell):**

```powershell
Get-FileHash .\active-capacity-node-windows.zip -Algorithm SHA256
```

**Linux/macOS:**

```bash
sha256sum active-capacity-node-windows.zip
# or
shasum -a 256 active-capacity-node-windows.zip
```

Compare the printed hash against the **published** checksum for that release
(release notes, the `*.sha256` sidecar, or the package `MANIFEST.json` /
`sha256sums.txt`). They must match **exactly** (case-insensitive). If they differ,
**do not run the file** — re-download from the official source and report it.

## Verify the devnet bundle

`devnet/manifest.json` and `devnet/sha256sums.txt` (when present) list per-file
hashes for the devnet materials.

## Automated check

`scripts/verify_release.py` validates the tokenomics JSON and scans the package for
the safety invariants (no secrets, no unsafe claims, correct token parameters). Run:

```bash
python3 scripts/verify_release.py
```

A non-zero exit means a check failed — see its output.

## Installer guarantees

The Windows installer (`installers/windows/`):

- Refuses any non-`https://` download URL.
- Computes and compares SHA-256 for every archive before extracting/running it.
- Aborts on mismatch without starting anything partial.
