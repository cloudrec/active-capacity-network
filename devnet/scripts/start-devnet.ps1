# NON-PRODUCTION LAB devnet bundle helper (reference). The package-level
# START_LOCAL_DEVNET.ps1 drives the validated plan; this documents the raw besu call.
# RPC binds 127.0.0.1 only. No mainnet, no rewards, no public RPC.
# besu --data-path=$env:USERPROFILE\.acap-devnet --genesis-file=.\genesis.json `
#      --node-private-key-file=.\validators\validator-1\key --config-file=.\config.toml
