# CHECK_BESU_WALLET.ps1 - Besu/secp256k1 wallet self-test + keccak self-test.
# Read-only. Runs deterministic canonical vectors only. NO real account is created, NO
# password is asked, NO private key is ever printed. Devnet/testnet identity only.
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $here "_qa_lib.ps1")
$pkg = Get-QaPackageRoot $here
$py  = Get-QaPython $pkg
$checks = @()

Write-Host "ACAP QA - Besu wallet self-test" -ForegroundColor Cyan

try {
    $kec = & $py (Join-Path $pkg "acap_keccak.py") 2>&1 | Out-String
    if ($kec -match "KECCAK SELFTEST OK") {
        $checks += New-QaCheck "keccak_selftest" "Keccak-256 self-test" "PASS" "known-answer vectors OK"
    } else {
        $checks += New-QaCheck "keccak_selftest" "Keccak-256 self-test" "FAIL" "selftest did not report OK" `
            "Re-extract the ZIP; ensure acap_keccak.py is intact."
    }
} catch {
    $checks += New-QaCheck "keccak_selftest" "Keccak-256 self-test" "FAIL" ("error: " + $_.Exception.Message) ""
}

try {
    $bes = & $py (Join-Path $pkg "acap_besu_wallet.py") selftest 2>&1 | Out-String
    if ($bes -match "BESU WALLET SELFTEST OK") {
        $checks += New-QaCheck "besu_selftest" "Besu secp256k1 / EIP-55 self-test" "PASS" "canonical priv=1/2/3 address vectors OK"
    } else {
        $checks += New-QaCheck "besu_selftest" "Besu secp256k1 / EIP-55 self-test" "FAIL" "selftest did not report OK" `
            "Re-extract the ZIP; ensure acap_besu_wallet.py is intact."
    }
} catch {
    $checks += New-QaCheck "besu_selftest" "Besu secp256k1 / EIP-55 self-test" "FAIL" ("error: " + $_.Exception.Message) ""
}

$checks | ForEach-Object { Write-QaCheck $_ }
[pscustomobject]@{ name = "besu_wallet"; checks = $checks }
