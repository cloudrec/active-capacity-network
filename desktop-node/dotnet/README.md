# ACAP.Node — .NET Windows launcher (source)

This is the **source** of `ACAP.Node.exe`, the native Windows launcher for the ACAP
Desktop Node. The released `.exe` and embedded Python runtime are **build
artifacts** and are intentionally **not** committed to this repository — build them
yourself from source.

## What it does

`Program.cs` boots the stdlib-Python desktop node (`acap_desktop.py`) on
`127.0.0.1` only. It holds no keys, exposes no public RPC, and never touches
mainnet. It can embed and self-extract the Python node files so a copied-alone
`ACAP.Node.exe` is standalone-safe.

## Build

Requires the **.NET 8 SDK** (cross-compiles to Windows on Linux/macOS):

```bash
dotnet publish -c Release -r win-x64
```

## Note on embedded-resource paths

`AcapNode.csproj` references the node Python files and the local devnet bundle via
relative paths (`../../active-capacity-node-windows/...`) as laid out in the
project's internal monorepo. In this public repo the node sources live under
`desktop-node/` and the devnet under `devnet/`. Adjust the `<EmbeddedResource>`
`Include` paths to match your checkout before building, and supply your **own**
generated lab devnet key (the real key is not shipped — see
[../../docs/DEVNET_GUIDE.md](../../docs/DEVNET_GUIDE.md)).
