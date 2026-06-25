# CHECK_WALLET.ps1 - local wallet self-test (deterministic test vectors only).
# Read-only. Runs acap_wallet.py selftest. NO real wallet is created, NO password is asked,
# NO private key / seed / mnemonic is ever printed.
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $here "_qa_lib.ps1")
$pkg = Get-QaPackageRoot $here
$py  = Get-QaPython $pkg
$checks = @()

Write-Host "ACAP QA - wallet self-test" -ForegroundColor Cyan

try {
    $out = & $py (Join-Path $pkg "acap_wallet.py") selftest 2>&1 | Out-String
    if ($out -match "SELFTEST OK") {
        $checks += New-QaCheck "wallet_selftest" "ACAP wallet crypto self-test" "PASS" "scrypt + HMAC encrypt-then-MAC vectors OK"
    } else {
        $checks += New-QaCheck "wallet_selftest" "ACAP wallet crypto self-test" "FAIL" "selftest did not report OK" `
            "Re-extract the ZIP; ensure acap_wallet.py is intact."
    }
} catch {
    $checks += New-QaCheck "wallet_selftest" "ACAP wallet crypto self-test" "FAIL" ("error: " + $_.Exception.Message) `
        "Ensure Python (bundled runtime/python or system) is available."
}

$checks | ForEach-Object { Write-QaCheck $_ }
[pscustomobject]@{ name = "wallet"; checks = $checks }
