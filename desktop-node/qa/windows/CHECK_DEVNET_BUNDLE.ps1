# CHECK_DEVNET_BUNDLE.ps1 - validate the NON-PRODUCTION devnet bootstrap bundle.
# Read-only. Confirms manifest + genesis (chainId 469469 / QBFT) + loopback config + lab
# validator key are present and consistent, and that the per-file sha256sums match.
# Does NOT start a node. Bundle keys are LAB keys (never user wallet / production keys).
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $here "_qa_lib.ps1")
$pkg = Get-QaPackageRoot $here
$py  = Get-QaPython $pkg
$checks = @()

Write-Host "ACAP QA - devnet bundle validation" -ForegroundColor Cyan

$bundle = Invoke-QaPython $py $pkg "acap_node_manager.py" @("bundle")
if ($null -eq $bundle) {
    $checks += New-QaCheck "bundle_probe" "Devnet bundle validator" "FAIL" "could not run acap_node_manager.py bundle" `
        "Ensure Python + runtime/devnet/ are present (full ZIP)."
} else {
    $checks += New-QaCheck "bundle_present" "Bundle present" ($(if($bundle.present){"PASS"}else{"FAIL"})) `
        ([string]$bundle.path) "Re-extract the full ZIP (runtime/devnet/ must exist)."
    $checks += New-QaCheck "bundle_valid" "Bundle valid (manifest/genesis/loopback/key)" ($(if($bundle.valid){"PASS"}else{"FAIL"})) `
        ($(if($bundle.valid){"all checks passed"}else{($bundle.errors -join "; ")})) `
        "Re-extract the ZIP; do not edit runtime/devnet/ files."
    $checks += New-QaCheck "bundle_chain" "Chain id 469469" ($(if($bundle.chain_id -eq 469469){"PASS"}else{"FAIL"})) `
        ("chain_id=" + $bundle.chain_id) ""
    $checks += New-QaCheck "bundle_loopback" "Loopback-only RPC binding" ($(if($bundle.loopback_only){"PASS"}else{"FAIL"})) `
        ("loopback_only=" + $bundle.loopback_only) "config.toml must bind RPC/host-allowlist to 127.0.0.1 only."
    $checks += New-QaCheck "bundle_p2p" "P2P loopback-only (disabled or 127.0.0.1)" ($(if($bundle.p2p_loopback_only){"PASS"}else{"FAIL"})) `
        ("p2p_exposure=" + $bundle.p2p_exposure) "config.toml must set p2p-enabled=false or p2p-interface=127.0.0.1 (p2p-host alone leaves port 30303 open on all interfaces)."
    $checks += New-QaCheck "bundle_nonprod" "Marked NON-PRODUCTION lab" ($(if($bundle.non_production){"PASS"}else{"FAIL"})) `
        "lab keys only - not user wallet keys, not the production chain" ""
}

# Independent integrity: verify runtime/devnet/sha256sums.txt against the actual files.
$devDir = Join-Path $pkg "runtime\devnet"
$sumsFile = Join-Path $devDir "sha256sums.txt"
if (Test-Path $sumsFile) {
    $bad = 0; $n = 0
    foreach ($line in Get-Content $sumsFile) {
        $l = $line.Trim()
        if (-not $l -or $l.StartsWith("#")) { continue }
        $parts = $l -split "\s+", 2
        if ($parts.Count -lt 2) { continue }
        $want = $parts[0].ToLower()
        $rel = $parts[1].TrimStart("*").Trim()
        $f = Join-Path $devDir ($rel -replace "/", "\")
        if (-not (Test-Path $f)) { $bad++; continue }
        $n++
        $got = (Get-FileHash $f -Algorithm SHA256).Hash.ToLower()
        if ($got -ne $want) { $bad++ }
    }
    $checks += New-QaCheck "bundle_sums" "Devnet file checksums (sha256sums.txt)" ($(if($bad -eq 0 -and $n -gt 0){"PASS"}else{"FAIL"})) `
        ("$n verified, $bad mismatched/missing") "Re-extract the ZIP if any checksum mismatches."
} else {
    $checks += New-QaCheck "bundle_sums" "Devnet file checksums (sha256sums.txt)" "WARN" "sha256sums.txt not found" ""
}

$checks | ForEach-Object { Write-QaCheck $_ }
[pscustomobject]@{ name = "devnet_bundle"; checks = $checks }
