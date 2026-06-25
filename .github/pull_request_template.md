<!--
Thanks for contributing to Active Capacity Network (preview).
Do NOT include secrets, private keys, .env, credentials, or production config.
-->

## Summary

What does this PR change and why?

## Area

- [ ] desktop-node
- [ ] installers/windows
- [ ] devnet
- [ ] docs
- [ ] scripts / CI
- [ ] tokenomics

## Safety checklist

- [ ] No secrets, private keys, mnemonics, `.env`, credentials, or DB dumps added.
- [ ] No real validator key added (devnet ships only a `key.example` placeholder).
- [ ] No claim that mainnet / rewards / custody / bridge / payments / trading is live.
- [ ] No fake contract address; no Buy button / active-sale wording.
- [ ] Devnet stays loopback-only; no public RPC/P2P exposure introduced.
- [ ] Tokenomics numbers (if touched) match `tokenomics/acap_tokenomics.json`.
- [ ] Ran the local safety checks:
  ```bash
  python3 scripts/check_no_secrets.py
  python3 scripts/check_claims.py
  python3 scripts/verify_release.py
  ```

## Related issues

Fixes #
